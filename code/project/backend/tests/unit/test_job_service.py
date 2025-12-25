"""
單元測試：app/services/job_service.py

測試任務服務的所有業務邏輯
目標：100% 測試通過率 + 95%+ 覆蓋率
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from app import create_app
from app.services.job_service import JobService
from app.models.others import Job, JobStatus
from app.models.user import User, UserRole
from app.exceptions import (
    PermissionDeniedError, NotFoundError, ValidationError
)


@pytest.fixture
def app():
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield app


# ==================== list_jobs ====================
class TestListJobs:
    
    def test_admin_can_list_all_jobs(self, app_context, monkeypatch):
        """TC-01: 管理員可以查看所有任務"""
        mock_admin = Mock(spec=User)
        mock_admin.user_id = 1
        mock_admin.role = UserRole.ADMIN
        
        mock_db_session = Mock()
        mock_db_session.get.return_value = mock_admin
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        mock_pagination = Mock()
        mock_pagination.total = 10
        mock_pagination.items = []
        
        mock_query = Mock()
        mock_query.options.return_value.order_by.return_value.paginate.return_value = mock_pagination
        monkeypatch.setattr('app.services.job_service.Job.query', mock_query)
        
        result = JobService.list_jobs(user_id=1, filters={'page': 1, 'per_page': 20})
        
        assert 'total' in result
        assert result['total'] == 10
        assert 'jobs' in result
    
    def test_regular_user_can_only_see_own_jobs(self, app_context, monkeypatch):
        """TC-02: 普通用戶只能看到自己的任務"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 2
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_db_session = Mock()
        mock_db_session.get.return_value = mock_user
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        mock_pagination = Mock()
        mock_pagination.total = 3
        mock_pagination.items = []
        
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.options.return_value.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.job_service.Job.query', mock_query)
        
        result = JobService.list_jobs(user_id=2, filters={})
        
        assert result['total'] == 3
    
    def test_filter_by_type(self, app_context, monkeypatch):
        """TC-03: 按類型過濾任務"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_db_session = Mock()
        mock_db_session.get.return_value = mock_admin
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        mock_pagination = Mock()
        mock_pagination.total = 5
        mock_pagination.items = []
        
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.options.return_value.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.job_service.Job.query', mock_query)
        
        result = JobService.list_jobs(user_id=1, filters={'type': 'user_data_deletion'})
        
        assert result['total'] == 5
    
    def test_invalid_status_filter_raises_error(self, app_context, monkeypatch):
        """TC-04: 無效的狀態過濾"""
        mock_admin = Mock(spec=User)
        mock_admin.user_id = 1
        mock_admin.role = UserRole.ADMIN
        
        mock_db_session = Mock()
        mock_db_session.get.return_value = mock_admin
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        # Mock the query chain
        mock_pagination = Mock()
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_options_result = Mock()
        
        def filter_side_effect(*args, **kwargs):
            # Check if filtering by status with invalid value
            raise ValueError('Invalid status')
        
        mock_options_result.filter = Mock(side_effect=filter_side_effect)
        
        mock_query = Mock()
        mock_query.options.return_value = mock_options_result
        monkeypatch.setattr('app.services.job_service.Job.query', mock_query)
        
        with pytest.raises(ValidationError, match='無效的狀態'):
            JobService.list_jobs(user_id=1, filters={'status': 'invalid_status'})
    
    def test_admin_filter_by_created_by(self, app_context, monkeypatch):
        """TC-04a: 管理員可以按創建者過濾"""
        mock_admin = Mock(spec=User)
        mock_admin.user_id = 1
        mock_admin.role = UserRole.ADMIN
        
        mock_db_session = Mock()
        mock_db_session.get.return_value = mock_admin
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        mock_pagination = Mock()
        mock_pagination.total = 2
        mock_pagination.items = []
        
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.options.return_value.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.job_service.Job.query', mock_query)
        
        result = JobService.list_jobs(user_id=1, filters={'created_by': 2})
        
        assert result['total'] == 2


# ==================== get_job ====================
class TestGetJob:
    
    def test_admin_can_get_any_job(self, app_context, monkeypatch):
        """TC-05: 管理員可以查看任何任務"""
        mock_admin = Mock(spec=User)
        mock_admin.user_id = 1
        mock_admin.role = UserRole.ADMIN
        
        mock_job = Mock(spec=Job)
        mock_job.job_id = 100
        mock_job.created_by = 2
        
        mock_db_session = Mock()
        mock_db_session.get.side_effect = [mock_job, mock_admin]
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        result = JobService.get_job(job_id=100, user_id=1)
        
        assert result is not None
        assert result.job_id == 100
    
    def test_user_can_get_own_job(self, app_context, monkeypatch):
        """TC-06: 用戶可以查看自己的任務"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 2
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_job = Mock(spec=Job)
        mock_job.job_id = 100
        mock_job.created_by = 2
        
        mock_db_session = Mock()
        mock_db_session.get.side_effect = [mock_job, mock_user]
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        result = JobService.get_job(job_id=100, user_id=2)
        
        assert result is not None
    
    def test_user_cannot_get_others_job(self, app_context, monkeypatch):
        """TC-07: 用戶不能查看他人的任務"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 2
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_job = Mock(spec=Job)
        mock_job.job_id = 100
        mock_job.created_by = 3
        
        mock_db_session = Mock()
        mock_db_session.get.side_effect = [mock_job, mock_user]
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        with pytest.raises(PermissionDeniedError, match='無權限查看此任務'):
            JobService.get_job(job_id=100, user_id=2)
    
    def test_job_not_found_raises_error(self, app_context, monkeypatch):
        """TC-08: 任務不存在"""
        mock_db_session = Mock()
        mock_db_session.get.return_value = None
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        with pytest.raises(NotFoundError, match='任務不存在'):
            JobService.get_job(job_id=999, user_id=1)


# ==================== retry_job ====================
class TestRetryJob:
    
    def test_retry_failed_job_successfully(self, app_context, monkeypatch):
        """TC-09: 成功重試失敗的任務"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_job = Mock(spec=Job)
        mock_job.job_id = 100
        mock_job.created_by = 1
        mock_job.status = JobStatus.FAILED
        mock_job.attempts = 1
        
        mock_db_session = Mock()
        mock_db_session.get.side_effect = [mock_job, mock_user]
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        result = JobService.retry_job(job_id=100, user_id=1)
        
        assert result.status == JobStatus.PENDING
        assert result.attempts == 2
        mock_db_session.commit.assert_called_once()
    
    def test_cannot_retry_non_failed_job(self, app_context, monkeypatch):
        """TC-10: 不能重試非失敗的任務"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_job = Mock(spec=Job)
        mock_job.job_id = 100
        mock_job.created_by = 1
        mock_job.status = JobStatus.SUCCEEDED
        
        mock_db_session = Mock()
        mock_db_session.get.side_effect = [mock_job, mock_user]
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        with pytest.raises(ValidationError, match='只能重試失敗的任務'):
            JobService.retry_job(job_id=100, user_id=1)


# ==================== cancel_job ====================
class TestCancelJob:
    
    def test_cancel_pending_job_successfully(self, app_context, monkeypatch):
        """TC-11: 成功取消待處理的任務"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_job = Mock(spec=Job)
        mock_job.job_id = 100
        mock_job.created_by = 1
        mock_job.status = JobStatus.PENDING
        
        mock_db_session = Mock()
        mock_db_session.get.side_effect = [mock_job, mock_user]
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        result = JobService.cancel_job(job_id=100, user_id=1)
        
        assert result.status == JobStatus.FAILED
        assert result.result_summary == {'error': '任務已被用戶取消'}
        mock_db_session.commit.assert_called_once()
    
    def test_cannot_cancel_completed_job(self, app_context, monkeypatch):
        """TC-12: 不能取消已完成的任務"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_job = Mock(spec=Job)
        mock_job.job_id = 100
        mock_job.created_by = 1
        mock_job.status = JobStatus.SUCCEEDED
        
        mock_db_session = Mock()
        mock_db_session.get.side_effect = [mock_job, mock_user]
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        with pytest.raises(ValidationError, match='只能取消待處理或運行中的任務'):
            JobService.cancel_job(job_id=100, user_id=1)


# ==================== approve_job ====================
class TestApproveJob:
    
    @patch('app.services.notification_service.notification_service')
    @patch('app.services.audit_service.audit_service')
    def test_approve_job_successfully(self, mock_audit_service, mock_notification_service, app_context, monkeypatch):
        """TC-13: 管理員成功核准任務"""
        mock_admin = Mock(spec=User)
        mock_admin.user_id = 1
        mock_admin.role = UserRole.ADMIN
        
        mock_job = Mock(spec=Job)
        mock_job.job_id = 100
        mock_job.status = JobStatus.PENDING
        mock_job.type = 'user_data_deletion'
        mock_job.payload = {'user_id': 5}
        
        mock_target_user = Mock(spec=User)
        
        mock_db_session = Mock()
        mock_db_session.get.side_effect = [mock_admin, mock_job, mock_target_user]
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        mock_audit_service.log.return_value = None
        mock_notification_service.notify_job_completed.return_value = None
        
        result = JobService.approve_job(job_id=100, admin_id=1, notes='Approved')
        
        assert result.status == JobStatus.SUCCEEDED
        mock_db_session.commit.assert_called_once()
    
    def test_non_admin_cannot_approve(self, app_context, monkeypatch):
        """TC-14: 非管理員不能核准任務"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 2
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_db_session = Mock()
        mock_db_session.get.return_value = mock_user
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        with pytest.raises(PermissionDeniedError, match='僅管理員可執行此操作'):
            JobService.approve_job(job_id=100, admin_id=2)
    
    def test_cannot_approve_non_pending_job(self, app_context, monkeypatch):
        """TC-15: 不能核准非待處理的任務"""
        mock_admin = Mock(spec=User)
        mock_admin.user_id = 1
        mock_admin.role = UserRole.ADMIN
        
        mock_job = Mock(spec=Job)
        mock_job.status = JobStatus.SUCCEEDED
        
        mock_db_session = Mock()
        mock_db_session.get.side_effect = [mock_admin, mock_job]
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        with pytest.raises(ValidationError, match='只能核准待處理的任務'):
            JobService.approve_job(job_id=100, admin_id=1)


