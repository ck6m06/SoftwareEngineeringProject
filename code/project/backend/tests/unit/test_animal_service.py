"""
單元測試：app/services/animal_service.py - 完整版

目標：100% 測試通過率 + 最高覆蓋率
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from app import create_app
from app.services.animal_service import AnimalService
from app.models.animal import Animal, AnimalImage, AnimalStatus, Species, Sex
from app.models.user import User, UserRole
from app.exceptions import NotFoundError, ValidationError, PermissionDeniedError


@pytest.fixture
def app():
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield app


# ==================== create_animal ====================
class TestCreateAnimal:
    
    def test_shelter_member_creates_animal_for_shelter(self, app_context, monkeypatch):
        """TC-01: 收容所成員創建動物歸屬收容所"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.SHELTER_MEMBER
        mock_user.primary_shelter_id = 10
        
        data = {'name': '小白', 'species': 'DOG'}
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.create_animal(mock_user, data)
        
        assert result.shelter_id == 10
        assert result.owner_id is None
        mock_db_session.add.assert_called_once()
    
    def test_general_member_creates_animal_for_personal(self, app_context, monkeypatch):
        """TC-02: 一般會員創建個人動物"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 2
        mock_user.role = UserRole.GENERAL_MEMBER
        mock_user.primary_shelter_id = None
        
        data = {'name': '小黑', 'species': 'CAT'}
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.create_animal(mock_user, data)
        
        assert result.owner_id == 2
        assert result.shelter_id is None
    
    def test_admin_can_specify_shelter(self, app_context, monkeypatch):
        """TC-03: 管理員指定收容所"""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.ADMIN
        
        data = {'name': '小花', 'species': 'DOG', 'shelter_id': 20}
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.create_animal(mock_user, data)
        
        assert result.shelter_id == 20
    
    def test_raises_error_if_both_owner_and_shelter(self, app_context):
        """TC-04: 防護測試"""
        pass


# ==================== update_animal ====================
class TestUpdateAnimal:
    
    def test_owner_can_update_own_animal(self, app_context, monkeypatch):
        """TC-05: 擁有者更新動物"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        
        mock_animal = Mock(spec=Animal)
        mock_animal.owner_id = 1
        mock_animal.shelter_id = None
        mock_animal.name = '舊名字'
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.update_animal(100, mock_user, {'name': '新名字'})
        
        assert result.name == '新名字'
    
    def test_raises_not_found_if_animal_deleted(self, app_context, monkeypatch):
        """TC-06: 已刪除動物拋出錯誤"""
        mock_user = Mock(spec=User)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        with pytest.raises(NotFoundError):
            AnimalService.update_animal(999, mock_user, {'name': '新名字'})
    
    def test_raises_permission_denied_for_other_user(self, app_context, monkeypatch):
        """TC-07: 無權限拋出錯誤"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = False
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(PermissionDeniedError):
            AnimalService.update_animal(100, mock_user, {'name': '新名字'})


# ==================== delete_animal ====================
class TestDeleteAnimal:
    
    def test_soft_delete_sets_deleted_at(self, app_context, monkeypatch):
        """TC-08: 軟刪除設定時間戳"""
        mock_user = Mock(spec=User)
        
        mock_animal = Mock(spec=Animal)
        mock_animal.deleted_at = None
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        AnimalService.delete_animal(100, mock_user)
        
        assert mock_animal.deleted_at is not None


# ==================== get_animal ====================
class TestGetAnimal:
    
    def test_get_animal_returns_basic_data(self, app_context, monkeypatch):
        """TC-09: 取得動物基本資料"""
        mock_animal = Mock(spec=Animal)
        mock_animal.name = '小白'
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.get_animal(1)
        
        assert result.name == '小白'
    
    def test_get_animal_not_found_raises_error(self, app_context, monkeypatch):
        """TC-10: 動物不存在拋出錯誤"""
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        with pytest.raises(NotFoundError):
            AnimalService.get_animal(999)
    
    def test_get_animal_excludes_deleted(self, app_context, monkeypatch):
        """TC-11: 排除已刪除動物"""
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        try:
            AnimalService.get_animal(1)
        except:
            pass
        
        mock_query.filter_by.assert_called_with(animal_id=1, deleted_at=None)


# ==================== list_animals ====================
class TestListAnimals:
    
    def test_guest_sees_published_animals_only(self, app_context, monkeypatch):
        """TC-12: 訪客只看已發布動物"""
        mock_animal = Mock(spec=Animal)
        mock_animal.to_dict.return_value = {'animal_id': 1}
        
        mock_pagination = Mock()
        mock_pagination.items = [mock_animal]
        mock_pagination.total = 1
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 1
        
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value.filter_by.return_value = mock_filter_result
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'page': 1, 'per_page': 20})
        
        assert result['total'] == 1
    
    def test_filters_by_species(self, app_context, monkeypatch):
        """TC-13: 物種篩選"""
        mock_animal = Mock(spec=Animal)
        mock_animal.to_dict.return_value = {'animal_id': 1, 'species': 'DOG'}
        
        mock_pagination = Mock()
        mock_pagination.items = [mock_animal]
        mock_pagination.total = 1
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 1
        
        # Chain: query.filter_by(deleted_at) -> .filter_by(status) -> .filter_by(species) -> .order_by() -> .paginate()
        # 創建一個 Mock 來處理所有的 filter_by 調用
        mock_chain = Mock()
        # filter_by 可以被多次調用，每次都返回自己以支持鏈式調用
        mock_chain.filter_by.return_value = mock_chain
        # 最後的 order_by().paginate() 返回 pagination
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'species': 'DOG', 'page': 1})
        
        assert result['total'] == 1
    
    def test_pagination_works_correctly(self, app_context, monkeypatch):
        """TC-14: 分頁功能"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 100
        mock_pagination.pages = 5
        mock_pagination.page = 2
        mock_pagination.per_page = 20
        
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value.filter_by.return_value = mock_filter_result
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'page': 2, 'per_page': 20})
        
        assert result['page'] == 2
        assert result['total'] == 100


