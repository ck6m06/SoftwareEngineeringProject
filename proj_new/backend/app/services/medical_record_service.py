"""
Medical Record Service - 醫療紀錄業務邏輯服務
集中管理醫療紀錄的 CRUD、權限檢查和附件處理
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app import db
from app.models.medical_record import MedicalRecord, RecordType
from app.models.animal import Animal
from app.models.user import User, UserRole
from app.models.others import Attachment
from app.exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError
)
from app.services.permission_service import permission_service


class MedicalRecordService:
    """醫療紀錄服務類"""
    
    @staticmethod
    def create_medical_record(animal_id: int, current_user_id: int, record_type: Optional[RecordType],
                             date: Optional[datetime.date], provider: Optional[str], details: Optional[str],
                             attachments_data: List[Dict] = None) -> MedicalRecord:
        """
        創建醫療紀錄
        
        Args:
            animal_id: 動物 ID
            current_user_id: 當前用戶 ID
            record_type: 紀錄類型
            date: 記錄日期
            provider: 醫療提供者
            details: 詳細說明
            attachments_data: 附件資料列表
            
        Returns:
            MedicalRecord: 創建的醫療記錄
            
        Raises:
            NotFoundError: 動物或用戶不存在
            PermissionDeniedError: 無權限創建醫療記錄
        """
        # 檢查動物
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        if not animal:
            raise NotFoundError('動物不存在')
        
        # 檢查權限
        user = db.session.get(User, current_user_id)
        if not user:
            raise NotFoundError('用戶不存在')
        
        has_permission = False
        
        if user.role == UserRole.ADMIN:
            has_permission = True
        elif animal.owner_id and animal.owner_id == current_user_id:
            # 個人送養動物：動物擁有者可創建
            has_permission = True
        elif animal.shelter_id and user.role == UserRole.SHELTER_MEMBER and user.primary_shelter_id == animal.shelter_id:
            # 收容所動物：該收容所成員可創建
            has_permission = True
        
        if not has_permission:
            raise PermissionDeniedError('無權限為此動物創建醫療紀錄')
        
        # 創建醫療記錄
        medical_record = MedicalRecord(
            animal_id=animal_id,
            record_type=record_type,
            date=date,
            provider=provider,
            details=details,
            attachments=attachments_data or [],
            verified=False,
            created_by=current_user_id
        )
        
        db.session.add(medical_record)
        db.session.flush()
        
        # 處理附件
        if attachments_data:
            for attachment_info in attachments_data:
                if isinstance(attachment_info, dict) and 'storage_key' in attachment_info:
                    attachment = Attachment(
                        owner_type='medical_record',
                        owner_id=medical_record.medical_record_id,
                        filename=attachment_info.get('filename', '未知檔案'),
                        storage_key=attachment_info.get('storage_key'),
                        url=attachment_info.get('url'),
                        mime_type=attachment_info.get('mime_type'),
                        size=attachment_info.get('size'),
                        meta_data={
                            'type': 'user_uploaded',
                            'uploaded_via': 'medical_record_form'
                        },
                        created_by=current_user_id
                    )
                    db.session.add(attachment)
        
        db.session.commit()
        return medical_record
    
    @staticmethod
    def update_medical_record(record_id: int, current_user_id: int, 
                             record_type: Optional[RecordType] = None,
                             date: Optional[datetime.date] = None,
                             provider: Optional[str] = None,
                             details: Optional[str] = None,
                             attachments_data: List[Dict] = None) -> MedicalRecord:
        """
        更新醫療紀錄
        
        Args:
            record_id: 醫療記錄 ID
            current_user_id: 當前用戶 ID
            record_type: 新紀錄類型（可選）
            date: 新記錄日期（可選）
            provider: 新醫療提供者（可選）
            details: 新詳細說明（可選）
            attachments_data: 新附件資料列表（可選）
            
        Returns:
            MedicalRecord: 更新後的醫療記錄
            
        Raises:
            NotFoundError: 記錄不存在
            PermissionDeniedError: 無權限更新或超出時間限制
        """
        record = MedicalRecord.query.filter_by(
            medical_record_id=record_id,
            deleted_at=None
        ).first()
        
        if not record:
            raise NotFoundError('醫療紀錄不存在')
        
        # 檢查權限
        user = db.session.get(User, current_user_id)
        if not user:
            raise NotFoundError('用戶不存在')
        
        animal = Animal.query.get(record.animal_id)
        has_permission = False
        
        # 管理員不能直接編輯（保護醫療記錄專業性）
        if user.role == UserRole.ADMIN:
            raise PermissionDeniedError('管理員無法直接編輯醫療記錄，請使用"標記需要修正"功能通知相關人員')
        
        # 創建者可在 24 小時內更新
        if record.created_by == current_user_id:
            if record.created_at and datetime.utcnow() - record.created_at <= timedelta(hours=24):
                has_permission = True
            else:
                raise PermissionDeniedError('只能在創建後 24 小時內更新醫療記錄')
        
        # 動物擁有者可更新
        if animal and animal.owner_id and animal.owner_id == current_user_id:
            has_permission = True
        
        # 收容所成員可更新所屬收容所動物的記錄
        if animal and animal.shelter_id and user.role == UserRole.SHELTER_MEMBER and user.primary_shelter_id == animal.shelter_id:
            has_permission = True
        
        if not has_permission:
            raise PermissionDeniedError('無權限更新此醫療紀錄')
        
        # 更新欄位
        if record_type is not None:
            record.record_type = record_type
        
        if date is not None:
            record.date = date
        
        if provider is not None:
            record.provider = provider
        
        if details is not None:
            record.details = details
        
        # 處理附件更新
        if attachments_data is not None:
            for attachment_info in attachments_data:
                if (isinstance(attachment_info, dict) and 
                    'storage_key' in attachment_info and 
                    not attachment_info.get('attachment_id')):
                    
                    # 新附件，創建記錄
                    attachment = Attachment(
                        owner_type='medical_record',
                        owner_id=record.medical_record_id,
                        filename=attachment_info.get('filename', '未知檔案'),
                        storage_key=attachment_info.get('storage_key'),
                        url=attachment_info.get('url'),
                        mime_type=attachment_info.get('mime_type'),
                        size=attachment_info.get('size'),
                        meta_data={
                            'type': 'user_uploaded',
                            'uploaded_via': 'medical_record_form_update'
                        },
                        created_by=current_user_id
                    )
                    db.session.add(attachment)
            
            # 更新 JSON 欄位（向後兼容）
            record.attachments = attachments_data
        
        record.updated_at = datetime.utcnow()
        db.session.commit()
        return record
    
    @staticmethod
    def verify_medical_record(record_id: int, current_user_id: int, verified: bool = True) -> MedicalRecord:
        """
        驗證/取消驗證醫療紀錄（僅管理員）
        
        Args:
            record_id: 醫療記錄 ID
            current_user_id: 當前用戶 ID (必須是管理員)
            verified: 驗證狀態
            
        Returns:
            MedicalRecord: 更新後的醫療記錄
            
        Raises:
            NotFoundError: 記錄不存在
            PermissionDeniedError: 非管理員用戶
        """
        user = db.session.get(User, current_user_id)
        if not user or user.role != UserRole.ADMIN:
            raise PermissionDeniedError('僅管理員可驗證醫療紀錄')
        
        record = MedicalRecord.query.filter_by(
            medical_record_id=record_id,
            deleted_at=None
        ).first()
        
        if not record:
            raise NotFoundError('醫療紀錄不存在')
        
        record.verified = verified
        record.verified_by = current_user_id if verified else None
        record.updated_at = datetime.utcnow()
        db.session.commit()
        
        return record
    
    @staticmethod
    def parse_date(date_str: str) -> datetime.date:
        """
        解析多種日期格式
        
        Args:
            date_str: 日期字串
            
        Returns:
            datetime.date: 解析後的日期
            
        Raises:
            ValidationError: 日期格式錯誤
        """
        date_str = date_str.strip()
        date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValidationError('日期格式錯誤,支援格式: YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY, DD-MM-YYYY')
    
    @staticmethod
    def list_animal_medical_records(animal_id: int) -> List[MedicalRecord]:
        """
        獲取動物的所有醫療記錄
        
        Args:
            animal_id: 動物 ID
            
        Returns:
            List[MedicalRecord]: 醫療記錄列表
            
        Raises:
            NotFoundError: 動物不存在
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        if not animal:
            raise NotFoundError('動物不存在')
        
        records = MedicalRecord.query.filter_by(
            animal_id=animal_id,
            deleted_at=None
        ).order_by(MedicalRecord.date.desc()).all()
        
        return records
    
    @staticmethod
    def get_medical_record(record_id: int) -> MedicalRecord:
        """
        獲取單一醫療記錄
        
        Args:
            record_id: 醫療記錄 ID
            
        Returns:
            MedicalRecord: 醫療記錄對象
            
        Raises:
            NotFoundError: 記錄不存在
        """
        record = MedicalRecord.query.filter_by(
            medical_record_id=record_id,
            deleted_at=None
        ).first()
        
        if not record:
            raise NotFoundError('醫療紀錄不存在')
        
        return record


# 創建全局實例
medical_record_service = MedicalRecordService()
