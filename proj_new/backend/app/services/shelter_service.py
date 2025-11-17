"""
Shelter Service - 收容所業務邏輯服務
集中管理收容所 CRUD、批次匯入、批次狀態更新等複雜業務邏輯
"""
import re
import csv
import io
import uuid as uuid_lib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from werkzeug.datastructures import FileStorage
from app import db
from app.models.shelter import Shelter
from app.models.user import User, UserRole
from app.models.animal import Animal, AnimalStatus, Species, Sex, AnimalImage
from app.models.medical_record import MedicalRecord, RecordType
from app.models.others import Job, JobType, JobStatus
from app.exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, ConflictError
)
from app.services.audit_service import audit_service
from app.services.notification_service import NotificationService


class ShelterService:
    """收容所服務類"""
    
    @staticmethod
    def check_shelter_permission(user_id: int, shelter_id: Optional[int] = None) -> bool:
        """
        檢查用戶是否有收容所操作權限
        
        Args:
            user_id: 用戶 ID
            shelter_id: 收容所 ID (可選)
            
        Returns:
            bool: 是否有權限
            
        Raises:
            NotFoundError: 用戶不存在
            PermissionDeniedError: 沒有權限
        """
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError('用戶不存在')
        
        # 管理員有完全權限
        if user.role == UserRole.ADMIN:
            return True
        
        # 收容所成員需要檢查關聯
        if user.role == UserRole.SHELTER_MEMBER:
            if shelter_id:
                # 檢查是否為該收容所的主要負責人或關聯成員
                shelter = db.session.get(Shelter, shelter_id)
                if shelter and (shelter.primary_account_user_id == user_id or 
                              user.primary_shelter_id == shelter_id):
                    return True
            else:
                # 創建新收容所時,只要是收容所成員即可
                return True
        
        # 沒有權限則拋出異常
        raise PermissionDeniedError('沒有收容所操作權限')
    
    @staticmethod
    def create_shelter(user_id: int, name: str, contact_email: str, 
                      contact_phone: str, address: Dict[str, str],
                      slug: Optional[str] = None, region: Optional[str] = None) -> Shelter:
        """
        創建收容所
        
        Args:
            user_id: 創建者 ID (必須是 SHELTER_MEMBER 或 ADMIN)
            name: 收容所名稱
            contact_email: 聯繫 Email
            contact_phone: 聯繫電話
            address: 地址 (必須包含 street, city, county, postal_code)
            slug: 友好 URL slug (可選)
            region: 地區 (可選)
            
        Returns:
            Shelter: 創建的收容所對象
            
        Raises:
            PermissionDeniedError: 用戶沒有創建權限
            ValidationError: 必填欄位缺失或格式錯誤
            ConflictError: Slug 已存在
        """
        # 檢查權限
        if not ShelterService.check_shelter_permission(user_id):
            raise PermissionDeniedError('僅收容所成員或管理員可創建收容所')
        
        # 驗證 Email 格式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, contact_email):
            raise ValidationError('Email 格式不正確')
        
        # 驗證地址結構
        if not isinstance(address, dict):
            raise ValidationError('地址必須為 JSON 對象')
        
        required_address_fields = ['street', 'city', 'county', 'postal_code']
        for field in required_address_fields:
            if field not in address:
                raise ValidationError(f'地址缺少必填欄位: {field}')
        
        # 檢查 slug 唯一性
        if slug:
            if Shelter.query.filter_by(slug=slug).first():
                raise ConflictError('Slug 已存在')
        
        # 創建收容所
        shelter = Shelter(
            name=name,
            slug=slug,
            contact_email=contact_email,
            contact_phone=contact_phone,
            address=address,
            region=region,
            verified=False,
            primary_account_user_id=user_id
        )
        
        db.session.add(shelter)
        db.session.commit()
        
        return shelter
    
    @staticmethod
    def update_shelter(shelter_id: int, user_id: int, 
                      name: Optional[str] = None,
                      slug: Optional[str] = None,
                      contact_email: Optional[str] = None,
                      contact_phone: Optional[str] = None,
                      address: Optional[Dict[str, str]] = None,
                      region: Optional[str] = None) -> Shelter:
        """
        更新收容所資訊
        
        Args:
            shelter_id: 收容所 ID
            user_id: 操作者 ID (必須有權限)
            name: 新名稱 (可選)
            slug: 新 slug (可選)
            contact_email: 新 Email (可選)
            contact_phone: 新電話 (可選)
            address: 新地址 (可選)
            region: 新地區 (可選)
            
        Returns:
            Shelter: 更新後的收容所對象
            
        Raises:
            NotFoundError: 收容所不存在
            PermissionDeniedError: 用戶沒有更新權限
            ValidationError: 格式錯誤
            ConflictError: Slug 衝突
        """
        shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
        if not shelter:
            raise NotFoundError('收容所不存在')
        
        # 檢查權限
        if not ShelterService.check_shelter_permission(user_id, shelter_id):
            raise PermissionDeniedError('無權限更新此收容所')
        
        # 更新欄位
        if name is not None:
            shelter.name = name
        
        if slug is not None:
            # 檢查 slug 唯一性(排除自己)
            existing = Shelter.query.filter(
                Shelter.slug == slug,
                Shelter.shelter_id != shelter_id
            ).first()
            if existing:
                raise ConflictError('Slug 已存在')
            shelter.slug = slug
        
        if contact_email is not None:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, contact_email):
                raise ValidationError('Email 格式不正確')
            shelter.contact_email = contact_email
        
        if contact_phone is not None:
            shelter.contact_phone = contact_phone
        
        if address is not None:
            if not isinstance(address, dict):
                raise ValidationError('地址必須為 JSON 對象')
            
            required_fields = ['street', 'city', 'county', 'postal_code']
            for field in required_fields:
                if field not in address:
                    raise ValidationError(f'地址缺少必填欄位: {field}')
            
            shelter.address = address
        
        if region is not None:
            shelter.region = region
        
        shelter.updated_at = datetime.utcnow()
        db.session.commit()
        
        return shelter
    
    @staticmethod
    def verify_shelter(shelter_id: int, admin_id: int, verified: bool = True) -> Shelter:
        """
        驗證/取消驗證收容所（僅管理員）
        
        Args:
            shelter_id: 收容所 ID
            admin_id: 管理員 ID
            verified: 驗證狀態
            
        Returns:
            Shelter: 更新後的收容所對象
            
        Raises:
            NotFoundError: 收容所不存在
            PermissionDeniedError: 非管理員用戶
        """
        admin = db.session.get(User, admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            raise PermissionDeniedError('僅管理員可驗證收容所')
        
        shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
        if not shelter:
            raise NotFoundError('收容所不存在')
        
        shelter.verified = verified
        shelter.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 記錄審計日誌
        audit_service.log_shelter_verify(shelter_id, admin_id, verified)
        
        return shelter
    
    @staticmethod
    def validate_csv_file(file: FileStorage, max_size_mb: int = 10) -> Tuple[str, Dict[str, Any]]:
        """
        驗證並讀取 CSV 檔案
        
        Args:
            file: 上傳的檔案
            max_size_mb: 最大檔案大小 (MB)
            
        Returns:
            Tuple[str, Dict]: (CSV 內容, 檔案資訊)
            
        Raises:
            ValidationError: 檔案格式或大小錯誤
        """
        if not file or file.filename == '':
            raise ValidationError('未選擇檔案')
        
        if not file.filename.lower().endswith('.csv'):
            raise ValidationError('檔案必須為 CSV 格式')
        
        # 檢查檔案大小
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        max_size = max_size_mb * 1024 * 1024
        if file_size > max_size:
            raise ValidationError(f'檔案不能超過 {max_size_mb}MB')
        
        # 讀取內容
        try:
            csv_content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            raise ValidationError('CSV 編碼錯誤,請使用 UTF-8 編碼')
        
        # 驗證 CSV 格式
        try:
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            first_row = next(csv_reader, None)
            if not first_row:
                raise ValidationError('CSV 檔案為空')
        except Exception as e:
            raise ValidationError(f'CSV 格式錯誤: {str(e)}')
        
        file_info = {
            'filename': file.filename,
            'size': file_size,
            'content_type': file.content_type or 'text/csv'
        }
        
        return csv_content, file_info
    
    @staticmethod
    def upload_file_to_minio(file: FileStorage, minio_client, bucket: str,
                            object_key_prefix: str, allowed_types: List[str],
                            max_size_mb: int = 10) -> Dict[str, Any]:
        """
        上傳檔案到 MinIO
        
        Args:
            file: 上傳的檔案
            minio_client: MinIO 客戶端
            bucket: 儲存桶名稱
            object_key_prefix: 物件鍵前綴
            allowed_types: 允許的 MIME 類型列表
            max_size_mb: 最大檔案大小 (MB)
            
        Returns:
            Dict: 包含 storage_key, url, size, content_type 的字典
            
        Raises:
            ValidationError: 檔案類型或大小不符
        """
        if not file.content_type or file.content_type not in allowed_types:
            raise ValidationError(f'檔案格式不支援。支援格式: {", ".join(allowed_types)}')
        
        # 檢查檔案大小
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        max_size = max_size_mb * 1024 * 1024
        if file_size > max_size:
            raise ValidationError(f'檔案 {file.filename} 超過 {max_size_mb}MB 限制')
        
        # 生成唯一的 object key
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
        object_key = f"{object_key_prefix}/{uuid_lib.uuid4()}.{ext}"
        
        # 上傳到 MinIO
        try:
            minio_client.put_object(
                bucket_name=bucket,
                object_name=object_key,
                data=file,
                length=file_size,
                content_type=file.content_type
            )
        except Exception as e:
            raise ValidationError(f'上傳檔案到 MinIO 失敗: {str(e)}')
        
        # 生成公開 URL (需要從 Config 取得 MINIO_EXTERNAL_ENDPOINT)
        from config import Config
        file_url = f"http://{Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'}/{bucket}/{object_key}"
        
        return {
            'filename': file.filename,
            'storage_key': object_key,
            'url': file_url,
            'size': file_size,
            'content_type': file.content_type
        }
    
    @staticmethod
    def create_batch_import_job(shelter_id: int, user_id: int,
                               animal_csv_content: str, animal_csv_filename: str,
                               medical_csv_content: Optional[str] = None,
                               medical_csv_filename: Optional[str] = None,
                               medical_proofs: List[Dict] = None,
                               photos: List[Dict] = None) -> Job:
        """
        創建批次匯入任務
        
        Args:
            shelter_id: 收容所 ID
            user_id: 創建者 ID
            animal_csv_content: 動物 CSV 內容
            animal_csv_filename: 動物 CSV 檔名
            medical_csv_content: 醫療記錄 CSV 內容 (可選)
            medical_csv_filename: 醫療記錄 CSV 檔名 (可選)
            medical_proofs: 醫療證明文件列表 (可選)
            photos: 照片列表 (可選)
            
        Returns:
            Job: 創建的任務對象
            
        Raises:
            NotFoundError: 收容所不存在
            PermissionDeniedError: 用戶沒有權限
        """
        # 檢查收容所
        shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
        if not shelter:
            raise NotFoundError('收容所不存在')
        
        # 檢查權限
        if not ShelterService.check_shelter_permission(user_id, shelter_id):
            raise PermissionDeniedError('無權限執行批次匯入')
        
        # 創建 Job 記錄
        job = Job(
            type=JobType.IMPORT_ANIMALS.value,
            status=JobStatus.PENDING,
            created_by=user_id,
            payload={
                'shelter_id': shelter_id,
                'animal_csv_content': animal_csv_content,
                'medical_csv_content': medical_csv_content,
                'medical_proofs': medical_proofs or [],
                'photos': photos or [],
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
        
        return job
    
    @staticmethod
    def batch_update_animal_status(shelter_id: int, user_id: int,
                                   animal_ids: List[int], action: str) -> Dict[str, Any]:
        """
        批次更新動物狀態
        
        Args:
            shelter_id: 收容所 ID
            user_id: 操作者 ID
            animal_ids: 動物 ID 列表
            action: 操作類型 ('draft', 'submit', 'publish', 'retire')
            
        Returns:
            Dict: 包含成功/失敗計數和錯誤訊息的字典
            
        Raises:
            NotFoundError: 收容所不存在
            PermissionDeniedError: 用戶沒有權限
            ValidationError: 操作類型無效或動物不存在
        """
        # 檢查收容所
        shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
        if not shelter:
            raise NotFoundError('收容所不存在')
        
        # 檢查權限
        if not ShelterService.check_shelter_permission(user_id, shelter_id):
            raise PermissionDeniedError('無權限執行批次操作')
        
        # 驗證操作類型
        if action not in ['draft', 'submit', 'publish', 'retire']:
            raise ValidationError('無效的操作類型。支援: draft, submit, publish, retire')
        
        # 檢查動物是否屬於該收容所
        animals = Animal.query.filter(
            Animal.animal_id.in_(animal_ids),
            Animal.shelter_id == shelter_id,
            Animal.deleted_at == None
        ).all()
        
        if len(animals) != len(animal_ids):
            found_ids = [a.animal_id for a in animals]
            missing_ids = [aid for aid in animal_ids if aid not in found_ids]
            raise ValidationError(f'以下動物不存在或不屬於該收容所: {missing_ids}')
        
        # 執行批次狀態更新
        success_count = 0
        failed_count = 0
        errors = []
        
        for animal in animals:
            try:
                if action == 'draft':
                    if animal.status in [AnimalStatus.SUBMITTED, AnimalStatus.PUBLISHED, AnimalStatus.RETIRED]:
                        animal.status = AnimalStatus.DRAFT
                        animal.updated_at = datetime.utcnow()
                        success_count += 1
                    else:
                        errors.append(f'動物 {animal.animal_id} ({animal.name}) 目前狀態無法變更為草稿')
                        failed_count += 1
                
                elif action == 'submit':
                    if animal.status == AnimalStatus.DRAFT:
                        animal.status = AnimalStatus.SUBMITTED
                        animal.updated_at = datetime.utcnow()
                        success_count += 1
                    else:
                        errors.append(f'動物 {animal.animal_id} ({animal.name}) 必須是草稿狀態才能提交')
                        failed_count += 1
                
                elif action == 'publish':
                    if animal.status in [AnimalStatus.SUBMITTED, AnimalStatus.DRAFT]:
                        animal.status = AnimalStatus.PUBLISHED
                        animal.updated_at = datetime.utcnow()
                        success_count += 1
                    else:
                        errors.append(f'動物 {animal.animal_id} ({animal.name}) 目前狀態無法發布')
                        failed_count += 1
                
                elif action == 'retire':
                    if animal.status == AnimalStatus.PUBLISHED:
                        animal.status = AnimalStatus.RETIRED
                        animal.updated_at = datetime.utcnow()
                        success_count += 1
                    else:
                        errors.append(f'動物 {animal.animal_id} ({animal.name}) 必須是已發布狀態才能下架')
                        failed_count += 1
            
            except Exception as e:
                errors.append(f'動物 {animal.animal_id} ({animal.name}) 處理失敗: {str(e)}')
                failed_count += 1
        
        # 提交變更
        db.session.commit()
        
        # 創建通知
        action_names = {
            'draft': '草稿',
            'submit': '提交審核',
            'publish': '發布',
            'retire': '下架'
        }
        action_name = action_names.get(action, action)
        
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
            'success_count': success_count,
            'failed_count': failed_count,
            'total_count': len(animal_ids),
            'errors': errors[:10],  # 只返回前10個錯誤
            'action': action_name
        }
    
    @staticmethod
    def list_shelters(page: int = 1, per_page: int = 10, search: Optional[str] = None,
                     verified_only: bool = False) -> Dict[str, Any]:
        """
        列出收容所（支援分頁和搜尋）
        
        Args:
            page: 頁碼
            per_page: 每頁數量
            search: 搜尋關鍵字
            verified_only: 僅顯示已驗證收容所
            
        Returns:
            Dict: 包含收容所列表和分頁資訊
        """
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        query = Shelter.query.filter_by(deleted_at=None)
        
        if search:
            query = query.filter(
                db.or_(
                    Shelter.name.ilike(f'%{search}%'),
                    Shelter.contact_email.ilike(f'%{search}%')
                )
            )
        
        if verified_only:
            query = query.filter_by(verified=True)
        
        query = query.order_by(Shelter.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'shelters': [shelter.to_dict() for shelter in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def get_shelter(shelter_id: int) -> Shelter:
        """
        取得單一收容所資訊
        
        Args:
            shelter_id: 收容所 ID
            
        Returns:
            Shelter: 收容所對象
            
        Raises:
            NotFoundError: 收容所不存在
        """
        shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
        if not shelter:
            raise NotFoundError('收容所不存在')
        
        return shelter


# 創建全局實例
shelter_service = ShelterService()