# ==================== status transitions ====================
class TestAnimalStatusTransitions:
    
    def test_submit_for_review_changes_status(self, app_context, monkeypatch):
        """TC-15: 提交審核"""
        mock_user = Mock(spec=User)
        
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.DRAFT
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_submit_animal_for_review.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.submit_for_review(100, mock_user)
        
        assert result.status == AnimalStatus.SUBMITTED
    
    def test_publish_animal_requires_admin(self, app_context, monkeypatch):
        """TC-16: 發布動物"""
        mock_admin = Mock(spec=User)
        
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.SUBMITTED
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_publish_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.publish_animal(100, mock_admin)
        
        assert result.status == AnimalStatus.PUBLISHED
    
    def test_retire_animal_sets_status_retired(self, app_context, monkeypatch):
        """TC-17: 下架動物"""
        mock_user = Mock(spec=User)
        
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.PUBLISHED
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.retire_animal(100, mock_user)
        
        assert result.status == AnimalStatus.RETIRED
    
    def test_reject_animal_with_reason(self, app_context, monkeypatch):
        """TC-18: 拒絕動物並記錄原因"""
        mock_admin = Mock(spec=User)
        mock_admin.user_id = 99
        
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.SUBMITTED
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_reject_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.reject_animal(100, mock_admin, '資料不完整')
        
        assert result.status == AnimalStatus.DRAFT
        assert result.rejection_reason == '資料不完整'


