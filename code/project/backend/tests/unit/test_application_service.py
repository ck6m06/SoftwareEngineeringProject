"""
單元測試：app/services/application_service.py

測試申請服務的所有業務邏輯
目標：100% 測試通過率 + 95%+ 覆蓋率
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from app import create_app
from app.services.application_service import ApplicationService
from app.models.application import Application, ApplicationStatus, ApplicationType
from app.models.user import User, UserRole
from app.models.animal import Animal, AnimalStatus
from app.exceptions import (
    PermissionDeniedError, NotFoundError, ValidationError, ConflictError
)


@pytest.fixture
def app():
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield app


# ==================== list_applications ====================
class TestListApplications:
    
    def test_admin_can_see_all_applications(self, app_context, monkeypatch):
        """TC-01: 管理員可以看到所有申請"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_query = Mock()
        mock_query.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination
        monkeypatch.setattr('app.services.application_service.Application.query', mock_query)
        
        result = ApplicationService.list_applications(
            mock_admin,
            {'page': 1, 'per_page': 20, 'mode': 'all'}
        )
        
        assert result['total'] == 0
        assert 'items' in result
    
    def test_general_member_review_mode(self, app_context, monkeypatch):
        """TC-02: 一般會員審核模式（看自己動物的申請）"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.GENERAL_MEMBER
        mock_user.primary_shelter_id = None
        
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        mock_query.filter_by.return_value.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.application_service.Application.query', mock_query)
        
        # Mock db.session.query for owned animals
        mock_db_session = Mock()
        mock_db_session.query.return_value.filter_by.return_value.all.return_value = []
        
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.application_service.db', mock_db)
        
        result = ApplicationService.list_applications(
            mock_user,
            {'page': 1, 'per_page': 20, 'mode': 'review'}
        )
        
        assert 'items' in result
    
    def test_general_member_my_mode(self, app_context, monkeypatch):
        """TC-03: 一般會員我的申請模式"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.GENERAL_MEMBER
        mock_user.primary_shelter_id = None
        
        mock_app = Mock(spec=Application)
        mock_app.to_dict.return_value = {'application_id': 1}
        
        mock_pagination = Mock()
        mock_pagination.items = [mock_app]  # 必須是 list
        mock_pagination.total = 1
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 1
        
        # Mock Application.query chain
        # Application.query.filter_by(deleted_at=None).filter_by(applicant_id=1).order_by(...).paginate(...)
        mock_query = Mock()
        mock_query_step1 = Mock()
        mock_query_step2 = Mock()
        mock_query_step3 = Mock()
        
        mock_query.filter_by.return_value = mock_query_step1
        mock_query_step1.filter_by.return_value = mock_query_step2
        mock_query_step2.order_by.return_value = mock_query_step3
        mock_query_step3.paginate.return_value = mock_pagination
        
        monkeypatch.setattr('app.services.application_service.Application.query', mock_query)
        
        # Mock db.session.query
        mock_db_session = Mock()
        mock_db_session.query.return_value.filter_by.return_value.all.return_value = []
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.application_service.db', mock_db)
        
        result = ApplicationService.list_applications(
            mock_user,
            {'page': 1, 'per_page': 20, 'mode': 'my'}
        )
        
        assert 'items' in result
    
    def test_shelter_member_includes_shelter_animals(self, app_context, monkeypatch):
        """TC-04: 收容所成員包含收容所動物"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.SHELTER_MEMBER
        mock_user.primary_shelter_id = 10
        
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        mock_query.filter_by.return_value.filter.return_value = mock_filter_result
        monkeypatch.setattr('app.services.application_service.Application.query', mock_query)
        
        # Mock db.session.query for owned and shelter animals
        mock_db_session = Mock()
        mock_db_session.query.return_value.filter_by.return_value.all.return_value = []
        
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.application_service.db', mock_db)
        
        result = ApplicationService.list_applications(
            mock_user,
            {'page': 1, 'per_page': 20, 'mode': 'all'}
        )
        
        assert 'items' in result
    
    def test_filter_by_status(self, app_context, monkeypatch):
        """TC-05: 依狀態篩選"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_query = Mock()
        mock_query.filter_by.return_value.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination
        monkeypatch.setattr('app.services.application_service.Application.query', mock_query)
        
        result = ApplicationService.list_applications(
            mock_admin,
            {'page': 1, 'status': 'PENDING'}
        )
        
        assert 'items' in result
    
    def test_invalid_status_raises_error(self, app_context, monkeypatch):
        """TC-06: 無效狀態拋出錯誤"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        monkeypatch.setattr('app.services.application_service.Application.query', mock_query)
        
        with pytest.raises(ValidationError, match='無效的狀態值'):
            ApplicationService.list_applications(
                mock_admin,
                {'status': 'INVALID_STATUS'}
            )
    
    def test_non_admin_cannot_query_other_user_applications(self, app_context, monkeypatch):
        """TC-07: 非管理員不能查詢其他用戶的申請"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.GENERAL_MEMBER
        mock_user.primary_shelter_id = None
        
        mock_query = Mock()
        monkeypatch.setattr('app.services.application_service.Application.query', mock_query)
        
        # Mock db.session.query
        mock_db_session = Mock()
        mock_db_session.query.return_value.filter_by.return_value.all.return_value = []
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.application_service.db', mock_db)
        
        with pytest.raises(PermissionDeniedError, match='無權限查看其他用戶的申請'):
            ApplicationService.list_applications(
                mock_user,
                {'applicant_id': 999}  # 不是自己的 ID
            )
    
    def test_admin_can_query_specific_applicant(self, app_context, monkeypatch):
        """TC-08: 管理員可以查詢指定申請人"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_query = Mock()
        mock_query.filter_by.return_value.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination
        monkeypatch.setattr('app.services.application_service.Application.query', mock_query)
        
        result = ApplicationService.list_applications(
            mock_admin,
            {'applicant_id': 999}
        )
        
        assert 'items' in result


# ==================== create_application ====================
class TestCreateApplication:
    
    def test_create_application_successfully(self, app_context, monkeypatch):
        """TC-09: 成功創建申請"""
        mock_applicant = Mock(spec=User)
        mock_applicant.user_id = 1
        mock_applicant.role = UserRole.GENERAL_MEMBER
        mock_applicant.username = 'user1'
        mock_applicant.email = 'user@test.com'
        
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 100
        mock_animal.owner_id = 2
        mock_animal.created_by = 2
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.name = 'Lucky'
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        # Mock existing application check
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.filter.return_value.first.return_value = None
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_db_session = MagicMock()
        mock_db_session.execute.return_value.scalar.return_value = 0
        
        mock_db = Mock()
        mock_db.session = mock_db_session
        mock_db.text = Mock(return_value='SELECT MAX(application_id) FROM applications')
        monkeypatch.setattr('app.services.application_service.db', mock_db)
        
        mock_notification_service = Mock()
        monkeypatch.setattr('app.services.application_service.notification_service', mock_notification_service)
        
        data = {
            'animal_id': 100,
            'contact_phone': '0912345678',
            'reason': '喜歡動物'
        }
        
        result = ApplicationService.create_application(mock_applicant, data)
        
        assert result.animal_id == 100
        assert result.applicant_id == 1
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called()
    
    def test_non_general_member_cannot_apply(self, app_context):
        """TC-10: 非一般會員不能申請"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        with pytest.raises(PermissionDeniedError, match='只有一般會員可提出領養申請'):
            ApplicationService.create_application(mock_admin, {'animal_id': 100})
    
    def test_missing_animal_id_raises_error(self, app_context):
        """TC-11: 缺少 animal_id"""
        mock_applicant = Mock(spec=User)
        mock_applicant.role = UserRole.GENERAL_MEMBER
        
        with pytest.raises(ValidationError, match='缺少必填欄位: animal_id'):
            ApplicationService.create_application(mock_applicant, {})
    
    def test_animal_not_found_raises_error(self, app_context, monkeypatch):
        """TC-12: 動物不存在"""
        mock_applicant = Mock(spec=User)
        mock_applicant.role = UserRole.GENERAL_MEMBER
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        with pytest.raises(NotFoundError, match='動物不存在'):
            ApplicationService.create_application(mock_applicant, {'animal_id': 999})
    
    def test_cannot_apply_adopted_animal(self, app_context, monkeypatch):
        """TC-13: 不能申請已領養動物"""
        mock_applicant = Mock(spec=User)
        mock_applicant.role = UserRole.GENERAL_MEMBER
        
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.ADOPTED
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        with pytest.raises(ValidationError, match='此動物已被領養'):
            ApplicationService.create_application(mock_applicant, {'animal_id': 100})
    
    def test_cannot_apply_unpublished_animal(self, app_context, monkeypatch):
        """TC-14: 不能申請未發布動物"""
        mock_applicant = Mock(spec=User)
        mock_applicant.role = UserRole.GENERAL_MEMBER
        
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.DRAFT
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        with pytest.raises(ValidationError, match='此動物目前無法申請領養'):
            ApplicationService.create_application(mock_applicant, {'animal_id': 100})
    
    def test_cannot_apply_own_animal(self, app_context, monkeypatch):
        """TC-15: 不能申請自己的動物"""
        mock_applicant = Mock(spec=User)
        mock_applicant.user_id = 1
        mock_applicant.role = UserRole.GENERAL_MEMBER
        
        mock_animal = Mock(spec=Animal)
        mock_animal.owner_id = 1  # 同一個人
        mock_animal.status = AnimalStatus.PUBLISHED
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        with pytest.raises(ValidationError, match='您不能申請自己刊登的動物'):
            ApplicationService.create_application(mock_applicant, {'animal_id': 100})
    
    def test_duplicate_application_raises_conflict(self, app_context, monkeypatch):
        """TC-16: 重複申請拋出衝突錯誤"""
        mock_applicant = Mock(spec=User)
        mock_applicant.user_id = 1
        mock_applicant.role = UserRole.GENERAL_MEMBER
        
        mock_animal = Mock(spec=Animal)
        mock_animal.owner_id = 2
        mock_animal.created_by = 2
        mock_animal.status = AnimalStatus.PUBLISHED
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        # Mock existing application
        mock_existing_app = Mock(spec=Application)
        mock_existing_app.status = ApplicationStatus.PENDING
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.filter.return_value.first.return_value = mock_existing_app
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        with pytest.raises(ConflictError, match='您已對此動物提交申請'):
            ApplicationService.create_application(mock_applicant, {'animal_id': 100})
    
    def test_idempotency_key_returns_existing_application(self, app_context, monkeypatch):
        """TC-17: 冪等性鍵值返回已存在的申請"""
        mock_applicant = Mock(spec=User)
        mock_applicant.user_id = 1
        mock_applicant.role = UserRole.GENERAL_MEMBER
        
        mock_animal = Mock(spec=Animal)
        mock_animal.owner_id = 2
        mock_animal.created_by = 2
        mock_animal.status = AnimalStatus.PUBLISHED
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        # Mock existing application with idempotency key
        mock_existing_app = Mock(spec=Application)
        mock_existing_app.application_id = 123
        
        # 冪等性檢查： Application.query.filter_by(idempotency_key=..., applicant_id=...).first()
        # 這是兩個參數在同一個 filter_by 中
        mock_filter1 = Mock()
        mock_filter1.first.return_value = mock_existing_app
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value = mock_filter1
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        result = ApplicationService.create_application(
            mock_applicant,
            {'animal_id': 100},
            idempotency_key='unique-key-123'
        )
        
        # 驗證返回的是同一個對象（用 identity check）
        assert result is mock_existing_app


