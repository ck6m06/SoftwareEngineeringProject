"""
單元測試：app/services/permission_service.py

測試權限服務的所有業務邏輯
目標：100% 測試通過率 + 95%+ 覆蓋率
"""
import pytest
from unittest.mock import Mock

from app import create_app
from app.services.permission_service import PermissionService
from app.models.user import User, UserRole
from app.models.animal import Animal, AnimalStatus
from app.models.application import Application


@pytest.fixture
def app():
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield app


# ==================== can_manage_animal ====================
class TestCanManageAnimal:
    
    def test_owner_can_manage_personal_animal(self, app_context):
        """TC-01: 擁有者可以管理個人送養動物"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.GENERAL_MEMBER
        
        animal = Mock(spec=Animal)
        animal.owner_id = 1
        animal.shelter_id = None
        
        assert PermissionService.can_manage_animal(user, animal) is True
    
    def test_non_owner_cannot_manage_personal_animal(self, app_context):
        """TC-02: 非擁有者不能管理個人動物"""
        user = Mock(spec=User)
        user.user_id = 2
        user.role = UserRole.GENERAL_MEMBER
        
        animal = Mock(spec=Animal)
        animal.owner_id = 1
        animal.shelter_id = None
        
        assert PermissionService.can_manage_animal(user, animal) is False
    
    def test_shelter_member_can_manage_own_shelter_animal(self, app_context):
        """TC-03: 收容所成員可以管理自己收容所的動物"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.SHELTER_MEMBER
        user.primary_shelter_id = 10
        
        animal = Mock(spec=Animal)
        animal.owner_id = None
        animal.shelter_id = 10
        
        assert PermissionService.can_manage_animal(user, animal) is True
    
    def test_shelter_member_cannot_manage_other_shelter_animal(self, app_context):
        """TC-04: 收容所成員不能管理其他收容所動物"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.SHELTER_MEMBER
        user.primary_shelter_id = 10
        
        animal = Mock(spec=Animal)
        animal.owner_id = None
        animal.shelter_id = 20
        
        assert PermissionService.can_manage_animal(user, animal) is False
    
    def test_admin_can_manage_shelter_animal(self, app_context):
        """TC-05: 管理員可以管理收容所動物"""
        admin = Mock(spec=User)
        admin.user_id = 1
        admin.role = UserRole.ADMIN
        
        animal = Mock(spec=Animal)
        animal.owner_id = None
        animal.shelter_id = 10
        
        assert PermissionService.can_manage_animal(admin, animal) is True
    
    def test_admin_cannot_manage_personal_animal(self, app_context):
        """TC-06: 管理員不能管理個人動物"""
        admin = Mock(spec=User)
        admin.user_id = 1
        admin.role = UserRole.ADMIN
        
        animal = Mock(spec=Animal)
        animal.owner_id = 2
        animal.shelter_id = None
        
        assert PermissionService.can_manage_animal(admin, animal) is False
    
    def test_none_user_cannot_manage_animal(self, app_context):
        """TC-06a: None 用戶不能管理動物"""
        animal = Mock(spec=Animal)
        animal.owner_id = 1
        animal.shelter_id = None
        
        assert PermissionService.can_manage_animal(None, animal) is False
    
    def test_user_cannot_manage_none_animal(self, app_context):
        """TC-06b: 用戶不能管理 None 動物"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.GENERAL_MEMBER
        
        assert PermissionService.can_manage_animal(user, None) is False