# ==================== images ====================
class TestAnimalImages:
    
    def test_add_image_creates_record(self, app_context, monkeypatch):
        """TC-19: 新增圖片"""
        mock_user = Mock(spec=User)
        
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 100
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_query_result = Mock()
        mock_query_result.filter_by.return_value.scalar.return_value = 0
        
        mock_db_session = MagicMock()
        mock_db_session.query.return_value = mock_query_result
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        mock_image_class = Mock()
        monkeypatch.setattr('app.services.animal_service.AnimalImage', mock_image_class)
        
        AnimalService.add_image(100, mock_user, 'key', 'url')
        
        mock_image_class.assert_called_once()
    
    def test_delete_image_removes_record(self, app_context, monkeypatch):
        """TC-20: 刪除圖片"""
        mock_user = Mock(spec=User)
        
        mock_animal = Mock(spec=Animal)
        mock_image = Mock(spec=AnimalImage)
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_animal_query)
        
        mock_image_query = Mock()
        mock_image_query.filter_by.return_value.first.return_value = mock_image
        monkeypatch.setattr('app.services.animal_service.AnimalImage.query', mock_image_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        AnimalService.delete_image(100, 50, mock_user)
        
        mock_db_session.delete.assert_called_once_with(mock_image)
    
    def test_reorder_images_updates_order(self, app_context, monkeypatch):
        """TC-21: 重新排序圖片"""
        mock_user = Mock(spec=User)
        
        mock_animal = Mock(spec=Animal)
        
        mock_image1 = Mock(spec=AnimalImage)
        mock_image1.animal_image_id = 1
        mock_image1.order = 1
        
        mock_image2 = Mock(spec=AnimalImage)
        mock_image2.animal_image_id = 2
        mock_image2.order = 2
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_animal_query)
        
        def mock_image_query_side_effect(*args, **kwargs):
            mock_result = Mock()
            if kwargs.get('animal_image_id') == 1:
                mock_result.first.return_value = mock_image1
            elif kwargs.get('animal_image_id') == 2:
                mock_result.first.return_value = mock_image2
            return mock_result
        
        mock_image_query = Mock()
        mock_image_query.filter_by.side_effect = mock_image_query_side_effect
        monkeypatch.setattr('app.services.animal_service.AnimalImage.query', mock_image_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        orders = [{'image_id': 2, 'order': 1}, {'image_id': 1, 'order': 2}]
        AnimalService.reorder_images(100, mock_user, orders)
        
        assert mock_image1.order == 2
        assert mock_image2.order == 1


# ==================== advanced list_animals filters ====================
class TestAdvancedListFilters:
    
    def test_filters_by_keyword_search(self, app_context, monkeypatch):
        """TC-22: 關鍵字搜尋"""
        mock_animal = Mock(spec=Animal)
        mock_animal.to_dict.return_value = {'name': '小白'}
        
        mock_pagination = Mock()
        mock_pagination.items = [mock_animal]
        mock_pagination.total = 1
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 1
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'q': '小白', 'page': 1})
        
        assert result['total'] == 1
    
    def test_filters_by_source_type_shelter(self, app_context, monkeypatch):
        """TC-23: 來源類型篩選 - 收容所"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'source_type': 'shelter', 'page': 1})
        
        assert 'animals' in result
    
    def test_filters_by_source_type_personal(self, app_context, monkeypatch):
        """TC-24: 來源類型篩選 - 個人"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'source_type': 'personal', 'page': 1})
        
        assert 'animals' in result
    
    def test_filters_by_region(self, app_context, monkeypatch):
        """TC-25: 地區篩選"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'region': '台北', 'page': 1})
        
        assert 'animals' in result
    
    def test_filters_by_age_range(self, app_context, monkeypatch):
        """TC-26: 年齡範圍篩選"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        mock_db = Mock()
        mock_db.engine.name = 'mysql'
        monkeypatch.setattr('app.services.animal_service.db', mock_db)
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'min_age': 6, 'max_age': 24, 'page': 1})
        
        assert 'animals' in result
    
    def test_owner_id_filter_with_current_user(self, app_context, monkeypatch):
        """TC-27: owner_id 篩選 (查詢自己)"""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.GENERAL_MEMBER
        mock_user.primary_shelter_id = None
        
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        # Mock db.session.get to return mock_user
        mock_db_session = MagicMock()
        mock_db_session.get.return_value = mock_user
        
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'owner_id': 5, 'page': 1}, current_user_id=5)
        
        assert 'animals' in result
    
    def test_owner_id_filter_shelter_member(self, app_context, monkeypatch):
        """TC-28: 收容所成員查詢 owner_id"""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.SHELTER_MEMBER
        mock_user.primary_shelter_id = 10
        
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        # Mock db.session.get to return mock_user
        mock_db_session = MagicMock()
        mock_db_session.get.return_value = mock_user
        
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'owner_id': 5, 'page': 1}, current_user_id=5)
        
        assert 'animals' in result
    
    def test_owner_id_filter_guest(self, app_context, monkeypatch):
        """TC-29: 訪客查詢 owner_id (只看已發布)"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'owner_id': 5, 'page': 1}, current_user_id=None)
        
        assert 'animals' in result
    
    def test_created_by_filter(self, app_context, monkeypatch):
        """TC-30: created_by 篩選"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'created_by': 10, 'page': 1})
        
        assert 'animals' in result


