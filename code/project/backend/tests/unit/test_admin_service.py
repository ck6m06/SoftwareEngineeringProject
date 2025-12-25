"""
單元測試：app/services/admin_service.py

測試管理員服務的所有業務邏輯
目標：100% 測試通過率 + 95%+ 覆蓋率
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

from app import create_app
from app.services.admin_service import AdminService
from app.models.user import User, UserRole
from app.models.animal import Animal
from app.models.application import Application
from app.models.shelter import Shelter
from app.models.others import Job, AuditLog
from app.exceptions import NotFoundError, PermissionDeniedError, ValidationError


@pytest.fixture
def app():
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield app


# ==================== get_system_statistics ====================
class TestGetSystemStatistics:
    
    def test_returns_complete_statistics(self, app_context, monkeypatch):
        """TC-01: 返回完整的系統統計資料"""
        # Mock User.query
        mock_user_query = Mock()
        mock_user_query.filter_by.return_value.count.return_value = 100
        monkeypatch.setattr('app.services.admin_service.User.query', mock_user_query)
        
        # Mock Animal.query
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.count.return_value = 50
        monkeypatch.setattr('app.services.admin_service.Animal.query', mock_animal_query)
        
        # Mock Application.query
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.count.return_value = 30
        monkeypatch.setattr('app.services.admin_service.Application.query', mock_app_query)
        
        # Mock Shelter.query
        mock_shelter_query = Mock()
        mock_shelter_query.filter_by.return_value.count.return_value = 10
        monkeypatch.setattr('app.services.admin_service.Shelter.query', mock_shelter_query)
        
        # Mock Job.query
        mock_job_query = Mock()
        mock_job_query.count.return_value = 5
        mock_job_query.filter_by.return_value.count.return_value = 2
        monkeypatch.setattr('app.services.admin_service.Job.query', mock_job_query)
        
        result = AdminService.get_system_statistics()
        
        assert 'users' in result
        assert 'animals' in result
        assert 'applications' in result
        assert 'shelters' in result
        assert 'jobs' in result


# ==================== list_all_users ====================
class TestListAllUsers:
    
    def test_list_users_with_pagination(self, app_context, monkeypatch):
        """TC-02: 分頁列出用戶"""
        mock_user = Mock(spec=User)
        mock_user.to_dict.return_value = {'user_id': 1, 'username': 'test'}
        
        mock_pagination = Mock()
        mock_pagination.items = [mock_user]
        mock_pagination.total = 1
        
        mock_query = Mock()
        mock_query.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination
        monkeypatch.setattr('app.services.admin_service.User.query', mock_query)
        
        result = AdminService.list_all_users(page=1, per_page=20)
        
        assert result['total'] == 1
        assert result['page'] == 1
        assert len(result['users']) == 1
    
    def test_filter_users_by_role(self, app_context, monkeypatch):
        """TC-03: 依角色篩選用戶"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        mock_query.filter_by.return_value.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.admin_service.User.query', mock_query)
        
        result = AdminService.list_all_users(role='ADMIN')
        
        assert 'users' in result
    
    def test_search_users_by_keyword(self, app_context, monkeypatch):
        """TC-04: 關鍵字搜尋用戶"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        mock_query.filter_by.return_value.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.admin_service.User.query', mock_query)
        
        mock_db_or = Mock(return_value=True)
        monkeypatch.setattr('app.services.admin_service.db.or_', mock_db_or)
        
        result = AdminService.list_all_users(search='test')
        
        assert 'users' in result
    
    def test_invalid_role_raises_error(self, app_context, monkeypatch):
        """TC-05: 無效角色拋出錯誤"""
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        monkeypatch.setattr('app.services.admin_service.User.query', mock_query)
        
        with pytest.raises(ValidationError, match='無效的角色'):
            AdminService.list_all_users(role='INVALID_ROLE')


# ==================== ban_user ====================
class TestBanUser:
    
    def test_ban_user_successfully(self, app_context, monkeypatch):
        """TC-06: 成功封禁用戶"""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.GENERAL_MEMBER
        mock_user.locked_until = None
        
        mock_db_session = MagicMock()
        mock_db_session.get.return_value = mock_user
        monkeypatch.setattr('app.services.admin_service.db.session', mock_db_session)
        
        mock_audit_service = Mock()
        monkeypatch.setattr('app.services.admin_service.audit_service', mock_audit_service)
        
        result = AdminService.ban_user(1, 99, '違規', 30)
        
        assert result.locked_until is not None
        mock_audit_service.log_user_ban.assert_called_once()
    
    def test_ban_user_not_found_raises_error(self, app_context, monkeypatch):
        """TC-07: 用戶不存在拋出錯誤"""
        mock_db_session = MagicMock()
        mock_db_session.get.return_value = None
        monkeypatch.setattr('app.services.admin_service.db.session', mock_db_session)
        
        with pytest.raises(NotFoundError, match='用戶不存在'):
            AdminService.ban_user(999, 99, '違規', 30)
    
    def test_cannot_ban_admin(self, app_context, monkeypatch):
        """TC-08: 不能封禁管理員"""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.ADMIN
        
        mock_db_session = MagicMock()
        mock_db_session.get.return_value = mock_user
        monkeypatch.setattr('app.services.admin_service.db.session', mock_db_session)
        
        with pytest.raises(PermissionDeniedError, match='不能封禁管理員'):
            AdminService.ban_user(1, 99, '違規', 30)


# ==================== unban_user ====================
class TestUnbanUser:
    
    def test_unban_user_successfully(self, app_context, monkeypatch):
        """TC-09: 成功解除封禁"""
        mock_user = Mock(spec=User)
        mock_user.locked_until = datetime.utcnow() + timedelta(days=30)
        mock_user.failed_login_attempts = 5
        
        mock_db_session = MagicMock()
        mock_db_session.get.return_value = mock_user
        monkeypatch.setattr('app.services.admin_service.db.session', mock_db_session)
        
        mock_audit_service = Mock()
        monkeypatch.setattr('app.services.admin_service.audit_service', mock_audit_service)
        
        result = AdminService.unban_user(1, 99)
        
        assert result.locked_until is None
        assert result.failed_login_attempts == 0
        mock_audit_service.log.assert_called_once()
    
    def test_unban_user_not_found_raises_error(self, app_context, monkeypatch):
        """TC-10: 用戶不存在拋出錯誤"""
        mock_db_session = MagicMock()
        mock_db_session.get.return_value = None
        monkeypatch.setattr('app.services.admin_service.db.session', mock_db_session)
        
        with pytest.raises(NotFoundError, match='用戶不存在'):
            AdminService.unban_user(999, 99)


# ==================== list_all_animals ====================
class TestListAllAnimals:
    
    def test_list_animals_with_pagination(self, app_context, monkeypatch):
        """TC-11: 分頁列出動物"""
        mock_animal = Mock(spec=Animal)
        mock_animal.to_dict.return_value = {'animal_id': 1}
        
        mock_pagination = Mock()
        mock_pagination.items = [mock_animal]
        mock_pagination.total = 1
        
        mock_query = Mock()
        mock_query.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination
        monkeypatch.setattr('app.services.admin_service.Animal.query', mock_query)
        
        result = AdminService.list_all_animals(page=1, per_page=20)
        
        assert result['total'] == 1
        assert len(result['animals']) == 1
    
    def test_filter_animals_by_status(self, app_context, monkeypatch):
        """TC-12: 依狀態篩選動物"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        mock_query.filter_by.return_value.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.admin_service.Animal.query', mock_query)
        
        result = AdminService.list_all_animals(status='PUBLISHED')
        
        assert 'animals' in result
    
    def test_include_deleted_animals(self, app_context, monkeypatch):
        """TC-13: 包含已刪除動物"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        
        mock_query = Mock()
        mock_query.order_by.return_value.paginate.return_value = mock_pagination
        monkeypatch.setattr('app.services.admin_service.Animal.query', mock_query)
        
        result = AdminService.list_all_animals(include_deleted=True)
        
        assert 'animals' in result


# ==================== list_all_applications ====================
class TestListAllApplications:
    
    def test_list_applications_with_pagination(self, app_context, monkeypatch):
        """TC-14: 分頁列出申請"""
        mock_app = Mock(spec=Application)
        mock_app.to_dict.return_value = {'application_id': 1}
        
        mock_pagination = Mock()
        mock_pagination.items = [mock_app]
        mock_pagination.total = 1
        
        mock_query = Mock()
        mock_query.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination
        monkeypatch.setattr('app.services.admin_service.Application.query', mock_query)
        
        result = AdminService.list_all_applications(page=1, per_page=20)
        
        assert result['total'] == 1
        assert len(result['applications']) == 1
    
    def test_filter_applications_by_status(self, app_context, monkeypatch):
        """TC-15: 依狀態篩選申請"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        mock_query.filter_by.return_value.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.admin_service.Application.query', mock_query)
        
        result = AdminService.list_all_applications(status='PENDING')
        
        assert 'applications' in result


