"""
Shelter Service - 收容所相關業務邏輯
"""
import csv
import io
import re
import uuid as uuid_lib
from datetime import datetime, timedelta
from flask import current_app
from app import db
from app.models.shelter import Shelter
from app.models.user import User, UserRole
from app.models.others import Job, JobType, JobStatus
from app.models.animal import Animal, AnimalStatus, Species, AnimalImage, Sex
from app.models.medical_record import MedicalRecord, RecordType
from app.services.audit_service import AuditService
from sqlalchemy import or_


class ShelterService:
    """收容所業務邏輯服務"""

    @staticmethod
    def check_shelter_permission(user_id, shelter_id=None, require_admin=False):
        """
        檢查用戶對收容所的權限
        
        Args:
            user_id: 用戶ID
            shelter_id: 收容所ID（可選，創建新收容所時不需要）
            require_admin: 是否需要管理員權限
        
        Returns:
            User: 用戶對象
            
        Raises:
            ValueError: 無權限或用戶不存在
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用戶不存在')
        
        # 管理員有完全權限
        if user.role == UserRole.ADMIN:
            return user
            
        # 如果只要求管理員權限
        if require_admin:
            raise ValueError('僅管理員可執行此操作')
        
        # 收容所成員需要檢查關聯
        if user.role == UserRole.SHELTER_MEMBER:
            if shelter_id:
                # 檢查是否為該收容所的主要負責人或關聯成員
                shelter = Shelter.query.get(shelter_id)
                if shelter and (shelter.primary_account_user_id == user_id or user.primary_shelter_id == shelter_id):
                    return user
            else:
                # 創建新收容所時，只要是收容所成員即可
                return user
        
        raise ValueError('無權限執行此操作')

    @staticmethod
    def list_shelters(page=1, per_page=10, search='', verified_only=False):
        """
        獲取收容所列表
        
        Args:
            page: 頁碼
            per_page: 每頁數量
            search: 搜索關鍵字
            verified_only: 是否僅顯示已驗證收容所
        
        Returns:
            dict: 分頁收容所數據
        """
        try:
            # 驗證分頁參數
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 10
            
            # 構建查詢
            query = Shelter.query.filter_by(deleted_at=None)
            
            # 搜尋過濾
            if search:
                query = query.filter(
                    or_(
                        Shelter.name.ilike(f'%{search}%'),
                        Shelter.contact_email.ilike(f'%{search}%')
                    )
                )
            
            # 僅顯示已驗證收容所
            if verified_only:
                query = query.filter_by(verified=True)
            
            # 排序和分頁
            query = query.order_by(Shelter.created_at.desc())
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'shelters': [shelter.to_dict() for shelter in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
            
        except Exception as e:
            current_app.logger.error(f"List shelters error: {str(e)}")
            raise RuntimeError(f"獲取收容所列表失敗: {str(e)}")

    @staticmethod
    def create_shelter(user_id, data):
        """
        創建收容所
        
        Args:
            user_id: 創建者用戶ID
            data: 收容所資料
        
        Returns:
            dict: 創建結果
        """
        try:
            # 檢查權限
            ShelterService.check_shelter_permission(user_id)
            
            # 驗證必填欄位
            required_fields = ['name', 'contact_email', 'contact_phone', 'address']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f'缺少必填欄位: {field}')
            
            # 驗證 email 格式
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['contact_email']):
                raise ValueError('Email 格式不正確')
            
            # 驗證 address 結構
            if not isinstance(data['address'], dict):
                raise ValueError('地址必須為JSON對象')
            
            address_fields = ['street', 'city', 'county', 'postal_code']
            for field in address_fields:
                if field not in data['address']:
                    raise ValueError(f'地址缺少必填欄位: {field}')
            
            # 生成 slug (如果未提供)
            slug = data.get('slug')
            if slug:
                # 檢查 slug 唯一性
                if Shelter.query.filter_by(slug=slug).first():
                    raise ValueError('Slug 已存在')
            
            # 創建收容所
            shelter = Shelter(
                name=data['name'],
                slug=slug,
                contact_email=data['contact_email'],
                contact_phone=data['contact_phone'],
                address=data['address'],
                region=data.get('region'),  # 可選的地區欄位
                verified=False,  # 預設未驗證
                primary_account_user_id=user_id
            )
            
            db.session.add(shelter)
            db.session.commit()
            
            return {
                'message': '收容所創建成功',
                'shelter': shelter.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Create shelter error: {str(e)}")
            raise RuntimeError(f"創建收容所失敗: {str(e)}")

    @staticmethod
    def get_shelter(shelter_id):
        """
        獲取收容所資訊
        
        Args:
            shelter_id: 收容所ID
        
        Returns:
            dict: 收容所資料
        """
        try:
            shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
            
            if not shelter:
                raise ValueError('收容所不存在')
            
            return shelter.to_dict()
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Get shelter error: {str(e)}")
            raise RuntimeError(f"獲取收容所資訊失敗: {str(e)}")

    @staticmethod
    def update_shelter(user_id, shelter_id, data):
        """
        更新收容所資訊
        
        Args:
            user_id: 執行更新的用戶ID
            shelter_id: 收容所ID
            data: 更新資料
        
        Returns:
            dict: 更新結果
        """
        try:
            shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
            if not shelter:
                raise ValueError('收容所不存在')
            
            # 檢查權限
            ShelterService.check_shelter_permission(user_id, shelter_id)
            
            # 可更新的欄位
            allowed_fields = ['name', 'slug', 'contact_email', 'contact_phone', 'address', 'region']
            
            for field in allowed_fields:
                if field in data:
                    # 特殊驗證
                    if field == 'contact_email':
                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                        if not re.match(email_pattern, data['contact_email']):
                            raise ValueError('Email 格式不正確')
                    
                    if field == 'slug' and data['slug']:
                        # 檢查 slug 唯一性(排除自己)
                        existing = Shelter.query.filter(
                            Shelter.slug == data['slug'],
                            Shelter.shelter_id != shelter_id
                        ).first()
                        if existing:
                            raise ValueError('Slug 已存在')
                    
                    if field == 'address':
                        if not isinstance(data['address'], dict):
                            raise ValueError('地址必須為JSON對象')
                        address_fields = ['street', 'city', 'county', 'postal_code']
                        for addr_field in address_fields:
                            if addr_field not in data['address']:
                                raise ValueError(f'地址缺少必填欄位: {addr_field}')
                    
                    setattr(shelter, field, data[field])
            
            shelter.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'message': '收容所更新成功',
                'shelter': shelter.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update shelter error: {str(e)}")
            raise RuntimeError(f"更新收容所失敗: {str(e)}")

    @staticmethod
    def verify_shelter(admin_id, shelter_id, verified=True):
        """
        驗證收容所
        
        Args:
            admin_id: 管理員ID
            shelter_id: 收容所ID
            verified: 是否驗證
        
        Returns:
            dict: 驗證結果
        """
        try:
            # 檢查管理員權限
            ShelterService.check_shelter_permission(admin_id, require_admin=True)
            
            shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
            if not shelter:
                raise ValueError('收容所不存在')
            
            shelter.verified = verified
            shelter.updated_at = datetime.utcnow()
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='shelter.verify',
                actor_id=admin_id,
                target_type='shelter',
                target_id=shelter_id,
                before_state={'verified': not verified},
                after_state={'verified': verified},
                shelter_id=shelter_id
            )
            
            return {
                'message': f'收容所已{"驗證" if verified else "取消驗證"}',
                'shelter': shelter.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Verify shelter error: {str(e)}")
            raise RuntimeError(f"驗證收容所失敗: {str(e)}")

    @staticmethod
    def create_batch_import_job(user_id, shelter_id, animal_csv_content, animal_csv_filename, 
                              medical_csv_content=None, medical_csv_filename=None, 
                              medical_proof_data=None, photos_data=None):
        """
        創建批量匯入動物任務
        
        Args:
            user_id: 執行用戶ID
            shelter_id: 收容所ID
            animal_csv_content: 動物CSV內容
            animal_csv_filename: 動物CSV檔名
            medical_csv_content: 醫療記錄CSV內容
            medical_csv_filename: 醫療記錄CSV檔名
            medical_proof_data: 醫療證明文件數據
            photos_data: 照片數據
        
        Returns:
            dict: 任務創建結果
        """
        try:
            # 檢查權限
            ShelterService.check_shelter_permission(user_id, shelter_id)
            
            # 驗證 CSV 格式
            try:
                csv_reader = csv.DictReader(io.StringIO(animal_csv_content))
                first_row = next(csv_reader, None)
                if not first_row:
                    raise ValueError('動物基本資訊 CSV 檔案為空')
            except Exception as e:
                raise ValueError(f'動物基本資訊 CSV 格式錯誤: {str(e)}')
            
            # 創建 Job 記錄
            job = Job(
                type=JobType.IMPORT_ANIMALS.value,
                status=JobStatus.PENDING,
                created_by=user_id,
                payload={
                    'shelter_id': shelter_id,
                    'animal_csv_content': animal_csv_content,
                    'medical_csv_content': medical_csv_content,
                    'medical_proofs': medical_proof_data or [],
                    'photos': photos_data or [],
                    'animal_csv_filename': animal_csv_filename,
                    'medical_csv_filename': medical_csv_filename,
                    'options': {}
                }
            )
            
            db.session.add(job)
            db.session.commit()
            
            # 將 job 加入 Celery 隊列
            from app.tasks import process_animal_batch_import
            process_animal_batch_import.delay(job.job_id)
            
            return {
                'message': '批次匯入已加入隊列',
                'job_id': job.job_id,
                'status': job.status.value,
                'files_received': {
                    'animal_csv': animal_csv_filename,
                    'medical_csv': medical_csv_filename,
                    'medical_proofs_count': len(medical_proof_data or []),
                    'photos_count': len(photos_data or [])
                }
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Create batch import job error: {str(e)}")
            raise RuntimeError(f"創建批次匯入任務失敗: {str(e)}")

    @staticmethod
    def batch_update_animal_status(user_id, shelter_id, animal_ids, action):
        """
        批次更新動物狀態
        
        Args:
            user_id: 執行用戶ID
            shelter_id: 收容所ID
            animal_ids: 動物ID列表
            action: 操作類型
        
        Returns:
            dict: 批次更新結果
        """
        try:
            # 檢查權限
            ShelterService.check_shelter_permission(user_id, shelter_id)
            
            if not animal_ids:
                raise ValueError('請選擇要處理的動物')
            
            if action not in ['draft', 'submit', 'publish', 'retire']:
                raise ValueError('無效的操作類型。支援: draft, submit, publish, retire')
            
            # 檢查動物是否屬於該收容所
            animals = Animal.query.filter(
                Animal.animal_id.in_(animal_ids),
                Animal.shelter_id == shelter_id,
                Animal.deleted_at == None
            ).all()
            
            if len(animals) != len(animal_ids):
                found_ids = [a.animal_id for a in animals]
                missing_ids = [aid for aid in animal_ids if aid not in found_ids]
                raise ValueError(f'以下動物不存在或不屬於該收容所: {missing_ids}')
            
            # 將 action 轉換為對應的狀態
            action_to_status = {
                'draft': 'DRAFT',
                'submit': 'SUBMITTED', 
                'publish': 'PUBLISHED',
                'retire': 'RETIRED'
            }
            
            new_status = action_to_status[action]
            
            # 調用 Service 層執行批次更新
            from app.services.animal_service import AnimalService
            from app.services.notification_service import NotificationService
            
            result = AnimalService.batch_update_animal_status(
                animal_ids=animal_ids,
                new_status=new_status,
                user_id=user_id,
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
                recipient_id=user_id,
                type='system_notification',
                payload={
                    'title': f'批次{action_name}完成',
                    'message': f'成功處理 {success_count} 隻動物，失敗 {failed_count} 隻動物',
                    'priority': 'NORMAL'
                }
            )
            
            return {
                'message': f'批次{action_name}完成',
                'success_count': success_count,
                'failed_count': failed_count,
                'total_count': len(animal_ids),
                'errors': errors[:10]  # 只返回前10個錯誤
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Batch update animal status error: {str(e)}")
            raise RuntimeError(f"批次更新失敗: {str(e)}")

    @staticmethod
    def get_shelter_animals(user_id, shelter_id, filters=None, page=1, per_page=20):
        """
        取得收容所的動物列表
        
        Args:
            user_id: 查詢用戶ID
            shelter_id: 收容所ID
            filters: 篩選條件字典
            page: 頁碼
            per_page: 每頁數量
        
        Returns:
            dict: 分頁動物數據
        """
        try:
            # 檢查權限
            ShelterService.check_shelter_permission(user_id, shelter_id)
            
            shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
            if not shelter:
                raise ValueError('收容所不存在')
            
            filters = filters or {}
            per_page = min(per_page, 100)  # 限制最大每頁數量
            
            # 建立查詢
            query = Animal.query.filter(
                Animal.shelter_id == shelter_id,
                Animal.deleted_at == None
            )
            
            # 套用篩選
            status = filters.get('status')
            if status:
                try:
                    status_enum = AnimalStatus[status.upper()]
                    query = query.filter_by(status=status_enum)
                except KeyError:
                    raise ValueError(f'無效的狀態: {status}')
            
            species = filters.get('species')
            if species:
                try:
                    species_enum = Species[species.upper()]
                    query = query.filter_by(species=species_enum)
                except KeyError:
                    raise ValueError(f'無效的物種: {species}')

            sex = filters.get('sex')
            if sex:
                try:
                    sex_enum = Sex[sex.upper()]
                    query = query.filter_by(sex=sex_enum)
                except KeyError:
                    raise ValueError(f'無效的性別: {sex}')

            keyword = filters.get('keyword')
            if keyword:
                kw = f"%{keyword}%"
                query = query.filter(
                    or_(
                        Animal.name.ilike(kw),
                        Animal.breed.ilike(kw),
                        Animal.color.ilike(kw)
                    )
                )

            # 年齡範圍篩選
            min_age = filters.get('min_age')
            max_age = filters.get('max_age')
            if min_age is not None or max_age is not None:
                today = datetime.utcnow().date()
                if min_age is not None:
                    try:
                        cutoff_max = today.replace(year=today.year - min_age)
                    except ValueError:
                        cutoff_max = today.replace(year=today.year - min_age)
                    query = query.filter(Animal.dob != None).filter(Animal.dob <= cutoff_max)
                if max_age is not None:
                    try:
                        cutoff_min = today.replace(year=today.year - max_age)
                    except ValueError:
                        cutoff_min = today.replace(year=today.year - max_age)
                    query = query.filter(Animal.dob != None).filter(Animal.dob >= cutoff_min)

            # 疫苗接種篩選
            vaccinated = filters.get('vaccinated')
            if vaccinated is not None:
                vaccinated_bool = str(vaccinated).lower() == 'true'
                if vaccinated_bool:
                    query = query.filter(Animal.medical_records.any(
                        db.and_(MedicalRecord.record_type == RecordType.VACCINE, MedicalRecord.verified == True)
                    ))
                else:
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
            
            return {
                'animals': [animal.to_dict(include_relations=True) for animal in animals],
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Get shelter animals error: {str(e)}")
            raise RuntimeError(f"獲取收容所動物列表失敗: {str(e)}")

    @staticmethod
    def validate_file_upload(files, file_type='csv', max_size_mb=10):
        """
        驗證文件上傳
        
        Args:
            files: 上傳的文件列表
            file_type: 允許的文件類型
            max_size_mb: 最大文件大小(MB)
        
        Returns:
            list: 驗證後的文件數據
        """
        validated_files = []
        max_size_bytes = max_size_mb * 1024 * 1024
        
        for file in files:
            if file.filename and file.filename != '':
                # 驗證文件大小
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > max_size_bytes:
                    raise ValueError(f'檔案 {file.filename} 超過 {max_size_mb}MB 限制')
                
                # 驗證文件類型
                if file_type == 'csv' and not file.filename.lower().endswith('.csv'):
                    raise ValueError(f'檔案 {file.filename} 必須為 CSV 格式')
                elif file_type == 'image' and not file.content_type.startswith('image/'):
                    raise ValueError(f'檔案 {file.filename} 不是圖片格式')
                
                validated_files.append({
                    'file': file,
                    'filename': file.filename,
                    'content_type': file.content_type,
                    'size': file_size
                })
        
        return validated_files

    @staticmethod
    def _process_medical_proofs(medical_proofs, shelter_id):
        """處理醫療證明文件上傳"""
        medical_proof_data = []
        
        # 導入 MinIO 客戶端
        try:
            from app.blueprints.uploads import minio_client, minio_available
            from config import Config
        except ImportError:
            raise RuntimeError('MinIO 服務不可用')
        
        if not minio_available:
            raise RuntimeError('MinIO 服務不可用')
        
        for proof in medical_proofs:
            if proof.filename and proof.filename != '':
                # 驗證文件類型
                allowed_types = [
                    'application/pdf',
                    'application/msword', 
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'image/jpeg', 'image/jpg', 'image/png'
                ]
                
                if not proof.content_type or proof.content_type not in allowed_types:
                    raise ValueError(f'醫療證明文件 {proof.filename} 格式不支援。支援格式: PDF, DOC, DOCX, JPG, PNG')
                
                # 驗證文件大小
                proof.seek(0, 2)
                proof_size = proof.tell()
                proof.seek(0)
                
                if proof_size > 10 * 1024 * 1024:
                    raise ValueError(f'醫療證明文件 {proof.filename} 超過 10MB 限制')
                
                # 驗證檔名格式
                filename_pattern = re.compile(r'^(.+?)_(\d+)\.(pdf|doc|docx|jpg|jpeg|png)$', re.IGNORECASE)
                match = filename_pattern.match(proof.filename)
                
                if not match:
                    raise ValueError(f'醫療證明文件 {proof.filename} 檔名格式錯誤。正確格式: 動物編號_記錄序號.副檔名')
                
                animal_code = match.group(1)
                record_sequence = int(match.group(2))
                
                # 上傳到 MinIO
                try:
                    ext = proof.filename.split('.')[-1] if '.' in proof.filename else 'pdf'
                    object_key = f"medical-proofs/{shelter_id}/{uuid_lib.uuid4()}.{ext}"
                    
                    minio_client.put_object(
                        bucket_name=Config.MINIO_BUCKET,
                        object_name=object_key,
                        data=proof,
                        length=proof_size,
                        content_type=proof.content_type
                    )
                    
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
                    raise RuntimeError(f'上傳醫療證明文件 {proof.filename} 失敗: {str(e)}')
        
        return medical_proof_data

    @staticmethod
    def _process_photos(photos, shelter_id):
        """處理照片上傳"""
        photos_data = []
        
        # 導入 MinIO 客戶端
        try:
            from app.blueprints.uploads import minio_client, minio_available
            from config import Config
        except ImportError:
            raise RuntimeError('MinIO 服務不可用')
        
        if not minio_available:
            raise RuntimeError('MinIO 服務不可用')
        
        for photo in photos:
            if photo.filename and photo.filename != '':
                # 驗證文件類型
                if not photo.content_type or not photo.content_type.startswith('image/'):
                    raise ValueError(f'檔案 {photo.filename} 不是圖片格式')
                
                # 驗證文件大小
                photo.seek(0, 2)
                photo_size = photo.tell()
                photo.seek(0)
                
                if photo_size > 5 * 1024 * 1024:
                    raise ValueError(f'照片 {photo.filename} 超過 5MB 限制')
                
                # 上傳到 MinIO
                try:
                    ext = photo.filename.split('.')[-1] if '.' in photo.filename else 'jpg'
                    object_key = f"batch-uploads/{shelter_id}/{uuid_lib.uuid4()}.{ext}"
                    
                    minio_client.put_object(
                        bucket_name=Config.MINIO_BUCKET,
                        object_name=object_key,
                        data=photo,
                        length=photo_size,
                        content_type=photo.content_type or 'image/jpeg'
                    )
                    
                    photo_url = f"http://{Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'}/{Config.MINIO_BUCKET}/{object_key}"
                    
                    photos_data.append({
                        'filename': photo.filename,
                        'content_type': photo.content_type,
                        'storage_key': object_key,
                        'url': photo_url,
                        'size': photo_size
                    })
                    
                except Exception as e:
                    raise RuntimeError(f'上傳照片 {photo.filename} 失敗: {str(e)}')
        
        return photos_data