# ==================== review_application ====================
class TestReviewApplication:
    
    def test_approve_application_successfully(self, app_context, monkeypatch):
        """TC-18: 成功批准申請"""
        mock_reviewer = Mock(spec=User)
        mock_reviewer.user_id = 2
        mock_reviewer.role = UserRole.GENERAL_MEMBER
        
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.PUBLISHED
        
        mock_application = Mock(spec=Application)
        mock_application.application_id = 1
        mock_application.status = ApplicationStatus.PENDING
        mock_application.version = 1
        mock_application.animal = mock_animal
        mock_application.applicant = None
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_permission_service = Mock()
        mock_permission_service.can_review_application.return_value = True
        monkeypatch.setattr('app.services.application_service.permission_service', mock_permission_service)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.application_service.db.session', mock_db_session)
        
        mock_audit_service = Mock()
        monkeypatch.setattr('app.services.application_service.audit_service', mock_audit_service)
        
        mock_notification_service = Mock()
        monkeypatch.setattr('app.services.application_service.notification_service', mock_notification_service)
        
        result = ApplicationService.review_application(1, mock_reviewer, 'approve')
        
        assert result.status == ApplicationStatus.APPROVED
        assert mock_animal.status == AnimalStatus.ADOPTED
        mock_db_session.commit.assert_called()
    
    def test_reject_application_successfully(self, app_context, monkeypatch):
        """TC-19: 成功拒絕申請"""
        mock_reviewer = Mock(spec=User)
        mock_reviewer.user_id = 2
        mock_reviewer.role = UserRole.GENERAL_MEMBER
        
        mock_application = Mock(spec=Application)
        mock_application.application_id = 1
        mock_application.status = ApplicationStatus.PENDING
        mock_application.version = 1
        mock_application.animal = None
        mock_application.applicant = None
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_permission_service = Mock()
        mock_permission_service.can_review_application.return_value = True
        monkeypatch.setattr('app.services.application_service.permission_service', mock_permission_service)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.application_service.db.session', mock_db_session)
        
        mock_audit_service = Mock()
        monkeypatch.setattr('app.services.application_service.audit_service', mock_audit_service)
        
        mock_notification_service = Mock()
        monkeypatch.setattr('app.services.application_service.notification_service', mock_notification_service)
        
        result = ApplicationService.review_application(1, mock_reviewer, 'reject', 'not suitable')
        
        assert result.status == ApplicationStatus.REJECTED
        assert result.review_notes == 'not suitable'
    
    def test_application_not_found_raises_error(self, app_context, monkeypatch):
        """TC-20: 申請不存在"""
        mock_reviewer = Mock(spec=User)
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        with pytest.raises(NotFoundError, match='申請不存在'):
            ApplicationService.review_application(999, mock_reviewer, 'approve')
    
    def test_no_permission_to_review_raises_error(self, app_context, monkeypatch):
        """TC-21: 無權限審核"""
        mock_reviewer = Mock(spec=User)
        mock_reviewer.role = UserRole.GENERAL_MEMBER
        
        mock_application = Mock(spec=Application)
        mock_application.status = ApplicationStatus.PENDING
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_permission_service = Mock()
        mock_permission_service.can_review_application.return_value = False
        monkeypatch.setattr('app.services.application_service.permission_service', mock_permission_service)
        
        with pytest.raises(PermissionDeniedError):
            ApplicationService.review_application(1, mock_reviewer, 'approve')
    
    def test_admin_cannot_review_applications(self, app_context, monkeypatch):
        """TC-22: 管理員不能審核申請"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_application = Mock(spec=Application)
        mock_application.status = ApplicationStatus.PENDING
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_permission_service = Mock()
        mock_permission_service.can_review_application.return_value = False
        monkeypatch.setattr('app.services.application_service.permission_service', mock_permission_service)
        
        with pytest.raises(PermissionDeniedError, match='領養申請應由送養人或收容所成員審核'):
            ApplicationService.review_application(1, mock_admin, 'approve')
    
    def test_invalid_action_raises_error(self, app_context, monkeypatch):
        """TC-23: 無效操作"""
        mock_reviewer = Mock(spec=User)
        
        mock_application = Mock(spec=Application)
        mock_application.status = ApplicationStatus.PENDING
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_permission_service = Mock()
        mock_permission_service.can_review_application.return_value = True
        monkeypatch.setattr('app.services.application_service.permission_service', mock_permission_service)
        
        with pytest.raises(ValidationError, match='action 必須為 approve 或 reject'):
            ApplicationService.review_application(1, mock_reviewer, 'invalid_action')
    
    def test_cannot_review_non_pending_application(self, app_context, monkeypatch):
        """TC-24: 不能審核非待審核申請"""
        mock_reviewer = Mock(spec=User)
        
        mock_application = Mock(spec=Application)
        mock_application.status = ApplicationStatus.APPROVED  # 已批准
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_permission_service = Mock()
        mock_permission_service.can_review_application.return_value = True
        monkeypatch.setattr('app.services.application_service.permission_service', mock_permission_service)
        
        with pytest.raises(ValidationError, match='此申請無法審核'):
            ApplicationService.review_application(1, mock_reviewer, 'approve')
    
    def test_optimistic_lock_conflict_raises_error(self, app_context, monkeypatch):
        """TC-25: 樂觀鎖衝突"""
        mock_reviewer = Mock(spec=User)
        
        mock_application = Mock(spec=Application)
        mock_application.status = ApplicationStatus.PENDING
        mock_application.version = 2  # 版本號已變更
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_permission_service = Mock()
        mock_permission_service.can_review_application.return_value = True
        monkeypatch.setattr('app.services.application_service.permission_service', mock_permission_service)
        
        with pytest.raises(ConflictError, match='申請已被其他人修改'):
            ApplicationService.review_application(1, mock_reviewer, 'approve', expected_version=1)


# ==================== withdraw_application ====================
class TestWithdrawApplication:
    
    def test_withdraw_application_successfully(self, app_context, monkeypatch):
        """TC-26: 成功撤回申請"""
        mock_applicant = Mock(spec=User)
        mock_applicant.user_id = 1
        
        mock_application = Mock(spec=Application)
        mock_application.status = ApplicationStatus.PENDING
        mock_application.version = 1
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.application_service.db.session', mock_db_session)
        
        result = ApplicationService.withdraw_application(1, mock_applicant)
        
        assert result.status == ApplicationStatus.WITHDRAWN
        assert result.version == 2
    
    def test_cannot_withdraw_other_user_application(self, app_context, monkeypatch):
        """TC-27: 不能撤回其他人的申請"""
        mock_applicant = Mock(spec=User)
        mock_applicant.user_id = 1
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        with pytest.raises(NotFoundError, match='申請不存在或無權限'):
            ApplicationService.withdraw_application(1, mock_applicant)
    
    def test_cannot_withdraw_approved_application(self, app_context, monkeypatch):
        """TC-28: 不能撤回已批准申請"""
        mock_applicant = Mock(spec=User)
        mock_applicant.user_id = 1
        
        mock_application = Mock(spec=Application)
        mock_application.status = ApplicationStatus.APPROVED
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        with pytest.raises(ValidationError, match='此申請無法撤回'):
            ApplicationService.withdraw_application(1, mock_applicant)


# ==================== assign_application ====================
class TestAssignApplication:
    
    def test_admin_can_assign_application(self, app_context, monkeypatch):
        """TC-29: 管理員可以指派申請"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_assignee = Mock(spec=User)
        mock_assignee.user_id = 5
        mock_assignee.username = 'reviewer1'
        mock_assignee.email = 'reviewer@test.com'
        
        mock_application = Mock(spec=Application)
        mock_application.version = 1
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_user_query = Mock()
        mock_user_query.get.return_value = mock_assignee
        monkeypatch.setattr('app.services.application_service.User.query', mock_user_query)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.application_service.db.session', mock_db_session)
        
        mock_notification_service = Mock()
        monkeypatch.setattr('app.services.application_service.notification_service', mock_notification_service)
        
        result = ApplicationService.assign_application(1, mock_admin, 5)
        
        assert result.assignee_id == 5
        assert result.status == ApplicationStatus.UNDER_REVIEW
    
    def test_non_admin_cannot_assign(self, app_context):
        """TC-30: 非管理員不能指派"""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.GENERAL_MEMBER
        
        with pytest.raises(PermissionDeniedError, match='無權限指派申請'):
            ApplicationService.assign_application(1, mock_user, 5)
    
    def test_assign_to_invalid_assignee_raises_error(self, app_context, monkeypatch):
        """TC-31: 指派給無效受理人"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_application = Mock(spec=Application)
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_user_query = Mock()
        mock_user_query.get.return_value = None
        monkeypatch.setattr('app.services.application_service.User.query', mock_user_query)
        
        with pytest.raises(ValidationError, match='無效的受理人'):
            ApplicationService.assign_application(1, mock_admin, 999)


# ==================== 補充測試：提高覆蓋率 ====================
class TestAdditionalCoverage:
    
    def test_admin_query_specific_applicant_id(self, app_context, monkeypatch):
        """TC-32: 管理員查詢指定申請人的申請"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        # filter_by(deleted_at=None).filter_by(applicant_id=999).order_by().paginate()
        mock_query = Mock()
        mock_step1 = Mock()
        mock_step2 = Mock()
        mock_step3 = Mock()
        mock_query.filter_by.return_value = mock_step1
        mock_step1.filter_by.return_value = mock_step2
        mock_step2.order_by.return_value = mock_step3
        mock_step3.paginate.return_value = mock_pagination
        
        monkeypatch.setattr('app.services.application_service.Application.query', mock_query)
        
        result = ApplicationService.list_applications(
            mock_admin,
            {'applicant_id': 999}
        )
        
        assert 'items' in result
    
    def test_list_with_animal_id_filter(self, app_context, monkeypatch):
        """TC-33: 用 animal_id 過濾申請"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        # filter_by(deleted_at=None).filter_by(animal_id=100).order_by().paginate()
        mock_query = Mock()
        mock_step1 = Mock()
        mock_step2 = Mock()
        mock_step3 = Mock()
        mock_query.filter_by.return_value = mock_step1
        mock_step1.filter_by.return_value = mock_step2
        mock_step2.order_by.return_value = mock_step3
        mock_step3.paginate.return_value = mock_pagination
        
        monkeypatch.setattr('app.services.application_service.Application.query', mock_query)
        
        result = ApplicationService.list_applications(
            mock_admin,
            {'animal_id': 100}
        )
        
        assert 'items' in result
    
    def test_pending_application_conflict(self, app_context, monkeypatch):
        """TC-34: 動物有待審核申請時拋出衝突錯誤"""
        mock_applicant = Mock(spec=User)
        mock_applicant.user_id = 1
        mock_applicant.role = UserRole.GENERAL_MEMBER
        
        mock_animal = Mock(spec=Animal)
        mock_animal.owner_id = 2
        mock_animal.created_by = 2
        mock_animal.status = AnimalStatus.PUBLISHED
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        # Mock no existing application from same applicant
        # Application.query.filter_by(...).filter(...).first()
        mock_filter_step2 = Mock()
        mock_filter_step2.first.return_value = None
        mock_filter_step1 = Mock()
        mock_filter_step1.filter.return_value = mock_filter_step2
        
        # Mock pending application exists from someone else
        # Application.query.filter_by(...).filter(...).first()
        mock_pending_app = Mock(spec=Application)
        mock_pending_step2 = Mock()
        mock_pending_step2.first.return_value = mock_pending_app
        mock_pending_step1 = Mock()
        mock_pending_step1.filter.return_value = mock_pending_step2
        
        mock_app_query = Mock()
        # 第一次調用返回 no existing (line 200), 第二次調用返回 pending (line 216)
        mock_app_query.filter_by.side_effect = [mock_filter_step1, mock_pending_step1]
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        with pytest.raises(ConflictError, match='此動物目前有待審核的申請'):
            ApplicationService.create_application(mock_applicant, {'animal_id': 100})
    
    @patch('app.services.application_service.notification_service')
    def test_notification_failure_does_not_break_create(self, mock_notification_service, app_context, monkeypatch):
        """TC-35: 通知失敗不影響申請創建"""
        mock_applicant = Mock(spec=User)
        mock_applicant.user_id = 1
        mock_applicant.role = UserRole.GENERAL_MEMBER
        mock_applicant.username = 'user1'
        mock_applicant.email = 'user@test.com'
        
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 100
        mock_animal.owner_id = 2
        mock_animal.created_by = 2
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.name = 'Lucky'
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        # Mock no existing applications
        # First: filter_by().filter().first() -> None
        mock_filter1_step2 = Mock()
        mock_filter1_step2.first.return_value = None
        mock_filter1 = Mock()
        mock_filter1.filter.return_value = mock_filter1_step2
        
        # Second: filter_by().filter().first() -> None
        mock_filter2_step2 = Mock()
        mock_filter2_step2.first.return_value = None
        mock_filter2 = Mock()
        mock_filter2.filter.return_value = mock_filter2_step2
        
        mock_app_query = Mock()
        mock_app_query.filter_by.side_effect = [mock_filter1, mock_filter2]
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_db_session = MagicMock()
        mock_db_session.execute.return_value.scalar.return_value = 0
        mock_db = Mock()
        mock_db.session = mock_db_session
        mock_db.text = Mock(return_value='SELECT MAX(application_id) FROM applications')
        monkeypatch.setattr('app.services.application_service.db', mock_db)
        
        # Mock notification failure
        mock_notification_service.notify_application_submitted.side_effect = Exception('通知服務錯誤')
        
        result = ApplicationService.create_application(
            mock_applicant,
            {'animal_id': 100, 'contact_phone': '0912345678', 'reason': '喜歡動物'}
        )
        
        assert result.animal_id == 100
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called()
    
    @patch('app.services.application_service.notification_service')
    @patch('app.services.application_service.audit_service')
    def test_notification_failure_does_not_break_review(self, mock_audit_service, mock_notification_service, app_context, monkeypatch):
        """TC-36: 通知失敗不影響審核"""
        mock_reviewer = Mock(spec=User)
        mock_reviewer.user_id = 2
        mock_reviewer.role = UserRole.GENERAL_MEMBER
        
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 100
        mock_animal.owner_id = 2  # reviewer 是 owner
        mock_animal.shelter_id = None
        mock_animal.status = AnimalStatus.PUBLISHED
        
        mock_application = Mock(spec=Application)
        mock_application.application_id = 1
        mock_application.animal_id = 100
        mock_application.applicant_id = 1
        mock_application.status = ApplicationStatus.PENDING
        mock_application.version = 1
        mock_application.animal = mock_animal
        mock_application.applicant = Mock(email='user@test.com')
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        # Mock Animal.query.get to return the animal
        mock_animal_query = Mock()
        mock_animal_query.get.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        mock_db_session = Mock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.application_service.db', mock_db)
        
        # Mock audit service logs
        mock_audit_service.log_application_reviewed.return_value = None
        
        # Mock notification failure
        mock_notification_service.notify_application_reviewed.side_effect = Exception('通知錯誤')
        
        result = ApplicationService.review_application(
            1, mock_reviewer, 'approve', 'OK', 1
        )
        
        assert result.status == ApplicationStatus.APPROVED
        mock_db_session.commit.assert_called()
    
    @patch('app.services.application_service.notification_service')
    def test_notification_failure_does_not_break_assign(self, mock_notification_service, app_context, monkeypatch):
        """TC-37: 通知失敗不影響指派"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_application = Mock(spec=Application)
        mock_application.version = 1
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        mock_assignee = Mock(spec=User)
        mock_assignee.username = 'reviewer1'
        mock_user_query = Mock()
        mock_user_query.get.return_value = mock_assignee
        monkeypatch.setattr('app.services.application_service.User.query', mock_user_query)
        
        mock_db_session = Mock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.application_service.db', mock_db)
        
        # Mock notification failure
        mock_notification_service.notify_application_under_review.side_effect = Exception('通知錯誤')
        
        result = ApplicationService.assign_application(1, mock_admin, 5)
        
        assert result.status == ApplicationStatus.UNDER_REVIEW
        mock_db_session.commit.assert_called()
    
    @patch('app.services.application_service.notification_service')
    @patch('app.services.application_service.audit_service')
    @patch('app.tasks.email_tasks.send_application_notification_email_task')
    def test_review_with_email_notification_owner(self, mock_email_task, mock_audit_service, mock_notification_service, app_context, monkeypatch):
        """TC-38: 審核通過且發送 email 通知（owner 類型）"""
        mock_reviewer = Mock(spec=User)
        mock_reviewer.user_id = 2
        mock_reviewer.role = UserRole.GENERAL_MEMBER
        
        mock_owner = Mock(spec=User)
        mock_owner.username = 'owner1'
        mock_owner.email = 'owner@test.com'
        mock_owner.phone_number = '0911111111'
        mock_owner.first_name = 'John'
        mock_owner.last_name = 'Doe'
        
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 100
        mock_animal.owner_id = 2  # reviewer is owner
        mock_animal.shelter_id = None
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.name = 'Lucky'
        
        mock_applicant = Mock(spec=User)
        mock_applicant.email = 'applicant@test.com'
        
        mock_application = Mock(spec=Application)
        mock_application.application_id = 1
        mock_application.animal_id = 100
        mock_application.applicant_id = 1
        mock_application.status = ApplicationStatus.PENDING
        mock_application.version = 1
        mock_application.animal = mock_animal
        mock_application.applicant = mock_applicant
        mock_application.review_notes = 'Good'
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        # Mock Animal.query.get
        mock_animal_query = Mock()
        mock_animal_query.get.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        # Mock User.query.get for owner
        mock_user_query = Mock()
        mock_user_query.get.return_value = mock_owner
        monkeypatch.setattr('app.services.application_service.User.query', mock_user_query)
        
        mock_db_session = Mock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.application_service.db', mock_db)
        
        mock_audit_service.log_application_reviewed.return_value = None
        mock_notification_service.notify_application_reviewed.return_value = None
        
        result = ApplicationService.review_application(
            1, mock_reviewer, 'approve', 'Good', 1
        )
        
        assert result.status == ApplicationStatus.APPROVED
        # 驗證 email task 被調用
        mock_email_task.delay.assert_called_once()
        call_args = mock_email_task.delay.call_args[0]
        assert call_args[0] == 'applicant@test.com'
        assert call_args[1] == 'Lucky'
        assert call_args[2] == 'approved'
    
    @patch('app.services.application_service.notification_service')
    @patch('app.services.application_service.audit_service')
    @patch('app.tasks.email_tasks.send_application_notification_email_task')
    def test_review_with_email_notification_shelter(self, mock_email_task, mock_audit_service, mock_notification_service, app_context, monkeypatch):
        """TC-39: 審核通過且發送 email 通知（shelter 類型）"""
        mock_reviewer = Mock(spec=User)
        mock_reviewer.user_id = 2
        mock_reviewer.role = UserRole.SHELTER_MEMBER
        mock_reviewer.primary_shelter_id = 10
        
        mock_shelter = Mock()
        mock_shelter.name = 'Happy Shelter'
        mock_shelter.contact_email = 'shelter@test.com'
        mock_shelter.contact_phone = '0922222222'
        
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 100
        mock_animal.owner_id = None
        mock_animal.shelter_id = 10  # belongs to shelter
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.name = 'Buddy'
        
        mock_applicant = Mock(spec=User)
        mock_applicant.email = 'applicant@test.com'
        
        mock_application = Mock(spec=Application)
        mock_application.application_id = 1
        mock_application.animal_id = 100
        mock_application.applicant_id = 1
        mock_application.status = ApplicationStatus.PENDING
        mock_application.version = 1
        mock_application.animal = mock_animal
        mock_application.applicant = mock_applicant
        mock_application.review_notes = 'Great'
        
        mock_app_query = Mock()
        mock_app_query.filter_by.return_value.first.return_value = mock_application
        monkeypatch.setattr('app.services.application_service.Application.query', mock_app_query)
        
        # Mock Animal.query.get
        mock_animal_query = Mock()
        mock_animal_query.get.return_value = mock_animal
        monkeypatch.setattr('app.services.application_service.Animal.query', mock_animal_query)
        
        # Mock Shelter import and query
        mock_shelter_class = Mock()
        mock_shelter_query = Mock()
        mock_shelter_query.get.return_value = mock_shelter
        mock_shelter_class.query = mock_shelter_query
        
        mock_db_session = Mock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.application_service.db', mock_db)
        
        mock_audit_service.log_application_reviewed.return_value = None
        mock_notification_service.notify_application_reviewed.return_value = None
        
        with patch.dict('sys.modules', {'app.models.shelter': Mock(Shelter=mock_shelter_class)}):
            result = ApplicationService.review_application(
                1, mock_reviewer, 'approve', 'Great', 1
            )
            
            assert result.status == ApplicationStatus.APPROVED
            # 驗證 email task 被調用
            mock_email_task.delay.assert_called_once()
            call_args = mock_email_task.delay.call_args[0]
            assert call_args[0] == 'applicant@test.com'
            assert call_args[1] == 'Buddy'
            assert call_args[2] == 'approved'





