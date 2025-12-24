"""
Auth Service - 身份驗證業務邏輯服務
集中管理所有認證相關的業務邏輯
"""
from datetime import datetime, timedelta
from app.utils.datetime_helper import get_naive_taipei_now
from typing import Optional, Dict, Any, Tuple
from app import db
from app.models.user import User, UserRole
from app.models.pending_registration import PendingRegistration
from app.utils.security import (
    hash_password, verify_password, 
    generate_verification_token, verify_token,
    generate_numeric_code, hash_verification_code, verify_verification_code
)
from app.exceptions import (
    ValidationError, ConflictError, NotFoundError, 
    PermissionDeniedError, UnauthorizedError
)
from app.services.audit_service import audit_service
from app.services.email_service import email_service


class AuthService:
    """認證服務類"""
    
    @staticmethod
    def register_pending(email: str, password: str, username: Optional[str] = None,
                        phone_number: Optional[str] = None, region: Optional[str] = None,
                        address: Optional[str] = None, client_ip: Optional[str] = None,
                        user_agent: Optional[str] = None) -> PendingRegistration:
        """
        創建待註冊記錄並發送驗證碼
        
        Args:
            email: Email 地址
            password: 明文密碼
            username: 用戶名（可選）
            phone_number: 電話號碼（可選）
            region: 地區（可選）
            address: 地址（可選）
            client_ip: 客戶端 IP
            user_agent: 用戶代理字串
            
        Returns:
            PendingRegistration: 待註冊記錄
            
        Raises:
            ConflictError: Email 已被註冊或已有未完成的驗證流程
        """
        # 檢查是否已註冊
        if User.query.filter_by(email=email).first():
            raise ConflictError('此 email 已被註冊')
        
        # 檢查是否已有未過期的 pending
        existing_pending = PendingRegistration.query.filter_by(email=email).first()
        if existing_pending:
            return existing_pending
        
        # 生成驗證碼
        pwd_hash = hash_password(password)
        code = generate_numeric_code(6)
        code_hash = hash_verification_code(code)
        expires = get_naive_taipei_now() + timedelta(minutes=15)
        
        # 創建待註冊記錄
        pending = PendingRegistration(
            email=email,
            username=username,
            phone_number=phone_number,
            region=region,
            address=address,
            password_hash=pwd_hash,
            verification_code_hash=code_hash,
            code_expires_at=expires,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        db.session.add(pending)
        db.session.commit()
        
        # 發送驗證碼
        email_service.send_registration_code_email(
            user_email=email,
            username=username or email,
            code=code,
            expires_minutes=15
        )
        
        return pending
    
    @staticmethod
    def verify_registration(pending_id: int, code: str, role: Optional[str] = None) -> User:
        """
        驗證註冊碼並創建用戶
        
        Args:
            pending_id: 待註冊記錄 ID
            code: 驗證碼
            role: 用戶角色（可選，默認為 GENERAL_MEMBER）
            
        Returns:
            User: 創建的用戶對象
            
        Raises:
            NotFoundError: 找不到待註冊記錄
            ValidationError: 驗證碼錯誤或已過期
            ConflictError: Email 已被註冊
        """
        pending = db.session.get(PendingRegistration, pending_id)
        if not pending:
            raise NotFoundError('找不到對應的驗證流程')
        
        # 檢查過期
        if pending.code_expires_at < get_naive_taipei_now():
            db.session.delete(pending)
            db.session.commit()
            raise ValidationError('驗證碼已過期，請重新註冊或重新發送')
        
        # 驗證驗證碼
        if not verify_verification_code(code, pending.verification_code_hash):
            pending.attempts = (pending.attempts or 0) + 1
            db.session.commit()
            if pending.attempts >= 5:
                db.session.delete(pending)
                db.session.commit()
                raise ValidationError('驗證失敗次數過多，請重新註冊')
            raise ValidationError('驗證碼錯誤')
        
        # 再次檢查 email 是否已被註冊
        if User.query.filter_by(email=pending.email).first():
            db.session.delete(pending)
            db.session.commit()
            raise ConflictError('此 email 已被註冊')
        
        # 確定用戶角色
        role_to_set = UserRole.GENERAL_MEMBER
        if role:
            try:
                role_to_set = UserRole(role)
            except ValueError:
                pass
        
        # 創建用戶
        user = User(
            email=pending.email,
            password_hash=pending.password_hash,
            username=pending.username,
            phone_number=pending.phone_number,
            region=pending.region,
            address=pending.address,
            role=role_to_set,
            verified=True
        )
        
        db.session.add(user)
        db.session.delete(pending)
        db.session.commit()
        
        # 記錄審計日誌
        audit_service.log(
            action='user.register',
            actor_id=user.user_id,
            target_type='user',
            target_id=user.user_id,
            before_state=None,
            after_state={'email': user.email}
        )
        
        return user
    
    @staticmethod
    def resend_registration_code(pending_id: int) -> None:
        """
        重新發送註冊驗證碼
        
        Args:
            pending_id: 待註冊記錄 ID
            
        Raises:
            NotFoundError: 找不到待註冊記錄
            ValidationError: 已達今日重新寄信上限
        """
        pending = PendingRegistration.query.get(pending_id)
        if not pending:
            raise NotFoundError('找不到對應的驗證流程')
        
        # 檢查重發次數限制
        if pending.resend_count >= 5:
            raise ValidationError('已達今日重新寄信上限')
        
        # 生成新驗證碼
        code = generate_numeric_code(6)
        pending.verification_code_hash = hash_verification_code(code)
        pending.code_expires_at = get_naive_taipei_now() + timedelta(minutes=15)
        pending.resend_count = (pending.resend_count or 0) + 1
        
        db.session.commit()
        
        # 發送驗證碼
        email_service.send_registration_code_email(
            user_email=pending.email,
            username=pending.username or pending.email,
            code=code,
            expires_minutes=15
        )
    
    @staticmethod
    def login(email: str, password: str) -> Tuple[User, str, str]:
        """
        用戶登入
        
        Args:
            email: Email 地址
            password: 密碼
            
        Returns:
            Tuple[User, str, str]: (用戶對象, access_token, refresh_token)
            
        Raises:
            UnauthorizedError: Email 或密碼錯誤
            PermissionDeniedError: Email 未驗證或帳號被鎖定
        """
        from flask_jwt_extended import create_access_token, create_refresh_token
        
        # 查詢用戶
        user = User.query.filter_by(email=email, deleted_at=None).first()
        if not user:
            raise UnauthorizedError('Email 或密碼錯誤')
        
        # 檢查 Email 是否已驗證
        if not user.verified:
            raise PermissionDeniedError('請先驗證 Email，或使用重新發送驗證郵件功能')
        
        # 檢查帳號是否被鎖定
        if user.is_locked:
            raise PermissionDeniedError(f'帳號已被鎖定至 {user.locked_until}')
        
        # 驗證密碼
        if not verify_password(password, user.password_hash):
            # 增加失敗次數
            user.failed_login_attempts += 1
            
            # 如果失敗次數超過 5 次，鎖定帳號 30 分鐘
            if user.failed_login_attempts >= 5:
                user.locked_until = get_naive_taipei_now() + timedelta(minutes=30)
            
            db.session.commit()
            raise UnauthorizedError('Email 或密碼錯誤')
        
        # 登入成功，重置失敗次數
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = get_naive_taipei_now()
        db.session.commit()
        
        # 創建 token
        access_token = create_access_token(identity=str(user.user_id))
        refresh_token = create_refresh_token(identity=str(user.user_id))
        
        # 記錄登入審計日誌
        audit_service.log_login(user.user_id, success=True)
        
        return user, access_token, refresh_token
    
    @staticmethod
    def verify_email(token: str) -> User:
        """
        驗證 Email
        
        Args:
            token: 驗證 token
            
        Returns:
            User: 驗證的用戶對象
            
        Raises:
            ValidationError: Token 無效或已過期
            NotFoundError: 用戶不存在
        """
        # 驗證 token (24 小時有效)
        user_id = verify_token(token, purpose='email-verify', max_age=86400)
        if not user_id:
            raise ValidationError('驗證 token 無效或已過期')
        
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError('使用者不存在')
        
        if user.verified:
            return user
        
        # 標記為已驗證
        user.verified = True
        db.session.commit()
        
        # 記錄審計日誌
        audit_service.log(
            action='user.email.verify',
            actor_id=user_id,
            target_type='user',
            target_id=user_id,
            before_state={'verified': False},
            after_state={'verified': True}
        )
        
        return user
    
    @staticmethod
    def send_verification_email(email: str) -> bool:
        """
        重新發送驗證郵件
        
        Args:
            email: Email 地址
            
        Returns:
            bool: 是否成功發送（為安全考量，總是返回 True）
        """
        user = User.query.filter_by(email=email).first()
        
        # 為安全考量，即使用戶不存在也返回成功
        if not user or user.verified:
            return True
        
        # 生成新 token 並發送
        token = generate_verification_token(user.user_id, purpose='email-verify')
        email_service.send_verification_email(
            user_email=user.email,
            username=user.username or user.email,
            token=token
        )
        
        return True
    
    @staticmethod
    def request_password_reset(email: str) -> bool:
        """
        請求密碼重置
        
        Args:
            email: Email 地址
            
        Returns:
            bool: 是否成功發送（為安全考量，總是返回 True）
        """
        user = User.query.filter_by(email=email).first()
        
        # 為安全考量，即使用戶不存在也返回成功
        if not user:
            return True
        
        # 生成密碼重置 token (有效期 1 小時)
        token = generate_verification_token(user.user_id, purpose='password-reset')
        
        # 發送密碼重置郵件
        email_service.send_password_reset_email(
            user_email=user.email,
            username=user.username or user.email,
            token=token
        )
        
        return True
    
    @staticmethod
    def reset_password(token: str, new_password: str) -> User:
        """
        重置密碼
        
        Args:
            token: 重置 token
            new_password: 新密碼
            
        Returns:
            User: 更新後的用戶對象
            
        Raises:
            ValidationError: Token 無效、已過期或密碼強度不足
            NotFoundError: 用戶不存在
        """
        # 驗證密碼強度
        if len(new_password) < 8:
            raise ValidationError('密碼長度至少需要 8 個字符')
        
        # 驗證 token (1 小時有效期)
        user_id = verify_token(token, purpose='password-reset', max_age=3600)
        if not user_id:
            raise ValidationError('重置 token 無效或已過期')
        
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError('使用者不存在')
        
        # 更新密碼
        old_password_hash = user.password_hash
        user.password_hash = hash_password(new_password)
        user.password_changed_at = get_naive_taipei_now()
        
        # 重置失敗登入次數
        user.failed_login_attempts = 0
        user.locked_until = None
        
        db.session.commit()
        
        # 記錄審計日誌
        audit_service.log(
            action='user.password.reset',
            actor_id=user_id,
            target_type='user',
            target_id=user_id,
            before_state={'password_hash': old_password_hash[:20] + '...'},
            after_state={'password_hash': user.password_hash[:20] + '...'}
        )
        
        return user


# 創建全局實例
auth_service = AuthService()