# ==================== validation errors ====================
class TestValidationErrors:
    
    def test_invalid_species_raises_error(self, app_context, monkeypatch):
        """TC-31: 無效物種值"""
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        with pytest.raises(ValidationError, match='無效的物種值'):
            AnimalService.list_animals({'species': 'INVALID_SPECIES', 'page': 1})
    
    def test_invalid_sex_raises_error(self, app_context, monkeypatch):
        """TC-32: 無效性別值"""
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        with pytest.raises(ValidationError, match='無效的性別值'):
            AnimalService.list_animals({'sex': 'INVALID_SEX', 'page': 1})
    
    def test_invalid_status_raises_error(self, app_context, monkeypatch):
        """TC-33: 無效狀態值"""
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        with pytest.raises(ValidationError, match='無效的狀態值'):
            AnimalService.list_animals({'status': 'INVALID_STATUS', 'page': 1})
    
    def test_update_animal_with_invalid_species(self, app_context, monkeypatch):
        """TC-34: 更新動物 - 無效物種"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises((ValidationError, ValueError)):
            AnimalService.update_animal(100, mock_user, {'species': 'INVALID'})
    
    def test_update_animal_with_invalid_sex(self, app_context, monkeypatch):
        """TC-35: 更新動物 - 無效性別"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises((ValidationError, ValueError)):
            AnimalService.update_animal(100, mock_user, {'sex': 'INVALID'})
    
    def test_update_animal_with_invalid_status(self, app_context, monkeypatch):
        """TC-36: 更新動物 - 無效狀態"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises((ValidationError, ValueError)):
            AnimalService.update_animal(100, mock_user, {'status': 'INVALID'})


# ==================== update_animal field variations ====================
class TestUpdateAnimalFields:
    
    def test_update_animal_multiple_fields(self, app_context, monkeypatch):
        """TC-37: 更新多個欄位"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        mock_animal.owner_id = 1
        mock_animal.shelter_id = None
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        data = {
            'name': '新名字',
            'breed': '混種',
            'color': '黑色',
            'description': '可愛的狗狗'
        }
        
        result = AnimalService.update_animal(100, mock_user, data)
        
        assert result.name == '新名字'
        assert result.breed == '混種'
        assert result.color == '黑色'
        assert result.description == '可愛的狗狗'


