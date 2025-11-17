"""
Shelters Blueprint - 收容所管理 API
"""
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.shelter_service import ShelterService

shelters_bp = Blueprint('shelters', __name__, description='收容所管理 API')


@shelters_bp.route('', methods=['GET'])
def list_shelters():
    """
    獲取收容所列表 (公開端點)
    支援分頁和搜尋
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        verified_only = request.args.get('verified', 'false').lower() == 'true'
        
        result = ShelterService.list_shelters(
            page=page,
            per_page=per_page,
            search=search,
            verified_only=verified_only
        )
        return jsonify(result), 200
        
    except RuntimeError as e:
        abort(500, message=str(e))


@shelters_bp.route('', methods=['POST'])
@jwt_required()
def create_shelter():
    """
    創建收容所
    需要 SHELTER_MEMBER 或 ADMIN 角色
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            abort(400, message='缺少請求資料')
        
        result = ShelterService.create_shelter(current_user_id, data)
        return jsonify(result), 201
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@shelters_bp.route('/<int:shelter_id>', methods=['GET'])
def get_shelter(shelter_id):
    """取得收容所資訊 (公開端點)"""
    try:
        result = ShelterService.get_shelter(shelter_id)
        return jsonify(result), 200
        
    except ValueError as e:
        abort(404, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@shelters_bp.route('/<int:shelter_id>', methods=['PATCH'])
@jwt_required()
def update_shelter(shelter_id):
    """
    更新收容所資訊
    僅該收容所的主要負責人或管理員可更新
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            abort(400, message='缺少請求資料')
        
        result = ShelterService.update_shelter(current_user_id, shelter_id, data)
        return jsonify(result), 200
        
    except ValueError as e:
        if '收容所不存在' in str(e):
            abort(404, message=str(e))
        elif '無權限' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@shelters_bp.route('/<int:shelter_id>/verify', methods=['POST'])
@jwt_required()
def verify_shelter(shelter_id):
    """
    驗證收容所 (僅管理員)
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        verified = data.get('verified', True)
        
        result = ShelterService.verify_shelter(current_user_id, shelter_id, verified)
        return jsonify(result), 200
        
    except ValueError as e:
        if '收容所不存在' in str(e):
            abort(404, message=str(e))
        elif '僅管理員' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@shelters_bp.route('/<int:shelter_id>/animals/batch', methods=['POST'])
@jwt_required()
def batch_upload_animals(shelter_id):
    """
    批次匯入動物 (使用 Job Pattern)
    接收多個檔案:
    - animal_csv: 動物基本資訊 CSV (必填)
    - medical_csv: 醫療記錄 CSV (選填)
    - medical_proofs[]: 醫療證明文件 (選填)
    - photos[]: 動物照片 (選填)
    返回 202 Accepted + jobId
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # === 處理動物基本資訊 CSV (必填) ===
        if 'animal_csv' not in request.files:
            abort(400, message='缺少必填欄位: animal_csv')
        
        animal_csv = request.files['animal_csv']
        
        if animal_csv.filename == '':
            abort(400, message='未選擇動物基本資訊 CSV 檔案')
        
        # 驗證並讀取動物 CSV
        try:
            validated_files = ShelterService.validate_file_upload([animal_csv], 'csv', 10)
            animal_csv_content = animal_csv.read().decode('utf-8')
            animal_csv.seek(0)  # 重置文件指針
        except (UnicodeDecodeError, ValueError) as e:
            abort(400, message=str(e))
        
        # === 處理醫療記錄 CSV (選填) ===
        medical_csv_content = None
        medical_csv_filename = None
        if 'medical_csv' in request.files:
            medical_csv = request.files['medical_csv']
            
            if medical_csv.filename and medical_csv.filename != '':
                try:
                    ShelterService.validate_file_upload([medical_csv], 'csv', 10)
                    medical_csv_content = medical_csv.read().decode('utf-8')
                    medical_csv_filename = medical_csv.filename
                except (UnicodeDecodeError, ValueError) as e:
                    abort(400, message=str(e))
        
        # === 處理醫療證明文件和照片 (選填) ===
        medical_proof_data = []
        photos_data = []
        
        # 處理醫療證明
        if 'medical_proofs' in request.files:
            medical_proofs = request.files.getlist('medical_proofs')
            medical_proof_data = ShelterService._process_medical_proofs(medical_proofs, shelter_id)
        
        # 處理照片
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            photos_data = ShelterService._process_photos(photos, shelter_id)
        
        # 創建批量匯入任務
        result = ShelterService.create_batch_import_job(
            user_id=current_user_id,
            shelter_id=shelter_id,
            animal_csv_content=animal_csv_content,
            animal_csv_filename=animal_csv.filename,
            medical_csv_content=medical_csv_content,
            medical_csv_filename=medical_csv_filename,
            medical_proof_data=medical_proof_data,
            photos_data=photos_data
        )
        
        return jsonify(result), 202
        
    except ValueError as e:
        if '無權限' in str(e):
            abort(403, message=str(e))
        elif '收容所不存在' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@shelters_bp.route('/<int:shelter_id>/animals/batch/status', methods=['PATCH'])
@jwt_required()
def batch_update_animal_status(shelter_id):
    """
    批次更新動物狀態
    ---
    Request Body:
        animal_ids: List[int] - 動物 ID 列表
        action: str - 操作類型 ('draft', 'submit', 'publish', 'retire')
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 解析請求
        data = request.get_json()
        if not data:
            abort(400, message='缺少請求資料')
        
        animal_ids = data.get('animal_ids', [])
        action = data.get('action', '').lower()
        
        result = ShelterService.batch_update_animal_status(
            user_id=current_user_id,
            shelter_id=shelter_id,
            animal_ids=animal_ids,
            action=action
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '無權限' in str(e):
            abort(403, message=str(e))
        elif '收容所不存在' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@shelters_bp.route('/<int:shelter_id>/animals', methods=['GET'])
@jwt_required()
def get_shelter_animals(shelter_id):
    """
    取得收容所的動物列表 (含草稿狀態，供管理用)
    ---
    Query Parameters:
        - status: 狀態篩選 (DRAFT, SUBMITTED, PUBLISHED, RETIRED)
        - species: 物種篩選 (CAT, DOG)
        - sex: 性別篩選 (MALE, FEMALE)
        - keyword: 關鍵字搜尋
        - min_age, max_age: 年齡範圍
        - vaccinated: 是否接種疫苗 ('true'/'false')
        - page: 頁碼 (預設 1)
        - per_page: 每頁筆數 (預設 20)
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 取得查詢參數
        filters = {
            'status': request.args.get('status'),
            'species': request.args.get('species'),
            'sex': request.args.get('sex'),
            'keyword': request.args.get('keyword') or request.args.get('q'),
            'min_age': request.args.get('min_age', type=int),
            'max_age': request.args.get('max_age', type=int),
            'vaccinated': request.args.get('vaccinated')
        }
        
        # 移除空值
        filters = {k: v for k, v in filters.items() if v is not None}
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        result = ShelterService.get_shelter_animals(
            user_id=current_user_id,
            shelter_id=shelter_id,
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '無權限' in str(e):
            abort(403, message=str(e))
        elif '收容所不存在' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@shelters_bp.route('/<int:shelter_id>/animals/batch', methods=['POST'])
@jwt_required()
def batch_upload_animals(shelter_id):
    """
    批次匯入動物 (使用 Job Pattern)
    接收多個檔案:
    - animal_csv: 動物基本資訊 CSV (必填)
    - medical_csv: 醫療記錄 CSV (選填)
    - medical_proofs[]: 醫療證明文件 (選填,檔名格式: {animal_code}_{record_sequence}.pdf)
    - photos[]: 動物照片 (選填,檔名格式: {animal_code}_{order}.jpg)
    返回 202 Accepted + jobId
    """
    current_user_id = int(get_jwt_identity())
    
    shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
    if not shelter:
        abort(404, message='收容所不存在')
    
    # 檢查權限
    if not check_shelter_member_or_admin(current_user_id, shelter_id):
        abort(403, message='無權限執行批次匯入')
    
    # === 處理動物基本資訊 CSV (必填) ===
    if 'animal_csv' not in request.files:
        abort(400, message='缺少必填欄位: animal_csv')
    
    animal_csv = request.files['animal_csv']
    
    if animal_csv.filename == '':
        abort(400, message='未選擇動物基本資訊 CSV 檔案')
    
    # 驗證檔案類型
    if not animal_csv.filename.lower().endswith('.csv'):
        abort(400, message='動物基本資訊檔案必須為 CSV 格式')
    
    # 驗證檔案大小 (最大 10MB)
    animal_csv.seek(0, 2)
    file_size = animal_csv.tell()
    animal_csv.seek(0)
    
    if file_size > 10 * 1024 * 1024:
        abort(400, message='動物基本資訊 CSV 檔案不能超過 10MB')
    
    # 讀取動物 CSV 內容
    try:
        animal_csv_content = animal_csv.read().decode('utf-8')
    except UnicodeDecodeError:
        abort(400, message='動物基本資訊 CSV 編碼錯誤,請使用 UTF-8 編碼')
    
    # 驗證 CSV 格式
    import csv
    import io
    try:
        csv_reader = csv.DictReader(io.StringIO(animal_csv_content))
        first_row = next(csv_reader, None)
        if not first_row:
            abort(400, message='動物基本資訊 CSV 檔案為空')
    except Exception as e:
        abort(400, message=f'動物基本資訊 CSV 格式錯誤: {str(e)}')
    
    # === 處理醫療記錄 CSV (選填) ===
    medical_csv_content = None
    if 'medical_csv' in request.files:
        medical_csv = request.files['medical_csv']
        
        if medical_csv.filename and medical_csv.filename != '':
            # 驗證檔案類型
            if not medical_csv.filename.lower().endswith('.csv'):
                abort(400, message='醫療記錄檔案必須為 CSV 格式')
            
            # 驗證檔案大小
            medical_csv.seek(0, 2)
            file_size = medical_csv.tell()
            medical_csv.seek(0)
            
            if file_size > 10 * 1024 * 1024:
                abort(400, message='醫療記錄 CSV 檔案不能超過 10MB')
            
            # 讀取內容
            try:
                medical_csv_content = medical_csv.read().decode('utf-8')
            except UnicodeDecodeError:
                abort(400, message='醫療記錄 CSV 編碼錯誤,請使用 UTF-8 編碼')
    
    # === 處理醫療證明文件 (選填) ===
    medical_proof_data = []
    if 'medical_proofs' in request.files:
        medical_proofs = request.files.getlist('medical_proofs')
        
        # 導入 MinIO 客戶端
        from app.blueprints.uploads import minio_client, minio_available
        from config import Config
        import uuid as uuid_lib
        
        if not minio_available:
            abort(500, message='MinIO 服務不可用')
        
        for proof in medical_proofs:
            if proof.filename and proof.filename != '':
                # 驗證檔案類型 (PDF, DOC, DOCX, 圖片)
                allowed_types = [
                    'application/pdf',
                    'application/msword', 
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'image/jpeg', 'image/jpg', 'image/png'
                ]
                
                if not proof.content_type or proof.content_type not in allowed_types:
                    abort(400, message=f'醫療證明文件 {proof.filename} 格式不支援。支援格式: PDF, DOC, DOCX, JPG, PNG')
                
                # 驗證檔案大小 (最大 10MB per file)
                proof.seek(0, 2)
                proof_size = proof.tell()
                proof.seek(0)
                
                if proof_size > 10 * 1024 * 1024:
                    abort(400, message=f'醫療證明文件 {proof.filename} 超過 10MB 限制')
                
                # 驗證檔名格式: animal_code_record_sequence.ext
                import re
                filename_pattern = re.compile(r'^(.+?)_(\d+)\.(pdf|doc|docx|jpg|jpeg|png)$', re.IGNORECASE)
                match = filename_pattern.match(proof.filename)
                
                if not match:
                    abort(400, message=f'醫療證明文件 {proof.filename} 檔名格式錯誤。正確格式: 動物編號_記錄序號.副檔名 (例: 001_1.pdf)')
                
                animal_code = match.group(1)
                record_sequence = int(match.group(2))
                
                # 上傳到 MinIO
                try:
                    # 生成唯一的 object key
                    ext = proof.filename.split('.')[-1] if '.' in proof.filename else 'pdf'
                    object_key = f"medical-proofs/{shelter_id}/{uuid_lib.uuid4()}.{ext}"
                    
                    # 上傳到 MinIO
                    minio_client.put_object(
                        bucket_name=Config.MINIO_BUCKET,
                        object_name=object_key,
                        data=proof,
                        length=proof_size,
                        content_type=proof.content_type
                    )
                    
                    # 生成公開 URL
                    proof_url = f"http://{Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'}/{Config.MINIO_BUCKET}/{object_key}"
                    
                    medical_proof_data.append({
                        'filename': proof.filename,
                        'content_type': proof.content_type,
                        'storage_key': object_key,
                        'url': proof_url,
                        'size': proof_size,
                        'animal_code': animal_code,
                        'record_sequence': record_sequence
                    })
                except Exception as e:
                    db.session.rollback()
                    abort(400, message=f'上傳醫療證明文件 {proof.filename} 到 MinIO 失敗: {str(e)}')

    # === 處理照片 (選填) ===
    photos_data = []
    if 'photos' in request.files:
        photos = request.files.getlist('photos')
        
        # 導入 MinIO 客戶端
        from app.blueprints.uploads import minio_client, minio_available
        from config import Config
        import uuid as uuid_lib
        
        if not minio_available:
            abort(500, message='MinIO 服務不可用')
        
        for photo in photos:
            if photo.filename and photo.filename != '':
                # 驗證檔案類型
                if not photo.content_type or not photo.content_type.startswith('image/'):
                    abort(400, message=f'檔案 {photo.filename} 不是圖片格式')
                
                # 驗證檔案大小 (最大 5MB per photo)
                photo.seek(0, 2)
                photo_size = photo.tell()
                photo.seek(0)
                
                if photo_size > 5 * 1024 * 1024:
                    abort(400, message=f'照片 {photo.filename} 超過 5MB 限制')
                
                # 上傳照片到 MinIO
                try:
                    # 生成唯一的 object key
                    ext = photo.filename.split('.')[-1] if '.' in photo.filename else 'jpg'
                    object_key = f"batch-uploads/{shelter_id}/{uuid_lib.uuid4()}.{ext}"
                    
                    # 上傳到 MinIO
                    minio_client.put_object(
                        bucket_name=Config.MINIO_BUCKET,
                        object_name=object_key,
                        data=photo,
                        length=photo_size,
                        content_type=photo.content_type or 'image/jpeg'
                    )
                    
                    # 生成公開 URL
                    photo_url = f"http://{Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'}/{Config.MINIO_BUCKET}/{object_key}"
                    
                    photos_data.append({
                        'filename': photo.filename,
                        'content_type': photo.content_type,
                        'storage_key': object_key,
                        'url': photo_url,
                        'size': photo_size
                    })
                except Exception as e:
                    db.session.rollback()
                    abort(400, message=f'上傳照片 {photo.filename} 到 MinIO 失敗: {str(e)}')
    
    # 獲取醫療記錄檔名 (安全處理)
    medical_csv_filename = None
    if 'medical_csv' in request.files:
        medical_file = request.files['medical_csv']
        if medical_file and medical_file.filename:
            medical_csv_filename = medical_file.filename
    
    # 創建 Job 記錄
    try:
        job = Job(
            type=JobType.IMPORT_ANIMALS.value,
            status=JobStatus.PENDING,
            created_by=current_user_id,
            payload={
                'shelter_id': shelter_id,
                'animal_csv_content': animal_csv_content,
                'medical_csv_content': medical_csv_content,
                'medical_proofs': medical_proof_data,
                'photos': photos_data,
                'animal_csv_filename': animal_csv.filename,
                'medical_csv_filename': medical_csv_filename,
                'options': {}
            }
        )
        
        db.session.add(job)
        db.session.commit()
        
        # 將 job 加入 Celery 隊列
        from app.tasks import process_animal_batch_import
        process_animal_batch_import.delay(job.job_id)
        
        return jsonify({
            'message': '批次匯入已加入隊列',
            'job_id': job.job_id,
            'status': job.status.value,
            'files_received': {
                'animal_csv': animal_csv.filename,
                'medical_csv': medical_csv_filename,
                'medical_proofs_count': len(medical_proof_data),
                'photos_count': len(photos_data)
            }
        }), 202
        
    except Exception as e:
        db.session.rollback()
        abort(500, message=f'創建批次匯入任務失敗: {str(e)}')


@shelters_bp.route('/<int:shelter_id>/animals/batch/status', methods=['PATCH'])
@jwt_required()
def batch_update_animal_status(shelter_id):
    """
    批次更新動物狀態
    ---
    Request Body:
        animal_ids: List[int] - 動物 ID 列表
        action: str - 操作類型 ('draft', 'submit', 'publish', 'retire')
    """
    print(f"🔍 收到批次狀態更新請求 - Shelter ID: {shelter_id}")
    print(f"🔍 請求方法: {request.method}")
    print(f"🔍 請求資料: {request.get_json()}")
    print(f"🔍 Authorization 頭: {request.headers.get('Authorization', 'None')}")
    
    current_user_id = int(get_jwt_identity())
    
    shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
    if not shelter:
        abort(404, message='收容所不存在')
    
    # 檢查權限
    if not check_shelter_member_or_admin(current_user_id, shelter_id):
        abort(403, message='無權限執行批次操作')
    
    # 解析請求
    data = request.get_json()
    if not data:
        abort(400, message='缺少請求資料')
    
    animal_ids = data.get('animal_ids', [])
    action = data.get('action', '').lower()
    
    if not animal_ids:
        abort(400, message='請選擇要處理的動物')
    
    if action not in ['draft', 'submit', 'publish', 'retire']:
        abort(400, message='無效的操作類型。支援: draft, submit, publish, retire')
    
    # 檢查動物是否屬於該收容所
    animals = Animal.query.filter(
        Animal.animal_id.in_(animal_ids),
        Animal.shelter_id == shelter_id,
        Animal.deleted_at == None
    ).all()
    
    if len(animals) != len(animal_ids):
        found_ids = [a.animal_id for a in animals]
        missing_ids = [aid for aid in animal_ids if aid not in found_ids]
        abort(400, message=f'以下動物不存在或不屬於該收容所: {missing_ids}')
    
    # 執行批次狀態更新
    try:
        from app.services.animal_service import AnimalService
        from app.services.notification_service import NotificationService
        
        # 將 action 轉換為對應的狀態
        action_to_status = {
            'draft': 'DRAFT',
            'submit': 'SUBMITTED', 
            'publish': 'PUBLISHED',
            'retire': 'RETIRED'
        }
        
        new_status = action_to_status[action]
        
        # 調用 Service 層執行批次更新
        result = AnimalService.batch_update_animal_status(
            animal_ids=animal_ids,
            new_status=new_status,
            user_id=current_user_id,
            shelter_id=shelter_id
        )
        
        success_count = result['success_count']
        failed_count = result['failed_count'] 
        errors = result['errors']
        
        # 計算狀態中文名稱
        action_names = {
            'draft': '草稿',
            'submit': '提交審核',
            'publish': '發布',
            'retire': '下架'
        }
        action_name = action_names.get(action, action)
        
        # 創建通知
        NotificationService.create(
            recipient_id=current_user_id,
            type='system_notification',
            payload={
                'title': f'批次{action_name}完成',
                'message': f'成功處理 {success_count} 隻動物，失敗 {failed_count} 隻動物',
                'priority': 'NORMAL'
            }
        )
        
        return jsonify({
            'message': f'批次{action_name}完成',
            'success_count': success_count,
            'failed_count': failed_count,
            'total_count': len(animal_ids),
            'errors': errors[:10]  # 只返回前10個錯誤
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'批次更新失敗: {str(e)}',
            'message': '請稍後再試或聯繫管理員'
        }), 500


@shelters_bp.route('/<int:shelter_id>/animals', methods=['GET'])
@jwt_required()
def get_shelter_animals(shelter_id):
    """
    取得收容所的動物列表 (含草稿狀態，供管理用)
    ---
    Query Parameters:
        - status: 狀態篩選 (DRAFT, SUBMITTED, PUBLISHED, RETIRED)
        - species: 物種篩選 (CAT, DOG)
        - page: 頁碼 (預設 1)
        - per_page: 每頁筆數 (預設 20)
    """
    current_user_id = int(get_jwt_identity())
    
    shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
    if not shelter:
        abort(404, message='收容所不存在')
    
    # 檢查權限
    if not check_shelter_member_or_admin(current_user_id, shelter_id):
        abort(403, message='無權限查看收容所動物')
    
    # 取得查詢參數 (新增 sex, min_age, max_age, vaccinated, keyword)
    status = request.args.get('status')
    species = request.args.get('species')
    sex = request.args.get('sex')
    keyword = request.args.get('keyword') or request.args.get('q')
    # 年齡以整數年為單位
    min_age = request.args.get('min_age', type=int)
    max_age = request.args.get('max_age', type=int)
    # vaccinated: 'true' or 'false' (optional)
    vaccinated = request.args.get('vaccinated')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # 建立查詢
    query = Animal.query.filter(
        Animal.shelter_id == shelter_id,
        Animal.deleted_at == None
    )
    
    # 套用篩選
    if status:
        try:
            status_enum = AnimalStatus[status.upper()]
            query = query.filter_by(status=status_enum)
        except KeyError:
            abort(400, message=f'無效的狀態: {status}')
    
    if species:
        try:
            species_enum = Species[species.upper()]
            query = query.filter_by(species=species_enum)
        except KeyError:
            abort(400, message=f'無效的物種: {species}')

    # 性別篩選
    if sex:
        try:
            sex_enum = Sex[sex.upper()]
            query = query.filter_by(sex=sex_enum)
        except KeyError:
            abort(400, message=f'無效的性別: {sex}')

    # 關鍵字搜尋 (在 name, breed, color 上模糊匹配)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            db.or_(
                Animal.name.ilike(kw),
                Animal.breed.ilike(kw),
                Animal.color.ilike(kw)
            )
        )

    # 年齡範圍 (以生日 dob 反推)
    if min_age is not None or max_age is not None:
        today = datetime.utcnow().date()
        if min_age is not None:
            # 年齡 >= min_age => dob <= today - min_age years
            try:
                cutoff_max = today.replace(year=today.year - min_age)
            except ValueError:
                # 跨閏年的簡單處理: 若發生錯誤，回退一天
                cutoff_max = today.replace(year=today.year - min_age)
            query = query.filter(Animal.dob != None).filter(Animal.dob <= cutoff_max)
        if max_age is not None:
            # 年齡 <= max_age => dob >= today - max_age years
            try:
                cutoff_min = today.replace(year=today.year - max_age)
            except ValueError:
                cutoff_min = today.replace(year=today.year - max_age)
            query = query.filter(Animal.dob != None).filter(Animal.dob >= cutoff_min)

    # 已接種疫苗篩選 (根據是否存在已驗證的 VACCINE 醫療記錄)
    if vaccinated is not None:
        vaccinated_bool = str(vaccinated).lower() == 'true'
        if vaccinated_bool:
            # 至少有一筆 record_type == VACCINE 且 verified == True
            query = query.filter(Animal.medical_records.any(
                db.and_(MedicalRecord.record_type == RecordType.VACCINE, MedicalRecord.verified == True)
            ))
        else:
            # 沒有任何已驗證的 VACCINE 記錄
            query = query.filter(~Animal.medical_records.any(
                db.and_(MedicalRecord.record_type == RecordType.VACCINE, MedicalRecord.verified == True)
            ))
    
    # 分頁
    pagination = query.order_by(Animal.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    animals = pagination.items
    
    # 載入圖片
    for animal in animals:
        animal.images = AnimalImage.query.filter_by(
            animal_id=animal.animal_id
        ).order_by(AnimalImage.order).all()
    
    return jsonify({
        'animals': [animal.to_dict(include_relations=True) for animal in animals],
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next
    }), 200
