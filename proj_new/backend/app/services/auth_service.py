"""
Auth Service - 用戶認證相關業務邏輯
"""
from datetime import datetime, timedelta
import secrets
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
from flask_jwt_extended import create_access_token
from app import db
from app.models.user import User, UserRole
from app.models.pending_registration import PendingRegistration
from app.services.audit_service import AuditService
from app.services.email_service import EmailService
from app.utils.security import verify_password


class AuthService:
    """用戶認證業務邏輯服務"""

    @staticmethod
    def register_user(registration_data):
        """
        用戶註冊 - 簡化版本與原有流程相容
        
        Args:
            registration_data: dict 包含註冊資料
        
        Returns:
            dict: 處理結果
        
        Raises:
            ValueError: 資料驗證失敗
            RuntimeError: 系統錯誤
        """
        try:
            # 檢查 Email 是否已存在
            if User.query.filter_by(email=registration_data['email']).first():
                raise ValueError('此 Email 已經註冊過')
            
            # 檢查是否有待驗證的註冊
            existing_pending = PendingRegistration.query.filter_by(
                email=registration_data['email']
            ).first()
            
            if existing_pending:
                return {
                    'message': '此 email 已有未完成的驗證流程',
                    'pending_id': existing_pending.pending_id,
                    'verification_required': True
                }
            
            # 為了保持與現有流程相容，我們返回一個通用的成功訊息
            # 實際的 pending registration 創建仍由原有的 blueprint 處理
            return {
                'message': '請求已接收，請繼續使用現有的註冊流程',
                'verification_required': True
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Registration error: {str(e)}")
            raise RuntimeError(f"註冊失敗: {str(e)}")

    @staticmethod
    def login_user(email, password):
        """
        用戶登入
        
        Args:
            email: 用戶 Email
            password: 密碼
        
        Returns:
            dict: 登入結果包含 token 和用戶資訊
        
        Raises:
            ValueError: 登入失敗
            RuntimeError: 系統錯誤
        """
        try:
            user = User.query.filter_by(email=email, deleted_at=None).first()
            
            if not user or not verify_password(password, user.password_hash):
                # 記錄失敗嘗試
                if user:
                    user.failed_login_attempts += 1
                    if user.failed_login_attempts >= 5:
                        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                    db.session.commit()
                
                raise ValueError('Email 或密碼錯誤')
            
            # 檢查帳號是否被鎖定
            if user.locked_until and user.locked_until > datetime.utcnow():
                raise ValueError(f'帳號已被鎖定至 {user.locked_until.strftime("%Y-%m-%d %H:%M:%S")}')
            
            # 檢查帳號是否已驗證
            if not user.verified:
                raise ValueError('請先驗證您的 Email')
            
            # 重置失敗計數
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='user.login.success',
                actor_id=user.user_id,
                target_type='user',
                target_id=user.user_id
            )
            
            # 創建 JWT token
            access_token = create_access_token(
                identity=str(user.user_id),
                fresh=True
            )
            
            return {
                'access_token': access_token,
                'user': user.to_dict(),
                'message': '登入成功'
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            raise RuntimeError(f"登入失敗: {str(e)}")

    @staticmethod
    def get_user_profile(user_id):
        """
        獲取用戶檔案
        
        Args:
            user_id: 用戶 ID
        
        Returns:
            dict: 用戶資訊
        
        Raises:
            ValueError: 用戶不存在
        """
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        if not user:
            raise ValueError('使用者不存在或已刪除')
        
        return user.to_dict()

    @staticmethod
    def update_user_profile(user_id, profile_data):
        """
        更新用戶檔案
        
        Args:
            user_id: 用戶 ID
            profile_data: 更新資料
        
        Returns:
            dict: 更新後的用戶資訊
        
        Raises:
            ValueError: 用戶不存在或資料無效
            RuntimeError: 系統錯誤
        """
        try:
            user = db.session.get(User, user_id)
            if not user or user.deleted_at:
                raise ValueError('使用者不存在')
            
            # 記錄修改前狀態
            before_state = user.to_dict()
            
            # 更新允許的欄位
            updatable_fields = ['first_name', 'last_name', 'phone_number', 'region', 'address']
            for field in updatable_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='user.profile.update',
                actor_id=user_id,
                target_type='user',
                target_id=user_id,
                before_state=before_state,
                after_state=user.to_dict()
            )
            
            return user.to_dict()
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Profile update error: {str(e)}")
            raise RuntimeError(f"檔案更新失敗: {str(e)}")

    @staticmethod
    def request_password_reset(email):
        """
        請求密碼重置
        
        Args:
            email: 用戶 Email
        
        Returns:
            dict: 處理結果
        """
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                # 為了安全，不告知用戶 Email 是否存在
                return {'message': '如果該 Email 存在，重置連結已發送'}
            
            # 生成重置 token
            reset_token = secrets.token_urlsafe(32)
            user.password_reset_token = reset_token
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # 發送重置郵件
            EmailService.send_password_reset_email(email, reset_token)
            
            return {'message': '如果該 Email 存在，重置連結已發送'}
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password reset request error: {str(e)}")
            return {'message': '如果該 Email 存在，重置連結已發送'}

    @staticmethod
    def verify_email(verification_code):
        """
        驗證 Email
        
        Args:
            verification_code: 驗證碼
        
        Returns:
            dict: 驗證結果
        
        Raises:
            ValueError: 驗證失敗
            RuntimeError: 系統錯誤
        """
        try:
            pending = db.session.get(PendingRegistration, verification_code)
            if not pending:
                raise ValueError('無效的驗證連結')
            
            # 檢查是否過期
            if pending.expires_at < datetime.utcnow():
                db.session.delete(pending)
                db.session.commit()
                raise ValueError('驗證連結已過期，請重新註冊')
            
            # 檢查是否 Email 已被註冊
            if User.query.filter_by(email=pending.email).first():
                db.session.delete(pending)
                db.session.commit()
                raise ValueError('該 Email 已被註冊')
            
            # 創建用戶帳號
            user = User(
                email=pending.email,
                username=pending.username,
                password_hash=pending.password_hash,
                first_name=pending.first_name,
                last_name=pending.last_name,
                phone_number=pending.phone_number,
                region=pending.region,
                address=pending.address,
                role=UserRole.GENERAL_MEMBER,
                verified=True
            )
            
            db.session.add(user)
            db.session.delete(pending)
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='user.email.verify',
                actor_id=user.user_id,
                target_type='user',
                target_id=user.user_id,
                after_state=user.to_dict()
            )
            
            return {
                'message': 'Email 驗證成功，您現在可以登入',
                'user': user.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Email verification error: {str(e)}")
            raise RuntimeError(f"驗證失敗: {str(e)}")

    @staticmethod
    def reset_password(token, new_password):
        """
        重置密碼
        
        Args:
            token: 重置 token
            new_password: 新密碼
        
        Returns:
            dict: 處理結果
        
        Raises:
            ValueError: token 無效或過期
            RuntimeError: 系統錯誤
        """
        try:
            user = User.query.filter_by(password_reset_token=token).first()
            if not user or not user.password_reset_expires:
                raise ValueError('無效的重置連結')
            
            if user.password_reset_expires < datetime.utcnow():
                raise ValueError('重置連結已過期')
            
            # 更新密碼
            user.password_hash = generate_password_hash(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            user.password_changed_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='user.password.reset',
                actor_id=user.user_id,
                target_type='user',
                target_id=user.user_id
            )
            
            return {'message': '密碼重置成功，請使用新密碼登入'}
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password reset error: {str(e)}")
            raise RuntimeError(f"密碼重置失敗: {str(e)}")

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        變更密碼
        
        Args:
            user_id: 用戶 ID
            old_password: 舊密碼
            new_password: 新密碼
        
        Returns:
            dict: 處理結果
        
        Raises:
            ValueError: 舊密碼錯誤或用戶不存在
            RuntimeError: 系統錯誤
        """
        try:
            user = db.session.get(User, user_id)
            if not user or user.deleted_at:
                raise ValueError('使用者不存在')
            
            # 驗證舊密碼
            if not verify_password(old_password, user.password_hash):
                raise ValueError('舊密碼錯誤')
            
            # 更新密碼 - 需要使用我們的 hash_password 函數
            from app.utils.security import hash_password
            user.password_hash = hash_password(new_password)
            user.password_changed_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='user.password.change',
                actor_id=user_id,
                target_type='user',
                target_id=user_id
            )
            
            return {'message': '密碼變更成功'}
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password change error: {str(e)}")
            raise RuntimeError(f"密碼變更失敗: {str(e)}")

    @staticmethod
    def resend_verification_email(email):
        """
        重新發送驗證郵件
        
        Args:
            email: 用戶 Email
        
        Returns:
            dict: 處理結果
        """
        try:
            # 檢查是否有待驗證的註冊
            pending = PendingRegistration.query.filter_by(email=email).first()
            if not pending:
                # 檢查是否已經註冊但未驗證
                user = User.query.filter_by(email=email, verified=False).first()
                if not user:
                    return {'message': '找不到相關的註冊記錄'}
                
                # 為未驗證用戶創建新的驗證請求
                pending = PendingRegistration(
                    email=user.email,
                    username=user.username,
                    password_hash=user.password_hash,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone_number=user.phone_number,
                    region=user.region,
                    address=user.address,
                    verification_code=secrets.token_urlsafe(32),
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                db.session.add(pending)
                
                # 刪除原用戶記錄
                db.session.delete(user)
            else:
                # 更新過期時間和驗證碼
                pending.verification_code = secrets.token_urlsafe(32)
                pending.expires_at = datetime.utcnow() + timedelta(hours=24)
            
            db.session.commit()
            
            # 發送驗證郵件
            EmailService.send_verification_email(email, pending.verification_code)
            
            return {'message': '驗證郵件已重新發送，請檢查您的 Email'}
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Resend verification error: {str(e)}")
            return {'message': '發送失敗，請稍後再試'}

    @staticmethod
    def create_pending_registration(registration_data):
        """
        創建待驗證註冊記錄
        
        Args:
            registration_data: dict 包含註冊資料
        
        Returns:
            dict: 處理結果
        """
        try:
            from app.utils.security import hash_password, generate_numeric_code, hash_verification_code
            from app.services.email_service import email_service
            
            # 檢查 email 是否已存在
            if User.query.filter_by(email=registration_data['email']).first():
                raise ValueError('此 email 已被註冊')
            
            existing_pending = PendingRegistration.query.filter_by(email=registration_data['email']).first()
            if existing_pending:
                return {
                    'message': '此 email 已有未完成的驗證流程',
                    'pending_id': existing_pending.pending_id,
                    'masked_email': AuthService._mask_email(existing_pending.email),
                    'expires_in': 15 * 60
                }

            pwd_hash = hash_password(registration_data['password'])
            code = generate_numeric_code(6)
            code_hash = hash_verification_code(code)
            expires = datetime.utcnow() + timedelta(minutes=15)

            pending = PendingRegistration(
                email=registration_data['email'],
                username=registration_data.get('username'),
                phone_number=registration_data.get('phone_number'),
                region=registration_data.get('region'),
                address=registration_data.get('address'),
                password_hash=pwd_hash,
                verification_code_hash=code_hash,
                code_expires_at=expires,
                client_ip=registration_data.get('client_ip'),
                user_agent=registration_data.get('user_agent')
            )

            db.session.add(pending)
            db.session.commit()

            # 發送驗證碼
            email_service.send_registration_code_email(
                user_email=pending.email,
                username=pending.username or pending.email,
                code=code,
                expires_minutes=15
            )

            return {
                'message': '驗證碼已發送至電子郵件',
                'pending_id': pending.pending_id,
                'masked_email': AuthService._mask_email(pending.email),
                'expires_in': 15 * 60
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration creation error: {str(e)}")
            raise RuntimeError(f'註冊失敗: {str(e)}')
    
    @staticmethod
    def verify_registration_code(pending_id, code, role=None):
        """
        驗證註冊驗證碼並創建用戶
        
        Args:
            pending_id: 待驗證ID
            code: 驗證碼
            role: 用戶角色（可選）
        
        Returns:
            dict: 處理結果
        """
        try:
            from app.utils.security import verify_verification_code
            
            pending = db.session.get(PendingRegistration, pending_id)
            if not pending:
                raise ValueError('找不到對應的驗證流程')

            if pending.code_expires_at < datetime.utcnow():
                db.session.delete(pending)
                db.session.commit()
                raise ValueError('驗證碼已過期，請重新註冊或重新發送')

            if not verify_verification_code(code, pending.verification_code_hash):
                pending.attempts = (pending.attempts or 0) + 1
                db.session.commit()
                if pending.attempts >= 5:
                    db.session.delete(pending)
                    db.session.commit()
                    raise ValueError('驗證失敗次數過多，請重新註冊')
                raise ValueError('驗證碼錯誤')

            if User.query.filter_by(email=pending.email).first():
                db.session.delete(pending)
                db.session.commit()
                raise ValueError('此 email 已被註冊')

            # 創建用戶
            role_to_set = UserRole.GENERAL_MEMBER
            if role:
                try:
                    role_to_set = UserRole(role)
                except ValueError:
                    role_to_set = UserRole.GENERAL_MEMBER

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
            AuditService.log(
                action='user.register',
                actor_id=user.user_id,
                target_type='user',
                target_id=user.user_id,
                before_state=None,
                after_state={'email': user.email},
                shelter_id=None
            )

            return {'message': '驗證成功，帳號已建立'}
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration verification error: {str(e)}")
            raise RuntimeError(f'驗證失敗: {str(e)}')
    
    @staticmethod
    def resend_registration_code(pending_id):
        """
        重新發送註冊驗證碼
        
        Args:
            pending_id: 待驗證ID
        
        Returns:
            dict: 處理結果
        """
        try:
            from app.utils.security import generate_numeric_code, hash_verification_code
            from app.services.email_service import email_service
            
            pending = db.session.get(PendingRegistration, pending_id)
            if not pending:
                raise ValueError('找不到對應的驗證流程')

            # 檢查重發限制
            if pending.resend_count >= 5:
                raise ValueError('已達今日重新寄信上限')

            # 生成新驗證碼
            code = generate_numeric_code(6)
            pending.verification_code_hash = hash_verification_code(code)
            pending.code_expires_at = datetime.utcnow() + timedelta(minutes=15)
            pending.resend_count = (pending.resend_count or 0) + 1
            db.session.commit()

            # 發送驗證碼
            email_service.send_registration_code_email(
                user_email=pending.email,
                username=pending.username or pending.email,
                code=code,
                expires_minutes=15
            )

            return {'message': '驗證碼已重新發送'}
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration code resend error: {str(e)}")
            raise RuntimeError(f'重新發送失敗: {str(e)}')
    
    @staticmethod
    def _mask_email(email):
        """
        遮罩 email 地址
        
        Args:
            email: 原始 email
        
        Returns:
            str: 遮罩後的 email
        """
        if '@' in email:
            local, domain = email.split('@', 1)
            if len(local) > 3:
                return local[:3] + '***@' + domain
            else:
                return '***@' + domain
        return email

    @staticmethod
    def check_email_exists(email):
        """
        檢查 Email 是否已存在
        
        Args:
            email: Email 地址
        
        Returns:
            bool: 是否存在
        """
        user = User.query.filter_by(email=email).first()
        pending = PendingRegistration.query.filter_by(email=email).first()
        return user is not None or pending is not None