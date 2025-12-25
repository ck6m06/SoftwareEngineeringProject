"""
Email Service unit tests
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app import create_app
from app.services.email_service import email_service


@pytest.fixture
def app():
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield app


class TestSendViaSMTP:
    """Test _send_via_smtp method"""
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_via_smtp_success(self, mock_smtp_class, app_context):
        """測試成功透過 SMTP 發送郵件"""
        app_context.config['SMTP_HOST'] = 'smtp.gmail.com'
        app_context.config['SMTP_PORT'] = 587
        app_context.config['SMTP_USER'] = 'test@example.com'
        app_context.config['SMTP_PASSWORD'] = 'password'
        app_context.config['SMTP_USE_TLS'] = True
        app_context.config['SMTP_USE_SSL'] = False
        app_context.config['SMTP_FROM'] = 'no-reply@example.com'
        
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        
        result = email_service._send_via_smtp('Test', 'test@example.com', 'Body')
        
        assert result is True
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with('test@example.com', 'password')
        mock_smtp.send_message.assert_called_once()
    
    def test_send_via_smtp_no_config_fallback(self, app_context):
        """測試無 SMTP 設定時直接返回 True"""
        app_context.config['SMTP_HOST'] = None
        
        result = email_service._send_via_smtp('Test', 'test@example.com', 'Body')
        
        assert result is True
    
    @patch('app.services.email_service.smtplib.SMTP_SSL')
    def test_send_via_smtp_ssl(self, mock_smtp_ssl_class, app_context):
        """測試使用 SSL 連接"""
        app_context.config['SMTP_HOST'] = 'smtp.gmail.com'
        app_context.config['SMTP_PORT'] = 465
        app_context.config['SMTP_USER'] = 'test@example.com'
        app_context.config['SMTP_PASSWORD'] = 'password'
        app_context.config['SMTP_USE_SSL'] = True
        app_context.config['SMTP_USE_TLS'] = False
        app_context.config['SMTP_FROM'] = 'no-reply@example.com'
        
        mock_smtp = MagicMock()
        mock_smtp_ssl_class.return_value = mock_smtp
        
        result = email_service._send_via_smtp('Test', 'test@example.com', 'Body')
        
        assert result is True
        mock_smtp.login.assert_called_once()
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_via_smtp_failure_fallback(self, mock_smtp_class, app_context):
        """測試 SMTP 失敗時回退"""
        app_context.config['SMTP_HOST'] = 'smtp.gmail.com'
        app_context.config['SMTP_PORT'] = 587
        app_context.config['SMTP_USER'] = 'test@example.com'
        app_context.config['SMTP_PASSWORD'] = 'password'
        app_context.config['SMTP_USE_TLS'] = True
        app_context.config['SMTP_FROM'] = 'no-reply@example.com'
        
        mock_smtp_class.side_effect = Exception('Connection failed')
        
        result = email_service._send_via_smtp('Test', 'test@example.com', 'Body')
        
        assert result is False
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_via_smtp_with_html(self, mock_smtp_class, app_context):
        """測試發送 HTML 郵件"""
        app_context.config['SMTP_HOST'] = 'smtp.gmail.com'
        app_context.config['SMTP_PORT'] = 587
        app_context.config['SMTP_USER'] = 'test@example.com'
        app_context.config['SMTP_PASSWORD'] = 'password'
        app_context.config['SMTP_USE_TLS'] = True
        app_context.config['SMTP_FROM'] = 'no-reply@example.com'
        
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        
        html_content = '<html><body><h1>Test</h1></body></html>'
        result = email_service._send_via_smtp('Test', 'test@example.com', 'Body', html=html_content)
        
        assert result is True
        mock_smtp.send_message.assert_called_once()
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_via_smtp_login_failure(self, mock_smtp_class, app_context):
        """測試 SMTP 登入失敗"""
        app_context.config['SMTP_HOST'] = 'smtp.gmail.com'
        app_context.config['SMTP_PORT'] = 587
        app_context.config['SMTP_USER'] = 'test@example.com'
        app_context.config['SMTP_PASSWORD'] = 'wrong_password'
        app_context.config['SMTP_USE_TLS'] = True
        app_context.config['SMTP_FROM'] = 'no-reply@example.com'
        
        mock_smtp = MagicMock()
        mock_smtp.login.side_effect = Exception('Authentication failed')
        mock_smtp_class.return_value = mock_smtp
        
        result = email_service._send_via_smtp('Test', 'test@example.com', 'Body')
        
        assert result is False


class TestSendVerificationEmail:
    """Test send_verification_email method"""
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_verification_email(self, mock_send_smtp, app_context):
        """測試發送驗證郵件"""
        app_context.config['FRONTEND_URL'] = 'http://localhost:3000'
        app_context.config['APP_NAME'] = 'Test App'
        mock_send_smtp.return_value = True
        
        result = email_service.send_verification_email('test@example.com', 'testuser', 'token123')
        
        assert result is True
        mock_send_smtp.assert_called_once()
        call_args = mock_send_smtp.call_args
        assert call_args[0][1] == 'test@example.com'
        assert '驗證' in call_args[0][0]
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_verification_email_no_frontend_url(self, mock_send_smtp, app_context):
        """測試無 FRONTEND_URL 時使用 localhost 回退"""
        app_context.config['FRONTEND_URL'] = None
        app_context.config['APP_NAME'] = 'Test App'
        mock_send_smtp.return_value = True
        
        result = email_service.send_verification_email('test@example.com', 'testuser', 'token123')
        
        assert result is True
        call_args = mock_send_smtp.call_args
        assert 'localhost:5173' in call_args[0][2]


class TestSendPasswordResetEmail:
    """Test send_password_reset_email method"""
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_password_reset_email(self, mock_send_smtp, app_context):
        """測試發送密碼重置郵件"""
        app_context.config['FRONTEND_URL'] = 'http://localhost:3000'
        app_context.config['APP_NAME'] = 'Test App'
        mock_send_smtp.return_value = True
        
        result = email_service.send_password_reset_email('test@example.com', 'testuser', 'token123')
        
        assert result is True
        mock_send_smtp.assert_called_once()
        call_args = mock_send_smtp.call_args
        assert call_args[0][1] == 'test@example.com'
        assert '重置' in call_args[0][0]
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_password_reset_email_no_frontend_url(self, mock_send_smtp, app_context):
        """測試無 FRONTEND_URL 時使用 localhost 回退"""
        app_context.config['FRONTEND_URL'] = None
        app_context.config['APP_NAME'] = 'Test App'
        mock_send_smtp.return_value = True
        
        result = email_service.send_password_reset_email('test@example.com', 'testuser', 'token123')
        
        assert result is True
        call_args = mock_send_smtp.call_args
        assert 'localhost:5173' in call_args[0][2]


class TestSendRegistrationCodeEmail:
    """Test send_registration_code_email method"""
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_registration_code_email(self, mock_send_smtp, app_context):
        """測試發送註冊驗證碼郵件"""
        app_context.config['APP_NAME'] = 'Test App'
        mock_send_smtp.return_value = True
        
        result = email_service.send_registration_code_email('test@example.com', 'testuser', '123456')
        
        assert result is True
        mock_send_smtp.assert_called_once()
        call_args = mock_send_smtp.call_args
        assert call_args[0][1] == 'test@example.com'
        assert '驗證碼' in call_args[0][0]
        assert '123456' in call_args[0][2]


class TestSendEmail:
    """Test send_email method"""
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_email_simple(self, mock_send_smtp, app_context):
        """測試簡單郵件發送"""
        mock_send_smtp.return_value = True
        
        result = email_service.send_email(
            to='test@example.com',
            subject='Test Subject',
            context={'message': 'Test Message'}
        )
        
        assert result is True
        mock_send_smtp.assert_called_once()
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_email_with_animal_info(self, mock_send_smtp, app_context):
        """測試包含動物資訊的郵件"""
        mock_send_smtp.return_value = True
        
        result = email_service.send_email(
            to='test@example.com',
            subject='Test',
            context={
                'message': 'Test',
                'animal_name': '小白',
                'status': '已送養'
            }
        )
        
        assert result is True
        call_args = mock_send_smtp.call_args
        body = call_args[0][2]
        assert '小白' in body
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_email_with_contact_info(self, mock_send_smtp, app_context):
        """測試包含機構聯絡資訊的郵件"""
        mock_send_smtp.return_value = True
        
        contact_info = {
            'type': 'shelter',
            'name': '愛心動物之家',
            'email': 'shelter@example.com',
            'phone': '02-12345678'
        }
        
        result = email_service.send_email(
            to='test@example.com',
            subject='Test',
            context={
                'message': 'Test',
                'contact_info': contact_info
            }
        )
        
        assert result is True
        call_args = mock_send_smtp.call_args
        body = call_args[0][2]
        assert '愛心動物之家' in body
        assert '02-12345678' in body
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_email_with_personal_contact_info(self, mock_send_smtp, app_context):
        """測試包含個人聯絡資訊的郵件"""
        mock_send_smtp.return_value = True
        
        contact_info = {
            'type': 'personal',
            'name': '張三',
            'email': 'user@example.com',
            'phone': '0912-345678'
        }
        
        result = email_service.send_email(
            to='test@example.com',
            subject='Test',
            context={
                'message': 'Test',
                'contact_info': contact_info
            }
        )
        
        assert result is True
        call_args = mock_send_smtp.call_args
        body = call_args[0][2]
        assert '張三' in body
        assert '姓名' in body
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_email_with_template_success(self, mock_send_smtp, app_context):
        """測試使用模板成功發送郵件"""
        mock_send_smtp.return_value = True
        
        # Mock Jinja2 template rendering
        mock_template_txt = Mock()
        mock_template_txt.render.return_value = 'Rendered Text'
        app_context.jinja_env.get_template = Mock(return_value=mock_template_txt)
        
        result = email_service.send_email(
            to='test@example.com',
            subject='Test',
            template='notification',
            context={'message': 'Test'}
        )
        
        assert result is True
        mock_send_smtp.assert_called_once()
    
    @patch('app.services.email_service.email_service._send_via_smtp')
    def test_send_email_template_not_found(self, mock_send_smtp, app_context):
        """測試模板不存在時回退到簡單格式"""
        mock_send_smtp.return_value = True
        app_context.jinja_env.get_template = Mock(side_effect=Exception('Template not found'))
        
        result = email_service.send_email(
            to='test@example.com',
            subject='Test',
            context={'message': 'Test Message'},
            template='nonexistent'
        )
        
        assert result is True
        call_args = mock_send_smtp.call_args
        assert 'Test Message' in call_args[0][2]