# ==================== can_view_animal ====================
class TestCanViewAnimal:
    
    def test_anyone_can_view_published_animal(self, app_context):
        """TC-07: 任何人可以查看已發布的動物"""
        animal = Mock(spec=Animal)
        animal.status = AnimalStatus.PUBLISHED
        
        assert PermissionService.can_view_animal(None, animal) is True
    
    def test_guest_cannot_view_draft_animal(self, app_context):
        """TC-08: 未登入用戶不能查看草稿動物"""
        animal = Mock(spec=Animal)
        animal.status = AnimalStatus.DRAFT
        
        assert PermissionService.can_view_animal(None, animal) is False
    
    def test_owner_can_view_draft_animal(self, app_context):
        """TC-09: 擁有者可以查看自己的草稿"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.GENERAL_MEMBER
        
        animal = Mock(spec=Animal)
        animal.status = AnimalStatus.DRAFT
        animal.owner_id = 1
        animal.shelter_id = None
        
        assert PermissionService.can_view_animal(user, animal) is True


# ==================== can_review_application ====================
class TestCanReviewApplication:
    
    def test_owner_can_review_application(self, app_context):
        """TC-10: 擁有者可以審核申請"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.GENERAL_MEMBER
        
        animal = Mock(spec=Animal)
        animal.owner_id = 1
        animal.shelter_id = None
        
        application = Mock(spec=Application)
        application.animal = animal
        
        assert PermissionService.can_review_application(user, application) is True
    
    def test_shelter_member_can_review_shelter_application(self, app_context):
        """TC-11: 收容所成員可以審核收容所申請"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.SHELTER_MEMBER
        user.primary_shelter_id = 10
        
        animal = Mock(spec=Animal)
        animal.owner_id = None
        animal.shelter_id = 10
        
        application = Mock(spec=Application)
        application.animal = animal
        
        assert PermissionService.can_review_application(user, application) is True
    
    def test_non_owner_cannot_review_application(self, app_context):
        """TC-12: 非擁有者不能審核申請"""
        user = Mock(spec=User)
        user.user_id = 2
        user.role = UserRole.GENERAL_MEMBER
        
        animal = Mock(spec=Animal)
        animal.owner_id = 1
        animal.shelter_id = None
        
        application = Mock(spec=Application)
        application.animal = animal
        
        assert PermissionService.can_review_application(user, application) is False
    
    def test_cannot_review_none_application(self, app_context):
        """TC-12a: None application 不能審核"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.GENERAL_MEMBER
        
        assert PermissionService.can_review_application(user, None) is False
    
    def test_cannot_review_application_with_none_animal(self, app_context):
        """TC-12b: 沒有動物的申請不能審核"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.GENERAL_MEMBER
        
        application = Mock(spec=Application)
        application.animal = None
        
        assert PermissionService.can_review_application(user, application) is False


# ==================== can_view_application ====================
class TestCanViewApplication:
    
    def test_applicant_can_view_own_application(self, app_context):
        """TC-13: 申請人可以查看自己的申請"""
        user = Mock(spec=User)
        user.user_id = 1
        
        application = Mock(spec=Application)
        application.applicant_id = 1
        
        assert PermissionService.can_view_application(user, application) is True
    
    def test_animal_owner_can_view_application(self, app_context):
        """TC-14: 動物擁有者可以查看申請"""
        user = Mock(spec=User)
        user.user_id = 2
        user.role = UserRole.GENERAL_MEMBER
        
        animal = Mock(spec=Animal)
        animal.owner_id = 2
        animal.shelter_id = None
        
        application = Mock(spec=Application)
        application.applicant_id = 1
        application.animal = animal
        
        assert PermissionService.can_view_application(user, application) is True
    
    def test_admin_can_view_any_application(self, app_context):
        """TC-15: 管理員可以查看任何申請"""
        admin = Mock(spec=User)
        admin.user_id = 3
        admin.role = UserRole.ADMIN
        
        application = Mock(spec=Application)
        application.applicant_id = 1
        
        assert PermissionService.can_view_application(admin, application) is True
    
    def test_cannot_view_none_application(self, app_context):
        """TC-15a: None application 不能查看"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.GENERAL_MEMBER
        
        assert PermissionService.can_view_application(user, None) is False
    
    def test_cannot_view_application_without_animal(self, app_context):
        """TC-15b: 非申請人且無動物的申請不能查看"""
        user = Mock(spec=User)
        user.user_id = 2
        user.role = UserRole.GENERAL_MEMBER
        
        application = Mock(spec=Application)
        application.applicant_id = 1
        application.animal = None
        
        assert PermissionService.can_view_application(user, application) is False


# ==================== can_submit_animal_for_review ====================
class TestCanSubmitAnimalForReview:
    
    def test_owner_can_submit_draft_animal(self, app_context):
        """TC-16: 擁有者可以提交草稿動物"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.GENERAL_MEMBER
        
        animal = Mock(spec=Animal)
        animal.status = AnimalStatus.DRAFT
        animal.owner_id = 1
        animal.shelter_id = None
        
        assert PermissionService.can_submit_animal_for_review(user, animal) is True


# ==================== can_publish_animal ====================
class TestCanPublishAnimal:
    
    def test_admin_can_publish_pending_animal(self, app_context):
        """TC-17: 管理員可以發布待審核動物"""
        admin = Mock(spec=User)
        admin.user_id = 1
        admin.role = UserRole.ADMIN
        
        animal = Mock(spec=Animal)
        animal.status = AnimalStatus.SUBMITTED
        
        assert PermissionService.can_publish_animal(admin, animal) is True
    
    def test_non_admin_cannot_publish_animal(self, app_context):
        """TC-18: 非管理員不能發布動物"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.GENERAL_MEMBER
        
        animal = Mock(spec=Animal)
        animal.status = AnimalStatus.SUBMITTED
        
        assert PermissionService.can_publish_animal(user, animal) is False


# ==================== can_reject_animal ====================
class TestCanRejectAnimal:
    
    def test_admin_can_reject_pending_animal(self, app_context):
        """TC-19: 管理員可以拒絕待審核動物"""
        admin = Mock(spec=User)
        admin.user_id = 1
        admin.role = UserRole.ADMIN
        
        animal = Mock(spec=Animal)
        animal.status = AnimalStatus.SUBMITTED
        
        assert PermissionService.can_reject_animal(admin, animal) is True
    
    def test_non_admin_cannot_reject_animal(self, app_context):
        """TC-20: 非管理員不能拒絕動物"""
        user = Mock(spec=User)
        user.user_id = 1
        user.role = UserRole.GENERAL_MEMBER
        
        animal = Mock(spec=Animal)
        animal.status = AnimalStatus.SUBMITTED
        
        assert PermissionService.can_reject_animal(user, animal) is False