# ==================== reject_job ====================
class TestRejectJob:
    
    @patch('app.services.notification_service.notification_service')
    @patch('app.services.audit_service.audit_service')
    def test_reject_job_successfully(self, mock_audit_service, mock_notification_service, app_context, monkeypatch):
        """TC-16: 管理員成功拒絕任務"""
        mock_admin = Mock(spec=User)
        mock_admin.user_id = 1
        mock_admin.role = UserRole.ADMIN
        
        mock_job = Mock(spec=Job)
        mock_job.job_id = 100
        mock_job.status = JobStatus.PENDING
        
        mock_db_session = Mock()
        mock_db_session.get.side_effect = [mock_admin, mock_job]
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        mock_audit_service.log.return_value = None
        mock_notification_service.notify_job_completed.return_value = None
        
        result = JobService.reject_job(job_id=100, admin_id=1, reason='Not valid')
        
        assert result.status == JobStatus.FAILED
        assert result.result_summary['reason'] == 'Not valid'
        mock_db_session.commit.assert_called_once()
    
    def test_non_admin_cannot_reject(self, app_context, monkeypatch):
        """TC-17: 非管理員不能拒絕任務"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 2
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_db_session = Mock()
        mock_db_session.get.return_value = mock_user
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.job_service.db', mock_db)
        
        with pytest.raises(PermissionDeniedError, match='僅管理員可執行此操作'):
            JobService.reject_job(job_id=100, admin_id=2)
