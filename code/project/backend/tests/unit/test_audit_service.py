"""
單元測試：app/services/audit_service.py

測試審計日誌服務的所有業務邏輯
目標：100% 測試通過率 + 95%+ 覆蓋率
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from app import create_app
from app.services.audit_service import AuditService
from app.models.others import AuditLog


@pytest.fixture
def app():
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield app


# ==================== log ====================
class TestLog:
    
    def test_log_with_all_parameters(self, app_context, monkeypatch):
        """TC-01: 完整參數記錄審計日誌"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log(
            action='user.update',
            actor_id=1,
            target_type='user',
            target_id=2,
            before_state={'status': 'active'},
            after_state={'status': 'banned'},
            shelter_id=10,
            commit=True
        )
        
        assert result is not None
        assert result.action == 'user.update'
        assert result.actor_id == 1
        assert result.target_type == 'user'
        assert result.target_id == 2
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_log_without_commit(self, app_context, monkeypatch):
        """TC-02: 不立即提交的日誌記錄"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log(
            action='test.action',
            actor_id=1,
            commit=False
        )
        
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_not_called()
    
    def test_log_with_minimal_parameters(self, app_context, monkeypatch):
        """TC-03: 最小參數記錄（系統操作）"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log(
            action='system.maintenance'
        )
        
        assert result is not None
        assert result.action == 'system.maintenance'
        assert result.actor_id is None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_log_handles_exception_gracefully(self, app_context, monkeypatch):
        """TC-04: 異常處理不影響主流程"""
        mock_db_session = MagicMock()
        mock_db_session.add.side_effect = Exception('Database error')
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        # 應該返回 None 而不是拋出異常
        result = AuditService.log(
            action='test.action',
            actor_id=1
        )
        
        assert result is None
        mock_db_session.rollback.assert_called_once()


# ==================== 專用日誌方法 ====================
class TestSpecificLogMethods:
    
    def test_log_login_success(self, app_context, monkeypatch):
        """TC-05: 記錄成功登入"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log_login(user_id=1, success=True)
        
        assert result is not None
        assert result.action == 'user.login.success'
        assert result.actor_id == 1
        assert result.target_id == 1
    
    def test_log_login_failed(self, app_context, monkeypatch):
        """TC-06: 記錄失敗登入"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log_login(user_id=1, success=False)
        
        assert result is not None
        assert result.action == 'user.login.failed'
        assert result.actor_id is None  # 失敗時不記錄 actor_id
        assert result.target_id == 1
    
    def test_log_application_review(self, app_context, monkeypatch):
        """TC-07: 記錄申請審核"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log_application_review(
            application_id=100,
            reviewer_id=2,
            old_status='PENDING',
            new_status='APPROVED'
        )
        
        assert result is not None
        assert result.action == 'application.review'
        assert result.actor_id == 2
        assert result.target_id == 100
        assert result.before_state == {'status': 'PENDING'}
        assert result.after_state == {'status': 'APPROVED'}
    
    def test_log_animal_publish(self, app_context, monkeypatch):
        """TC-08: 記錄動物發布"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log_animal_publish(
            animal_id=50,
            admin_id=3,
            old_status='DRAFT'
        )
        
        assert result is not None
        assert result.action == 'animal.publish'
        assert result.actor_id == 3
        assert result.target_id == 50
        assert result.before_state == {'status': 'DRAFT'}
        assert result.after_state == {'status': 'PUBLISHED'}
    
    def test_log_shelter_verify(self, app_context, monkeypatch):
        """TC-09: 記錄收容所驗證"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log_shelter_verify(
            shelter_id=10,
            admin_id=3,
            verified=True
        )
        
        assert result is not None
        assert result.action == 'shelter.verify'
        assert result.actor_id == 3
        assert result.target_id == 10
        assert result.shelter_id == 10
        assert result.after_state == {'verified': True}
    
    def test_log_shelter_unverify(self, app_context, monkeypatch):
        """TC-10: 記錄收容所取消驗證"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log_shelter_verify(
            shelter_id=10,
            admin_id=3,
            verified=False
        )
        
        assert result is not None
        assert result.action == 'shelter.unverify'
        assert result.after_state == {'verified': False}
    
    def test_log_user_ban(self, app_context, monkeypatch):
        """TC-11: 記錄用戶封禁"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log_user_ban(
            target_user_id=5,
            admin_id=3,
            days=7,
            reason='Violation of terms'
        )
        
        assert result is not None
        assert result.action == 'user.ban'
        assert result.actor_id == 3
        assert result.target_id == 5
        assert result.after_state == {'days': 7, 'reason': 'Violation of terms'}
    
    def test_log_data_export(self, app_context, monkeypatch):
        """TC-12: 記錄資料匯出"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log_data_export(
            user_id=5,
            requester_id=5
        )
        
        assert result is not None
        assert result.action == 'user.data.export'
        assert result.actor_id == 5
        assert result.target_id == 5
    
    def test_log_data_deletion(self, app_context, monkeypatch):
        """TC-13: 記錄資料刪除"""
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.audit_service.db', mock_db)
        
        result = AuditService.log_data_deletion(
            user_id=5,
            requester_id=3
        )
        
        assert result is not None
        assert result.action == 'user.data.delete'
        assert result.actor_id == 3
        assert result.target_id == 5
