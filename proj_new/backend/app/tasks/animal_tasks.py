"""
Animal-related Celery Tasks
"""
import csv
import io
from datetime import datetime
from typing import Dict, Any

from app.celery import celery
from app import db
from app.models import Job, JobStatus, Animal, AnimalStatus, Shelter, MedicalRecord, RecordType, AnimalImage


@celery.task(bind=True, max_retries=3)
def process_animal_batch_import(self, job_id: int) -> Dict[str, Any]:
    """
    批次匯入動物資料 (支援多檔案架構)
    
    檔案:
    - animal_csv: 動物基本資訊 (必填)
    - medical_csv: 醫療記錄 (選填,多筆)
    - photos: 動物照片 (選填,檔名格式: {animal_code}_{order}.jpg)
    
    Args:
        job_id: Job ID
        
    Returns:
        處理結果統計
    """
    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}
    
    # 更新狀態為執行中
    job.status = JobStatus.RUNNING
    job.started_at = datetime.utcnow()
    db.session.commit()
    
    try:
        # 從 payload 取得參數
        shelter_id = job.payload.get('shelter_id')
        animal_csv_content = job.payload.get('animal_csv_content')
        medical_csv_content = job.payload.get('medical_csv_content')
        medical_proof_data = job.payload.get('medical_proofs', [])
        photos_data = job.payload.get('photos', [])
        options = job.payload.get('options', {})
        
        # 驗證必要參數
        if not shelter_id:
            raise ValueError('Missing shelter_id in job payload')
        
        if not animal_csv_content:
            raise ValueError('Missing animal_csv_content in job payload')
        
        # 驗證 shelter 存在
        shelter = Shelter.query.get(shelter_id)
        if not shelter:
            raise ValueError(f'Shelter {shelter_id} not found')
        
        # 統計
        stats = {
            'total_animals': 0,
            'success_animals': 0,
            'failed_animals': 0,
            'total_medical_records': 0,
            'success_medical_records': 0,
            'total_medical_proofs': 0,
            'success_medical_proofs': 0,
            'total_photos': 0,
            'success_photos': 0,
            'errors': []
        }
        
        # === 第一階段: 解析動物 CSV 並建立 animal_code → animal_id 映射 ===
        animal_code_map = {}  # {animal_code: animal_id}
        animal_code_numeric_map = {}  # {numeric_code: animal_id} for photo matching
        
        try:
            csv_reader = csv.DictReader(io.StringIO(animal_csv_content))
            headers = csv_reader.fieldnames
            
            # 驗證 CSV 標題
            required_headers = ['animal_code', 'name', 'species', 'breed', 'sex', 'dob', 'color', 'description']
            if not headers:
                raise ValueError('CSV file has no headers')
            
            missing_headers = [h for h in required_headers if h not in headers]
            if missing_headers:
                raise ValueError(f'CSV missing required headers: {", ".join(missing_headers)}')
                
        except Exception as e:
            raise ValueError(f'Invalid CSV format: {str(e)}')
        
        # === 預驗證照片格式（在創建任何動物之前） ===
        if photos_data:
            import re
            
            # 解析檔名格式: {animal_code}_{order}.{ext}
            filename_pattern = re.compile(r'^(.+?)_(\d+)\.[a-zA-Z]+$')
            
            # 首先收集所有動物代碼
            csv_reader_for_codes = csv.DictReader(io.StringIO(animal_csv_content))
            expected_animal_codes = []
            for row in csv_reader_for_codes:
                animal_code = row.get('animal_code', '').strip()
                if animal_code:
                    expected_animal_codes.append(animal_code)
            
            # 預驗證所有照片檔名
            photo_validation_errors = []
            for photo in photos_data:
                filename = photo.get('filename', '')
                match = filename_pattern.match(filename)
                
                if not match:
                    photo_validation_errors.append({
                        'file': 'photo',
                        'filename': filename,
                        'error': f'照片檔名格式錯誤: {filename}. 正確格式應為: {{動物代碼}}_{{序號}}.{{副檔名}}'
                    })
                    continue
                
                animal_code = match.group(1)
                
                # 檢查 animal_code 是否在 CSV 中
                found = False
                
                # 1. 直接匹配
                if animal_code in expected_animal_codes:
                    found = True
                # 2. 數字匹配（處理 "1" vs "001" 情況）
                else:
                    try:
                        numeric_code = int(animal_code)
                        for expected_code in expected_animal_codes:
                            try:
                                if int(expected_code) == numeric_code:
                                    found = True
                                    break
                            except ValueError:
                                continue
                    except ValueError:
                        pass
                
                if not found:
                    photo_validation_errors.append({
                        'file': 'photo',
                        'filename': filename,
                        'error': f'找不到動物代碼: {animal_code}. 可用代碼: {expected_animal_codes[:5]}'
                    })
            
            # 如果有照片格式錯誤，直接失敗
            if photo_validation_errors:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.utcnow()
                job.result_summary = {
                    'overall_result': 'failed',
                    'result_message': f'照片格式驗證失敗：{len(photo_validation_errors)} 個錯誤，匯入已取消',
                    'has_errors': True,
                    'animals': {
                        'total': len(expected_animal_codes),
                        'success': 0,  # 因為預驗證失敗，沒有動物被匯入
                        'failed': len(expected_animal_codes)
                    },
                    'photos': {
                        'total': len(photos_data),
                        'success': 0
                    },
                    'error_samples': photo_validation_errors[:10]  # 最多顯示10個錯誤
                }
                
                db.session.commit()
                return stats
        
        # 重新創建 reader (因為 fieldnames 消耗了迭代器)
        csv_reader = csv.DictReader(io.StringIO(animal_csv_content))
        
        for row_num, row in enumerate(csv_reader, start=2):
            stats['total_animals'] += 1
            
            # 錯誤太多時提前終止
            if stats['failed_animals'] > 100:
                raise ValueError(f'Too many errors ({stats["failed_animals"]}), aborting import')
            
            try:
                # 驗證必填欄位
                required_fields = ['animal_code', 'name', 'species', 'breed', 'sex', 'dob', 'color', 'description']
                missing_fields = [f for f in required_fields if not row.get(f) or not row[f].strip()]
                
                if missing_fields:
                    raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
                
                animal_code = row['animal_code'].strip()
                
                # 檢查重複的 animal_code
                if animal_code in animal_code_map:
                    raise ValueError(f'Duplicate animal_code: {animal_code}')
                
                # 驗證 species 值
                species = row['species'].strip().upper()
                if species not in ['CAT', 'DOG']:
                    raise ValueError(f'Invalid species: {species}. Must be CAT or DOG')
                
                # 驗證 sex 值
                sex = row['sex'].strip().upper()
                if sex not in ['MALE', 'FEMALE', 'UNKNOWN']:
                    raise ValueError(f'Invalid sex: {sex}. Must be MALE, FEMALE, or UNKNOWN')
                
                # 處理出生日期 - 支援多種格式
                try:
                    from datetime import datetime as dt
                    dob_str = row['dob'].strip()
                    # 嘗試多種日期格式
                    date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
                    dob = None
                    for fmt in date_formats:
                        try:
                            dob = dt.strptime(dob_str, fmt).date()
                            break
                        except ValueError:
                            continue
                    
                    if dob is None:
                        raise ValueError(f'Invalid date format for dob: {row["dob"]}. Supported formats: YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY, DD-MM-YYYY')
                except Exception as e:
                    if 'Invalid date format' not in str(e):
                        raise ValueError(f'Error parsing date {row["dob"]}: {str(e)}')
                
                # 建立動物物件
                animal = Animal(
                    shelter_id=shelter_id,
                    name=row['name'].strip(),
                    species=species,
                    breed=row['breed'].strip(),
                    sex=sex,
                    color=row['color'].strip(),
                    dob=dob,
                    description=row['description'].strip(),
                    status=AnimalStatus.DRAFT,
                    owner_id=None,  # 收容所動物不設定 owner_id
                    created_by=job.created_by,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                # 添加並 flush 以獲取 animal_id
                db.session.add(animal)
                db.session.flush()
                
                # 記錄映射
                animal_code_map[animal_code] = animal.animal_id
                
                # 為照片匹配建立數字版本的映射
                try:
                    numeric_code = str(int(animal_code))  # "001" -> "1"
                    animal_code_numeric_map[numeric_code] = animal.animal_id
                except ValueError:
                    # 如果 animal_code 不是數字，使用原始值
                    animal_code_numeric_map[animal_code] = animal.animal_id
                
                stats['success_animals'] += 1
                
            except Exception as e:
                stats['failed_animals'] += 1
                stats['errors'].append({
                    'row': row_num,
                    'file': 'animal_csv',
                    'data': row,
                    'error': str(e)
                })
        
        # Commit 動物資料
        db.session.commit()
        
        # === 第二階段: 解析醫療記錄 CSV (選填) ===
        medical_record_map = {}  # {(animal_code, record_sequence): medical_record_id}
        
        if medical_csv_content:
            medical_csv_reader = csv.DictReader(io.StringIO(medical_csv_content))
            
            for row_num, row in enumerate(medical_csv_reader, start=2):
                stats['total_medical_records'] += 1
                
                try:
                    # 驗證必填欄位
                    required_fields = ['animal_code', 'record_type', 'date']
                    missing_fields = [f for f in required_fields if not row.get(f) or not row[f].strip()]
                    
                    if missing_fields:
                        raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
                    
                    animal_code = row['animal_code'].strip()
                    
                    # 檢查 animal_code 是否存在
                    if animal_code not in animal_code_map:
                        raise ValueError(f'Unknown animal_code: {animal_code}. Animal not found in animal_csv')
                    
                    animal_id = animal_code_map[animal_code]
                    
                    # 驗證 record_type
                    record_type = row['record_type'].strip().upper()
                    if record_type not in ['TREATMENT', 'CHECKUP', 'VACCINE', 'SURGERY', 'OTHER']:
                        raise ValueError(f'Invalid record_type: {record_type}')
                    
                    # 取得 record_sequence (選填,預設為1)
                    record_sequence = 1
                    if 'record_sequence' in row and row['record_sequence'].strip():
                        try:
                            record_sequence = int(row['record_sequence'].strip())
                        except ValueError:
                            raise ValueError(f'Invalid record_sequence: {row["record_sequence"]}. Must be a number')
                    
                    # 處理醫療日期 - 支援多種格式
                    try:
                        from datetime import datetime as dt
                        medical_date_str = row['date'].strip()
                        # 嘗試多種日期格式 (與動物出生日期格式一致)
                        date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
                        medical_date = None
                        for fmt in date_formats:
                            try:
                                medical_date = dt.strptime(medical_date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                        
                        if medical_date is None:
                            raise ValueError(f'Invalid date format for medical record: {row["date"]}. Supported formats: YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY, DD-MM-YYYY')
                    except Exception as e:
                        if 'Invalid date format' not in str(e):
                            raise ValueError(f'Error parsing medical date {row["date"]}: {str(e)}')
                        raise
                    
                    # 創建醫療記錄
                    medical_record = MedicalRecord(
                        animal_id=animal_id,
                        record_type=RecordType[record_type],
                        date=medical_date,
                        provider=row.get('provider', '').strip() or None,
                        details=row.get('details', '').strip() or None,
                        verified=False,
                        created_by=job.created_by,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.session.add(medical_record)
                    db.session.flush()  # 獲取 medical_record_id
                    
                    # 記錄醫療記錄映射 (用於證明文件關聯)
                    medical_record_map[(animal_code, record_sequence)] = medical_record.medical_record_id
                    
                    stats['success_medical_records'] += 1
                    
                except Exception as e:
                    stats['errors'].append({
                        'row': row_num,
                        'file': 'medical_csv',
                        'data': row,
                        'error': str(e)
                    })
            
            # Commit 醫療記錄
            db.session.commit()
        
        # === 第三階段: 處理醫療證明文件 (選填) ===
        if medical_proof_data:
            # 處理醫療證明文件
            for proof in medical_proof_data:
                stats['total_medical_proofs'] += 1
                
                try:
                    animal_code = proof['animal_code']
                    record_sequence = proof['record_sequence']
                    
                    # 檢查動物是否存在
                    if animal_code not in animal_code_map:
                        raise ValueError(f'動物編號 {animal_code} 不存在於動物基本資訊 CSV 中')
                    
                    animal_id = animal_code_map[animal_code]
                    
                    # 嘗試找到對應的醫療記錄
                    medical_record_id = medical_record_map.get((animal_code, record_sequence))
                    
                    # 創建醫療證明附件記錄
                    from app.models.others import Attachment
                    
                    attachment = Attachment(
                        owner_type='medical_record' if medical_record_id else 'animal',
                        owner_id=medical_record_id or animal_id,  # 關聯到醫療記錄或動物
                        filename=proof['filename'],
                        storage_key=proof['storage_key'],
                        url=proof['url'],
                        mime_type=proof['content_type'],
                        size=proof['size'],
                        meta_data={
                            'animal_code': animal_code,
                            'record_sequence': record_sequence,
                            'type': 'medical_proof'
                        }
                    )
                    
                    db.session.add(attachment)
                    stats['success_medical_proofs'] += 1
                    
                except Exception as e:
                    stats['errors'].append({
                        'file': 'medical_proof',
                        'filename': proof.get('filename', 'unknown'),
                        'error': str(e)
                    })
            
            # Commit 醫療證明附件
            db.session.commit()

        # === 第四階段: 處理照片 (選填) ===
        if photos_data:
            # 所有照片已通過預驗證，開始處理
            import re
            filename_pattern = re.compile(r'^(.+?)_(\d+)\.[a-zA-Z]+$')
            
            for photo in photos_data:
                stats['total_photos'] += 1
                
                try:
                    filename = photo['filename']
                    match = filename_pattern.match(filename)
                    animal_code = match.group(1)
                    order = int(match.group(2))
                    
                    # 找到對應的動物ID（已經預驗證，必定存在）
                    animal_id = None
                    if animal_code in animal_code_map:
                        animal_id = animal_code_map[animal_code]
                    elif animal_code in animal_code_numeric_map:
                        animal_id = animal_code_numeric_map[animal_code]
                    else:
                        # 嘗試零填充匹配
                        try:
                            numeric_code = int(animal_code)
                            for padding in [2, 3, 4]:
                                padded_code = str(numeric_code).zfill(padding)
                                if padded_code in animal_code_map:
                                    animal_id = animal_code_map[padded_code]
                                    break
                        except ValueError:
                            pass
                    
                    # 使用 MinIO URL 和 storage_key
                    image_url = photo['url']
                    storage_key = photo['storage_key']
                    
                    animal_image = AnimalImage(
                        animal_id=animal_id,
                        url=image_url,  # 正確的欄位名稱是 'url'
                        storage_key=storage_key,
                        order=order
                    )
                    
                    db.session.add(animal_image)
                    stats['success_photos'] += 1
                    
                except Exception as e:
                    stats['errors'].append({
                        'file': 'photo',
                        'filename': photo.get('filename', 'unknown'),
                        'error': str(e)
                    })
            
            # Commit 照片記錄
            db.session.commit()
        
        # 判斷任務整體結果狀態
        has_critical_errors = stats['failed_animals'] > 0  # 動物匯入失敗是關鍵錯誤
        has_minor_errors = (
            (stats['total_photos'] > 0 and stats['success_photos'] == 0) or  # 照片全部失敗
            (stats['total_medical_proofs'] > 0 and stats['success_medical_proofs'] == 0)  # 醫療證明全部失敗
        )
        has_partial_errors = (
            (stats['total_photos'] > stats['success_photos'] > 0) or  # 部分照片失敗
            (stats['total_medical_proofs'] > stats['success_medical_proofs'] > 0)  # 部分醫療證明失敗
        )
        
        # 決定任務狀態和結果信息
        if has_critical_errors:
            # 動物匯入失敗 - 標記為失敗
            job.status = JobStatus.FAILED
            overall_result = 'failed'
            result_message = f'動物匯入失敗：{stats["failed_animals"]}/{stats["total_animals"]} 失敗'
        elif has_minor_errors:
            # 所有附件匯入失敗 - 標記為失敗
            job.status = JobStatus.FAILED 
            overall_result = 'partial_failed'
            
            failed_types = []
            if stats['total_photos'] > 0 and stats['success_photos'] == 0:
                failed_types.append('照片')
            if stats['total_medical_proofs'] > 0 and stats['success_medical_proofs'] == 0:
                failed_types.append('醫療證明')
            
            result_message = f'{"/".join(failed_types)}匯入完全失敗'
        elif has_partial_errors:
            # 部分附件失敗 - 標記為成功但含警告
            job.status = JobStatus.SUCCEEDED
            overall_result = 'partial_success'
            
            partial_types = []
            if stats['total_photos'] > stats['success_photos'] > 0:
                partial_types.append(f'照片 {stats["success_photos"]}/{stats["total_photos"]}')
            if stats['total_medical_proofs'] > stats['success_medical_proofs'] > 0:
                partial_types.append(f'醫療證明 {stats["success_medical_proofs"]}/{stats["total_medical_proofs"]}')
            
            result_message = f'部分成功：{", ".join(partial_types)} 成功'
        else:
            # 完全成功
            job.status = JobStatus.SUCCEEDED
            overall_result = 'success'
            result_message = '匯入完全成功'
        
        job.completed_at = datetime.utcnow()
        job.result_summary = {
            'overall_result': overall_result,
            'result_message': result_message,
            'has_errors': len(stats['errors']) > 0,
            'animals': {
                'total': stats['total_animals'],
                'success': stats['success_animals'],
                'failed': stats['failed_animals']
            },
            'medical_records': {
                'total': stats['total_medical_records'],
                'success': stats['success_medical_records']
            },
            'medical_proofs': {
                'total': stats['total_medical_proofs'],
                'success': stats['success_medical_proofs']
            },
            'photos': {
                'total': stats['total_photos'],
                'success': stats['success_photos']
            },
            'error_samples': stats['errors'][:20]  # 保存前20個錯誤
        }
        db.session.commit()
        
        return stats
        
    except Exception as exc:
        # Rollback 所有變更
        db.session.rollback()
        
        # 更新 job 狀態為失敗
        try:
            job = Job.query.get(job_id)  # 重新查詢 job (因為已 rollback)
            if job:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.utcnow()
                job.result_summary = {
                    'error': str(exc),
                    'error_type': type(exc).__name__,
                    'traceback': __import__('traceback').format_exc()
                }
                db.session.commit()
        except Exception as update_error:
            print(f'Failed to update job status: {update_error}')
        
        # 重試機制
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        
        raise


@celery.task(bind=True, max_retries=3)
def process_animal_batch_export(self, job_id: int) -> Dict[str, Any]:
    """
    批次匯出動物資料
    
    Args:
        job_id: Job ID
        
    Returns:
        處理結果
    """
    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}
    
    job.status = JobStatus.RUNNING
    job.started_at = datetime.utcnow()
    db.session.commit()
    
    try:
        # 從 payload 取得參數
        shelter_id = job.payload.get('shelter_id')
        filters = job.payload.get('filters', {})
        
        # 查詢動物
        query = Animal.query.filter_by(shelter_id=shelter_id, is_active=True)
        
        # 套用篩選
        if filters.get('species'):
            query = query.filter_by(species=filters['species'])
        if filters.get('status'):
            query = query.filter_by(status=filters['status'])
        
        animals = query.all()
        
        # 產生 CSV
        output = io.StringIO()
        fieldnames = [
            'animal_id', 'name', 'species', 'breed', 'age', 'gender',
            'color', 'size', 'health_status', 'vaccination_status',
            'sterilization_status', 'status', 'created_at'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for animal in animals:
            writer.writerow({
                'animal_id': animal.animal_id,
                'name': animal.name,
                'species': animal.species,
                'breed': animal.breed,
                'age': animal.age,
                'gender': animal.gender,
                'color': animal.color or '',
                'size': animal.size or '',
                'health_status': animal.health_status,
                'vaccination_status': animal.vaccination_status or '',
                'sterilization_status': animal.sterilization_status or '',
                'status': animal.status.value,
                'created_at': animal.created_at.isoformat()
            })
        
        # 上傳到 MinIO
        csv_content = output.getvalue().encode('utf-8')
        filename = f"animals-export-{shelter_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        
        # TODO: 實作 MinIO 上傳
        # file_url = minio_service.upload_file(
        #     file_content=csv_content,
        #     filename=filename,
        #     content_type='text/csv'
        # )
        
        # 暫時返回 CSV 內容 (實際應上傳到 MinIO)
        file_url = f"temp://{filename}"  # 臨時 URL
        
        # 更新 job 狀態
        job.status = JobStatus.SUCCEEDED
        job.completed_at = datetime.utcnow()
        job.result_summary = {
            'total_count': len(animals),
            'file_url': file_url,
            'filename': filename
        }
        db.session.commit()
        
        return {
            'success': True,
            'file_url': file_url,
            'count': len(animals)
        }
        
    except Exception as exc:
        job.status = JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.result_summary = {
            'error': str(exc),
            'error_type': type(exc).__name__
        }
        db.session.commit()
        
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        
        raise
