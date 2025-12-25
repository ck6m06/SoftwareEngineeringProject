"""
Auth Service unit tests
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.exceptions import NotFoundError, ValidationError, ConflictError, UnauthorizedError, PermissionDeniedError


class TestRegisterPending(unittest.TestCase):
    """Test register_pending method"""
    
    @patch('app.services.auth_service.email_service')
    @patch('app.services.auth_service.hash_verification_code')
    @patch('app.services.auth_service.generate_numeric_code')
    @patch('app.services.auth_service.hash_password')
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.PendingRegistration')
    def test_register_pending_success(self, mock_pending_model, mock_user_model, mock_db, mock_hash_pwd, mock_gen_code, mock_hash_code, mock_email):
        """測試成功創建待註冊記錄"""
        mock_user_query = Mock()
        mock_user_query.filter_by.return_value.first.return_value = None
        mock_user_model.query = mock_user_query
        
        mock_pending_query = Mock()
        mock_pending_query.filter_by.return_value.first.return_value = None
        mock_pending_model.query = mock_pending_query
        
        mock_hash_pwd.return_value = 'hashed_pwd'
        mock_gen_code.return_value = '123456'
        mock_hash_code.return_value = 'hashed_code'
        
        mock_pending = Mock(pending_id=1, email='test@example.com')
        mock_pending_model.return_value = mock_pending
        
        result = AuthService.register_pending(
            email='test@example.com',
            password='password123',
            username='testuser'
        )
        
        self.assertEqual(result.pending_id, 1)
        mock_db.session.add.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_register_pending_email_exists(self, mock_user_model):
        """測試 Email 已存在"""
        mock_user = Mock(email='test@example.com')
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query
        
        with self.assertRaises(ConflictError):
            AuthService.register_pending('test@example.com', 'password123', 'testuser')


class TestVerifyRegistration(unittest.TestCase):
    """Test verify_registration method"""
    
    @patch('app.services.auth_service.get_naive_taipei_now')
    @patch('app.services.auth_service.audit_service')
    @patch('app.services.auth_service.UserRole')
    @patch('app.services.auth_service.verify_verification_code')
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    def test_verify_registration_success(self, mock_user_model, mock_db, mock_verify_code, mock_role, mock_audit, mock_now):
        """測試成功驗證註冊"""
        current_time = datetime.utcnow()
        mock_now.return_value = current_time
        
        mock_pending = Mock(
            pending_id=1,
            email='test@example.com',
            password_hash='hashed_pwd',
            username='testuser',
            code_expires_at=current_time + timedelta(minutes=10),
            verification_code_hash='hash'
        )
        mock_db.session.get.return_value = mock_pending
        mock_verify_code.return_value = True
        
        mock_user_query = Mock()
        mock_user_query.filter_by.return_value.first.return_value = None
        mock_user_model.query = mock_user_query
        
        mock_user = Mock(user_id=1, email='test@example.com', verified=True)
        mock_user_model.return_value = mock_user
        mock_role.GENERAL_MEMBER = 'general_member'
        
        result = AuthService.verify_registration(1, '123456')
        
        self.assertEqual(result.email, 'test@example.com')
        mock_db.session.delete.assert_called_once_with(mock_pending)
    
    @patch('app.services.auth_service.db')
    def test_verify_registration_not_found(self, mock_db):
        """測試找不到待註冊記錄"""
        mock_db.session.get.return_value = None
        
        with self.assertRaises(NotFoundError):
            AuthService.verify_registration(999, '123456')
    
    @patch('app.services.auth_service.db')
    def test_verify_registration_expired(self, mock_db):
        """測試驗證碼已過期"""
        mock_pending = Mock(
            pending_id=1,
            code_expires_at=datetime.utcnow() - timedelta(minutes=1)
        )
        mock_db.session.get.return_value = mock_pending
        
        with self.assertRaises(ValidationError) as context:
            AuthService.verify_registration(1, '123456')
        
        self.assertIn('過期', str(context.exception))
        mock_db.session.delete.assert_called_once_with(mock_pending)
    
    @patch('app.services.auth_service.get_naive_taipei_now')
    @patch('app.services.auth_service.verify_verification_code')
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    def test_verify_registration_email_conflict(self, mock_user_model, mock_db, mock_verify_code, mock_now):
        """測試驗證時 email 已被註冊"""
        current_time = datetime.utcnow()
        mock_now.return_value = current_time
        
        mock_pending = Mock(
            pending_id=1,
            email='test@example.com',
            code_expires_at=current_time + timedelta(minutes=10),
            verification_code_hash='hash'
        )
        mock_db.session.get.return_value = mock_pending
        mock_verify_code.return_value = True
        
        # Email 已被其他人註冊
        mock_existing_user = Mock(email='test@example.com')
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_existing_user
        mock_user_model.query = mock_query
        
        with self.assertRaises(ConflictError) as context:
            AuthService.verify_registration(1, '123456')
        
        self.assertIn('已被註冊', str(context.exception))
        mock_db.session.delete.assert_called_once_with(mock_pending)
    
    @patch('app.services.auth_service.get_naive_taipei_now')
    @patch('app.services.auth_service.verify_verification_code')
    @patch('app.services.auth_service.db')
    def test_verify_registration_code_error_max_attempts(self, mock_db, mock_verify_code, mock_now):
        """測試驗證碼錯誤達到最大次數"""
        current_time = datetime.utcnow()
        mock_now.return_value = current_time
        
        mock_pending = Mock(
            pending_id=1,
            email='test@example.com',
            code_expires_at=current_time + timedelta(minutes=10),
            verification_code_hash='hash',
            attempts=4
        )
        mock_db.session.get.return_value = mock_pending
        mock_verify_code.return_value = False
        
        with self.assertRaises(ValidationError) as context:
            AuthService.verify_registration(1, 'wrong_code')
        
        self.assertIn('驗證失敗次數過多', str(context.exception))
        mock_db.session.delete.assert_called_with(mock_pending)
    
    @patch('app.services.auth_service.get_naive_taipei_now')
    @patch('app.services.auth_service.audit_service')
    @patch('app.services.auth_service.UserRole')
    @patch('app.services.auth_service.verify_verification_code')
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    def test_verify_registration_with_custom_role(self, mock_user_model, mock_db, mock_verify_code, mock_role, mock_audit, mock_now):
        """測試驗證註冊時指定角色"""
        current_time = datetime.utcnow()
        mock_now.return_value = current_time
        
        mock_pending = Mock(
            pending_id=1,
            email='test@example.com',
            password_hash='hashed_pwd',
            username='testuser',
            code_expires_at=current_time + timedelta(minutes=10),
            verification_code_hash='hash'
        )
        mock_db.session.get.return_value = mock_pending
        mock_verify_code.return_value = True
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_user_model.query = mock_query
        
        mock_user = Mock(user_id=1, email='test@example.com', verified=True)
        mock_user_model.return_value = mock_user
        mock_role.return_value = 'shelter_staff'
        mock_role.GENERAL_MEMBER = 'general_member'
        
        # Mock audit_service.log to succeed silently
        mock_audit.log.return_value = None
        
        result = AuthService.verify_registration(1, '123456', role='shelter_staff')
        
        self.assertEqual(result.email, 'test@example.com')


class TestResendRegistrationCode(unittest.TestCase):
    """Test resend_registration_code method"""
    
    @patch('app.services.auth_service.email_service')
    @patch('app.services.auth_service.hash_verification_code')
    @patch('app.services.auth_service.generate_numeric_code')
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.PendingRegistration')
    def test_resend_code_success(self, mock_pending_model, mock_db, mock_gen_code, mock_hash_code, mock_email):
        """測試成功重新發送驗證碼"""
        mock_pending = Mock(
            pending_id=1,
            email='test@example.com',
            username='testuser',
            resend_count=0
        )
        
        mock_query = Mock()
        mock_query.get.return_value = mock_pending
        mock_pending_model.query = mock_query
        
        mock_gen_code.return_value = '654321'
        mock_hash_code.return_value = 'new_hashed_code'
        
        AuthService.resend_registration_code(1)
        
        self.assertEqual(mock_pending.verification_code_hash, 'new_hashed_code')
        mock_email.send_registration_code_email.assert_called_once()
    
    @patch('app.services.auth_service.PendingRegistration')
    def test_resend_code_limit_exceeded(self, mock_pending_model):
        """測試重發次數超過限制"""
        mock_pending = Mock(
            pending_id=1,
            email='test@example.com',
            resend_count=5
        )
        
        mock_query = Mock()
        mock_query.get.return_value = mock_pending
        mock_pending_model.query = mock_query
        
        with self.assertRaises(ValidationError) as context:
            AuthService.resend_registration_code(1)
        
        self.assertIn('已達今日重新寄信上限', str(context.exception))


class TestLogin(unittest.TestCase):
    """Test login method"""
    
    @patch('app.services.auth_service.audit_service')
    @patch('app.services.auth_service.verify_password')
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.db')
    def test_login_success(self, mock_db, mock_user_model, mock_verify_pwd, mock_audit):
        """測試成功登入"""
        with patch('flask_jwt_extended.create_access_token') as mock_access, \
             patch('flask_jwt_extended.create_refresh_token') as mock_refresh:
            
            mock_user = Mock(
                user_id=1,
                email='test@example.com',
                password_hash='hashed_pwd',
                verified=True,
                is_locked=False,
                deleted_at=None,
                failed_login_attempts=0
            )
            
            mock_query = Mock()
            mock_query.filter_by.return_value.first.return_value = mock_user
            mock_user_model.query = mock_query
            
            mock_verify_pwd.return_value = True
            mock_access.return_value = 'access_token'
            mock_refresh.return_value = 'refresh_token'
            
            user, access_token, refresh_token = AuthService.login('test@example.com', 'password123')
            
            self.assertEqual(user.email, 'test@example.com')
            self.assertEqual(access_token, 'access_token')
            self.assertEqual(refresh_token, 'refresh_token')
    
    @patch('app.services.auth_service.User')
    def test_login_user_not_found(self, mock_user_model):
        """測試用戶不存在"""
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_user_model.query = mock_query
        
        with self.assertRaises(UnauthorizedError):
            AuthService.login('nonexist@example.com', 'password123')
    
    @patch('app.services.auth_service.User')
    def test_login_not_verified(self, mock_user_model):
        """測試 Email 未驗證"""
        mock_user = Mock(
            email='test@example.com',
            verified=False,
            deleted_at=None
        )
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query
        
        with self.assertRaises(PermissionDeniedError):
            AuthService.login('test@example.com', 'password123')
    
    @patch('app.services.auth_service.verify_password')
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.db')
    def test_login_wrong_password_increments_attempts(self, mock_db, mock_user_model, mock_verify_pwd):
        """測試密碼錯誤時增加失敗次數"""
        mock_user = Mock(
            email='test@example.com',
            verified=True,
            is_locked=False,
            deleted_at=None,
            failed_login_attempts=2
        )
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query
        
        mock_verify_pwd.return_value = False
        
        with self.assertRaises(UnauthorizedError):
            AuthService.login('test@example.com', 'wrong_password')
        
        self.assertEqual(mock_user.failed_login_attempts, 3)
        mock_db.session.commit.assert_called()
    
    @patch('app.services.auth_service.verify_password')
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.db')
    def test_login_locks_after_5_failures(self, mock_db, mock_user_model, mock_verify_pwd):
        """測試失敗 5 次後鎖定帳號"""
        mock_user = Mock(
            email='test@example.com',
            verified=True,
            is_locked=False,
            deleted_at=None,
            failed_login_attempts=4
        )
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query
        
        mock_verify_pwd.return_value = False
        
        with self.assertRaises(UnauthorizedError):
            AuthService.login('test@example.com', 'wrong_password')
        
        self.assertEqual(mock_user.failed_login_attempts, 5)
        self.assertIsNotNone(mock_user.locked_until)


class TestVerifyEmail(unittest.TestCase):
    """Test verify_email method"""
    
    @patch('app.services.auth_service.audit_service')
    @patch('app.services.auth_service.verify_token')
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    def test_verify_email_success(self, mock_user_model, mock_db, mock_verify_token, mock_audit):
        """測試成功驗證 Email"""
        mock_verify_token.return_value = 1
        
        mock_user = Mock(user_id=1, email='test@example.com', verified=False)
        mock_db.session.get.return_value = mock_user
        
        result = AuthService.verify_email('valid_token')
        
        self.assertTrue(mock_user.verified)
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.auth_service.verify_token')
    def test_verify_email_invalid_token(self, mock_verify_token):
        """測試無效 token"""
        mock_verify_token.return_value = None
        
        with self.assertRaises(ValidationError):
            AuthService.verify_email('invalid_token')
    
    @patch('app.services.auth_service.verify_token')
    @patch('app.services.auth_service.db')
    def test_verify_email_already_verified(self, mock_db, mock_verify_token):
        """測試已驗證的用戶"""
        mock_verify_token.return_value = 1
        
        mock_user = Mock(user_id=1, email='test@example.com', verified=True)
        mock_db.session.get.return_value = mock_user
        
        result = AuthService.verify_email('valid_token')
        
        self.assertTrue(result.verified)
        self.assertEqual(result, mock_user)


class TestSendVerificationEmail(unittest.TestCase):
    """Test send_verification_email method"""
    
    @patch('app.services.auth_service.email_service')
    @patch('app.services.auth_service.generate_verification_token')
    @patch('app.services.auth_service.User')
    def test_send_verification_email_success(self, mock_user_model, mock_gen_token, mock_email):
        """測試成功發送驗證郵件"""
        mock_user = Mock(
            user_id=1,
            email='test@example.com',
            username='testuser',
            verified=False,
            deleted_at=None
        )
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query
        
        mock_gen_token.return_value = 'verification_token'
        
        result = AuthService.send_verification_email('test@example.com')
        
        self.assertTrue(result)
        mock_email.send_verification_email.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_send_verification_email_already_verified(self, mock_user_model):
        """測試用戶已驗證"""
        mock_user = Mock(
            user_id=1,
            email='test@example.com',
            verified=True
        )
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query
        
        result = AuthService.send_verification_email('test@example.com')
        
        # 為安全考量,總是返回 True
        self.assertTrue(result)


class TestRequestPasswordReset(unittest.TestCase):
    """Test request_password_reset method"""
    
    @patch('app.services.auth_service.email_service')
    @patch('app.services.auth_service.generate_verification_token')
    @patch('app.services.auth_service.User')
    def test_request_password_reset_success(self, mock_user_model, mock_gen_token, mock_email):
        """測試成功請求密碼重置"""
        mock_user = Mock(
            user_id=1,
            email='test@example.com',
            username='testuser'
        )
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query
        
        mock_gen_token.return_value = 'reset_token'
        
        result = AuthService.request_password_reset('test@example.com')
        
        self.assertTrue(result)
        mock_email.send_password_reset_email.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_request_password_reset_user_not_found(self, mock_user_model):
        """測試用戶不存在 - 為安全考量總是返回 True"""
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_user_model.query = mock_query
        
        result = AuthService.request_password_reset('nonexist@example.com')
        
        # 為安全考量,總是返回 True
        self.assertTrue(result)


class TestResetPassword(unittest.TestCase):
    """Test reset_password method"""
    
    @patch('app.services.auth_service.audit_service')
    @patch('app.services.auth_service.hash_password')
    @patch('app.services.auth_service.verify_token')
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    def test_reset_password_success(self, mock_user_model, mock_db, mock_verify_token, mock_hash_pwd, mock_audit):
        """測試成功重置密碼"""
        mock_verify_token.return_value = 1
        
        mock_user = Mock(
            user_id=1, 
            email='test@example.com',
            password_hash='old_hash_12345678901234567890'
        )
        mock_db.session.get.return_value = mock_user
        
        mock_hash_pwd.return_value = 'new_hash_12345678901234567890'
        
        result = AuthService.reset_password('valid_token', 'new_password123')
        
        self.assertEqual(mock_user.password_hash, 'new_hash_12345678901234567890')
        self.assertEqual(mock_user.failed_login_attempts, 0)
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.auth_service.verify_token')
    def test_reset_password_invalid_token(self, mock_verify_token):
        """測試無效 token"""
        mock_verify_token.return_value = None
        
        with self.assertRaises(ValidationError):
            AuthService.reset_password('invalid_token', 'new_password123')
    
    def test_reset_password_weak_password(self):
        """測試密碼過短"""
        with self.assertRaises(ValidationError) as context:
            AuthService.reset_password('valid_token', 'short')
        
        self.assertIn('8 個字符', str(context.exception))


if __name__ == '__main__':
    unittest.main()