# ==================== list_audit_logs ====================
class TestListAuditLogs:
    
    def test_list_audit_logs_basic(self, app_context, monkeypatch):
        """TC-16: 基本審計日誌列表"""
        mock_log = Mock(spec=AuditLog)
        mock_log.to_dict.return_value = {'audit_log_id': 1}
        mock_log.actor = None
        
        mock_pagination = Mock()
        mock_pagination.items = [mock_log]
        mock_pagination.total = 1
        mock_pagination.pages = 1
        
        mock_query = Mock()
        mock_query.order_by.return_value.paginate.return_value = mock_pagination
        monkeypatch.setattr('app.services.admin_service.AuditLog.query', mock_query)
        
        result = AdminService.list_audit_logs(page=1, per_page=20)
        
        assert result['total'] == 1
        assert len(result['audit_logs']) == 1
    
    def test_filter_by_actor_id(self, app_context, monkeypatch):
        """TC-17: 依操作者篩選"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.pages = 0
        
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        mock_query.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.admin_service.AuditLog.query', mock_query)
        
        result = AdminService.list_audit_logs(actor_id=10)
        
        assert 'audit_logs' in result
    
    def test_filter_by_action(self, app_context, monkeypatch):
        """TC-18: 依操作類型篩選"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.pages = 0
        
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        mock_query.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.admin_service.AuditLog.query', mock_query)
        
        result = AdminService.list_audit_logs(action='user.login')
        
        assert 'audit_logs' in result
    
    def test_filter_by_date_range(self, app_context, monkeypatch):
        """TC-19: 依日期範圍篩選"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.pages = 0
        
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_filter_result.filter.return_value = mock_filter_result
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        mock_query.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.admin_service.AuditLog.query', mock_query)
        
        result = AdminService.list_audit_logs(
            start_date='2025-01-01',
            end_date='2025-12-31'
        )
        
        assert 'audit_logs' in result
    
    def test_invalid_start_date_format_raises_error(self, app_context, monkeypatch):
        """TC-20: 無效開始日期格式"""
        mock_query = Mock()
        monkeypatch.setattr('app.services.admin_service.AuditLog.query', mock_query)
        
        with pytest.raises(ValidationError, match='start_date格式錯誤'):
            AdminService.list_audit_logs(start_date='invalid-date')
    
    def test_invalid_end_date_format_raises_error(self, app_context, monkeypatch):
        """TC-21: 無效結束日期格式"""
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_query.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.admin_service.AuditLog.query', mock_query)
        
        with pytest.raises(ValidationError, match='end_date格式錯誤'):
            AdminService.list_audit_logs(
                start_date='2025-01-01',
                end_date='invalid-date'
            )
    
    def test_audit_log_with_actor_info(self, app_context, monkeypatch):
        """TC-22: 審計日誌包含操作者資訊"""
        mock_actor = Mock(spec=User)
        mock_actor.user_id = 10
        mock_actor.username = 'admin'
        mock_actor.email = 'admin@test.com'
        mock_actor.role = UserRole.ADMIN
        
        mock_log = Mock(spec=AuditLog)
        mock_log.to_dict.return_value = {'audit_log_id': 1}
        mock_log.actor = mock_actor
        
        mock_pagination = Mock()
        mock_pagination.items = [mock_log]
        mock_pagination.total = 1
        mock_pagination.pages = 1
        
        mock_query = Mock()
        mock_query.order_by.return_value.paginate.return_value = mock_pagination
        monkeypatch.setattr('app.services.admin_service.AuditLog.query', mock_query)
        
        result = AdminService.list_audit_logs()
        
        assert result['audit_logs'][0]['actor']['username'] == 'admin'


# ==================== get_reviewers ====================
class TestGetReviewers:
    
    def test_get_reviewers_list(self, app_context, monkeypatch):
        """TC-23: 取得審核員列表"""
        mock_admin = Mock(spec=User)
        mock_admin.user_id = 1
        mock_admin.username = 'admin'
        mock_admin.email = 'admin@test.com'
        mock_admin.role = UserRole.ADMIN
        mock_admin.primary_shelter_id = None
        
        mock_shelter_member = Mock(spec=User)
        mock_shelter_member.user_id = 2
        mock_shelter_member.username = 'shelter_member'
        mock_shelter_member.email = 'member@test.com'
        mock_shelter_member.role = UserRole.SHELTER_MEMBER
        mock_shelter_member.primary_shelter_id = 10
        
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.all.return_value = [mock_admin, mock_shelter_member]
        mock_query.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.admin_service.User.query', mock_query)
        
        mock_db_or = Mock(return_value=True)
        monkeypatch.setattr('app.services.admin_service.db.or_', mock_db_or)
        
        result = AdminService.get_reviewers()
        
        assert len(result) == 2
        assert result[0]['username'] == 'admin'
        assert result[1]['shelter_id'] == 10
