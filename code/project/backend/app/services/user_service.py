"""
User Service - 使用者業務邏輯服務
集中管理所有使用者相關的業務邏輯
"""
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from app import db
from app.models.user import User, UserRole
from app.models.others import Job, JobStatus
from app.exceptions import (
    PermissionDeniedError, NotFoundError, ValidationError, ConflictError
)
from app.utils.security import verify_password, hash_password


class UserService:
    """使用者業務邏輯服務類"""
    
    @staticmethod
    def get_user(user_id: int, current_user_id: int) -> Tuple[User, bool]:
        """
        獲取使用者資訊
        
        Args:
            user_id: 要查詢的使用者 ID
            current_user_id: 當前登入使用者 ID
            
        Returns:
            Tuple[User, bool]: (使用者物件, 是否包含敏感資訊)
            
        Raises:
            NotFoundError: 使用者不存在
        """
        current_user = db.session.get(User, current_user_id)
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        
        if not user:
            raise NotFoundError('使用者不存在')
        
        # 檢查權限 - 只有本人或管理員可以查看完整資訊
        include_sensitive = (
            current_user_id == user_id or 
            (current_user and current_user.role == UserRole.ADMIN)
        )
        
        return user, include_sensitive
    
    @staticmethod
    def update_user(user_id: int, current_user_id: int, data: Dict[str, Any]) -> User:
        """
        更新使用者資訊
        
        Args:
            user_id: 要更新的使用者 ID
            current_user_id: 當前登入使用者 ID
            data: 更新資料
            
        Returns:
            User: 更新後的使用者物件
            
        Raises:
            NotFoundError: 使用者不存在
            PermissionDeniedError: 沒有權限
            ConflictError: Email 已被使用
        """
        current_user = db.session.get(User, current_user_id)
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        
        if not user:
            raise NotFoundError('使用者不存在')
        
        # 檢查權限 - 只有本人或管理員可以更新
        if current_user_id != user_id and (not current_user or current_user.role != UserRole.ADMIN):
            raise PermissionDeniedError('沒有權限修改此使用者資訊')
        
        # 可更新的欄位
        allowed_fields = ['username', 'phone_number', 'first_name', 'last_name', 
                         'profile_photo_url', 'settings', 'region', 'address']
        
        # 管理員可以更新額外欄位
        if current_user and current_user.role == UserRole.ADMIN:
            allowed_fields.extend(['role', 'verified', 'primary_shelter_id'])
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # 特殊處理 email 更新 (需要重新驗證)
        if 'email' in data and data['email'] != user.email:
            # 檢查新 email 是否已被使用
            existing_user = User.query.filter_by(email=data['email'], deleted_at=None).first()
            if existing_user and existing_user.user_id != user_id:
                raise ConflictError('該電子郵件已被使用')
            
            user.email = data['email']
            user.verified = False  # 需要重新驗證
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return user
    
    @staticmethod
    def change_password(user_id: int, current_user_id: int, old_password: str, new_password: str) -> None:
        """
        修改密碼
        
        Args:
            user_id: 要修改密碼的使用者 ID
            current_user_id: 當前登入使用者 ID
            old_password: 舊密碼
            new_password: 新密碼
            
        Raises:
            PermissionDeniedError: 只能修改自己的密碼
            NotFoundError: 使用者不存在
            ValidationError: 密碼驗證失敗
        """
        # 只能修改自己的密碼
        if current_user_id != user_id:
            raise PermissionDeniedError('只能修改自己的密碼')
        
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        
        if not user:
            raise NotFoundError('使用者不存在')
        
        if not old_password or not new_password:
            raise ValidationError('old_password 和 new_password 為必填欄位')
        
        # 驗證舊密碼
        if not verify_password(old_password, user.password_hash):
            raise ValidationError('舊密碼錯誤')
        
        # 驗證新密碼長度
        if len(new_password) < 8:
            raise ValidationError('新密碼長度至少需要 8 個字元')
        
        # 更新密碼
        user.password_hash = hash_password(new_password)
        
        # 更新密碼變更時間 (如果欄位存在)
        if hasattr(user, 'password_changed_at'):
            user.password_changed_at = datetime.utcnow()
        
        # 重置失敗登入次數
        if hasattr(user, 'failed_login_attempts'):
            user.failed_login_attempts = 0
        if hasattr(user, 'locked_until'):
            user.locked_until = None
        
        db.session.commit()
    
    @staticmethod
    def request_data_export(user_id: int, current_user_id: int) -> int:
        """
        請求個人資料匯出 (GDPR)
        
        Args:
            user_id: 要匯出資料的使用者 ID
            current_user_id: 當前登入使用者 ID
            
        Returns:
            int: 任務 ID
            
        Raises:
            PermissionDeniedError: 只能匯出自己的資料
            NotFoundError: 使用者不存在
        """
        # 只能匯出自己的資料
        if current_user_id != user_id:
            raise PermissionDeniedError('只能匯出自己的資料')
        
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        
        if not user:
            raise NotFoundError('使用者不存在')
        
        # 創建匯出任務
        job = Job(
            type='user_data_export',
            status=JobStatus.PENDING,
            payload={'user_id': user_id},
            created_by=user_id
        )
        
        db.session.add(job)
        db.session.commit()
        
        # TODO: 將任務加入 Celery 隊列
        # export_user_data.delay(job.job_id, user_id)
        
        return job.job_id
    
    @staticmethod
    def request_data_deletion(user_id: int, current_user_id: int) -> int:
        """
        請求個人資料刪除 (GDPR)
        
        Args:
            user_id: 要刪除資料的使用者 ID
            current_user_id: 當前登入使用者 ID
            
        Returns:
            int: 任務 ID
            
        Raises:
            PermissionDeniedError: 沒有權限
            NotFoundError: 使用者不存在
        """
        current_user = db.session.get(User, current_user_id)
        
        # 只有本人或管理員可以刪除
        if current_user_id != user_id and (not current_user or current_user.role != UserRole.ADMIN):
            raise PermissionDeniedError('沒有權限刪除此使用者資料')
        
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        
        if not user:
            raise NotFoundError('使用者不存在')
        
        # 創建刪除任務
        job = Job(
            type='user_data_deletion',
            status=JobStatus.PENDING,
            payload={'user_id': user_id},
            created_by=current_user_id
        )
        
        db.session.add(job)
        db.session.commit()
        
        # TODO: 將任務加入 Celery 隊列
        # delete_user_data.delay(job.job_id, user_id)
        
        return job.job_id


# 創建全局實例
user_service = UserService()