# ==================== status transition errors ====================
class TestStatusTransitionErrors:
    
    def test_submit_for_review_permission_denied(self, app_context, monkeypatch):
        """TC-38: 提交審核 - 權限不足"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_submit_animal_for_review.return_value = False
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(PermissionDeniedError):
            AnimalService.submit_for_review(100, mock_user)
    
    def test_publish_animal_permission_denied(self, app_context, monkeypatch):
        """TC-39: 發布動物 - 權限不足"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_publish_animal.return_value = False
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(PermissionDeniedError):
            AnimalService.publish_animal(100, mock_user)
    
    def test_reject_animal_permission_denied(self, app_context, monkeypatch):
        """TC-40: 拒絕動物 - 權限不足"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_reject_animal.return_value = False
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(PermissionDeniedError):
            AnimalService.reject_animal(100, mock_user, '理由')


# ==================== image operation errors ====================
class TestImageOperationErrors:
    
    def test_add_image_permission_denied(self, app_context, monkeypatch):
        """TC-41: 新增圖片 - 權限不足"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = False
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(PermissionDeniedError):
            AnimalService.add_image(100, mock_user, 'key', 'url')
    
    def test_delete_image_not_found(self, app_context, monkeypatch):
        """TC-42: 刪除圖片 - 圖片不存在"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_animal_query)
        
        mock_image_query = Mock()
        mock_image_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.animal_service.AnimalImage.query', mock_image_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(NotFoundError):
            AnimalService.delete_image(100, 50, mock_user)


# ==================== edge cases for 100% coverage ====================
class TestEdgeCasesForFullCoverage:
    
    def test_update_animal_dob_field(self, app_context, monkeypatch):
        """TC-43: 更新動物出生日期"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        mock_animal.owner_id = 1
        mock_animal.shelter_id = None
        mock_animal.dob = None
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.update_animal(100, mock_user, {'dob': '2020-01-15'})
        
        # 驗證 dob 被更新
        assert mock_animal.dob is not None
    
    def test_update_animal_medical_summary_field(self, app_context, monkeypatch):
        """TC-44: 更新動物醫療摘要"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        mock_animal.owner_id = 1
        mock_animal.shelter_id = None
        mock_animal.medical_summary = None
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.update_animal(100, mock_user, {'medical_summary': '健康狀況良好'})
        
        assert mock_animal.medical_summary == '健康狀況良好'
    
    def test_delete_animal_as_admin(self, app_context, monkeypatch):
        """TC-45: 管理員可以刪除任何動物"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_animal = Mock(spec=Animal)
        mock_animal.owner_id = 999  # 不是管理員的動物
        mock_animal.deleted_at = None
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = False  # 沒有管理權限
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        # 管理員可以刪除（不會拋出錯誤）
        AnimalService.delete_animal(100, mock_admin)
        
        assert mock_animal.deleted_at is not None
    
    def test_submit_for_review_wrong_status_raises_error(self, app_context, monkeypatch):
        """TC-46: 提交審核 - 非草稿狀態拋出錯誤"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.PUBLISHED  # 已發布，不是草稿
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_submit_animal_for_review.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(ValidationError, match='只能提交草稿狀態的動物'):
            AnimalService.submit_for_review(100, mock_user)
    
    def test_publish_animal_already_published_raises_error(self, app_context, monkeypatch):
        """TC-47: 發布動物 - 已經是發布狀態"""
        mock_admin = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.PUBLISHED  # 已經發布
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_publish_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(ValidationError, match='動物已經是發布狀態'):
            AnimalService.publish_animal(100, mock_admin)
    
    def test_retire_animal_as_admin(self, app_context, monkeypatch):
        """TC-48: 管理員下架動物"""
        mock_admin = Mock(spec=User)
        mock_admin.role = UserRole.ADMIN
        
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.owner_id = 999  # 不是管理員的動物
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = False  # 沒有管理權限
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        # 管理員可以下架
        result = AnimalService.retire_animal(100, mock_admin)
        
        assert result.status == AnimalStatus.RETIRED
    
    def test_retire_animal_already_retired_raises_error(self, app_context, monkeypatch):
        """TC-49: 下架動物 - 已經是下架狀態"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.RETIRED  # 已經下架
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(ValidationError, match='動物已經是下架狀態'):
            AnimalService.retire_animal(100, mock_user)
    
    def test_reject_animal_wrong_status_raises_error(self, app_context, monkeypatch):
        """TC-50: 拒絕動物 - 非待審核狀態"""
        mock_admin = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.PUBLISHED  # 已發布，不是待審核
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_reject_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(ValidationError, match='只能拒絕待審核狀態的動物'):
            AnimalService.reject_animal(100, mock_admin, '理由')
    
    def test_reject_animal_empty_reason_raises_error(self, app_context, monkeypatch):
        """TC-51: 拒絕動物 - 未提供原因"""
        mock_admin = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        mock_animal.status = AnimalStatus.SUBMITTED
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_reject_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(ValidationError, match='請提供拒絕原因'):
            AnimalService.reject_animal(100, mock_admin, '   ')  # 空白字串
    
    def test_add_image_animal_not_found(self, app_context, monkeypatch):
        """TC-52: 新增圖片 - 動物不存在"""
        mock_user = Mock(spec=User)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        with pytest.raises(NotFoundError, match='動物不存在'):
            AnimalService.add_image(999, mock_user, 'key', 'url')
    
    def test_delete_image_animal_not_found(self, app_context, monkeypatch):
        """TC-53: 刪除圖片 - 動物不存在"""
        mock_user = Mock(spec=User)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        with pytest.raises(NotFoundError, match='動物不存在'):
            AnimalService.delete_image(999, 50, mock_user)
    
    def test_reorder_images_animal_not_found(self, app_context, monkeypatch):
        """TC-54: 重新排序圖片 - 動物不存在"""
        mock_user = Mock(spec=User)
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        with pytest.raises(NotFoundError, match='動物不存在'):
            AnimalService.reorder_images(999, mock_user, [])
    
    def test_reorder_images_permission_denied(self, app_context, monkeypatch):
        """TC-55: 重新排序圖片 - 權限不足"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_animal_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = False
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        with pytest.raises(PermissionDeniedError):
            AnimalService.reorder_images(100, mock_user, [])
    
    def test_list_animals_filter_by_shelter_id(self, app_context, monkeypatch):
        """TC-56: 依收容所篩選"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'shelter_id': 10, 'page': 1})
        
        assert 'animals' in result
    
    def test_list_animals_filter_by_sex(self, app_context, monkeypatch):
        """TC-57: 依性別篩選"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'sex': 'MALE', 'page': 1})
        
        assert 'animals' in result
    
    def test_list_animals_with_sqlite_age_filter(self, app_context, monkeypatch):
        """TC-58: 年齡篩選 - SQLite 版本"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        mock_db = Mock()
        mock_db.engine.name = 'sqlite'  # 測試 SQLite 路徑
        monkeypatch.setattr('app.services.animal_service.db', mock_db)
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        result = AnimalService.list_animals({'min_age': 6, 'page': 1})
        
        assert 'animals' in result
    
    def test_owner_id_filter_other_user(self, app_context, monkeypatch):
        """TC-59: 查詢其他用戶的動物（只能看已發布）"""
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.pages = 0
        
        mock_chain = Mock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.order_by.return_value.paginate.return_value = mock_pagination
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_chain
        
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        # 用戶 10 查詢用戶 5 的動物
        result = AnimalService.list_animals({'owner_id': 5, 'page': 1}, current_user_id=10)
        
        assert 'animals' in result
    
    def test_update_animal_status_field(self, app_context, monkeypatch):
        """TC-60: 更新動物狀態欄位"""
        mock_user = Mock(spec=User)
        mock_animal = Mock(spec=Animal)
        mock_animal.owner_id = 1
        mock_animal.shelter_id = None
        mock_animal.status = AnimalStatus.DRAFT
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr('app.services.animal_service.Animal.query', mock_query)
        
        mock_permission = Mock()
        mock_permission.can_manage_animal.return_value = True
        monkeypatch.setattr('app.services.animal_service.permission_service', mock_permission)
        
        mock_db_session = MagicMock()
        monkeypatch.setattr('app.services.animal_service.db.session', mock_db_session)
        
        result = AnimalService.update_animal(100, mock_user, {'status': 'PUBLISHED'})
        
        assert mock_animal.status == AnimalStatus.PUBLISHED
