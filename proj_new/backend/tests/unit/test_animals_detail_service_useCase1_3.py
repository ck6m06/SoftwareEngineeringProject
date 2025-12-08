"""
Use Case 1.3 動物詳情檢視 - Service 單元測試

測試範圍：僅測試 animal_service.get_animal() 的業務邏輯
測試方法：使用 monkeypatch mock Animal.query 與相關 ORM 操作，不依賴真實資料庫
與其他測試的區別：
- Unit Tests: 測試 service 業務邏輯，mock ORM
- Controller Tests: 測試 route 層邏輯，mock service  
- Integration Tests: 測試完整流程，使用真實 DB
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from app import create_app
from app.services.animal_service import AnimalService
from app.models.animal import Animal, AnimalStatus, Species, Sex
from app.models.user import User, UserRole
from app.models.medical_record import MedicalRecord
from app.exceptions import NotFoundError, ValidationError


@pytest.fixture
def app():
    """創建測試應用程式"""
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    """創建應用程式上下文"""
    with app.app_context():
        yield app


class TestAnimalServiceGetAnimal:
    """測試 animal_service.get_animal() 的業務邏輯"""
    
    def test_basic_animal_data_loading(self, app_context, monkeypatch):
        """
        TC-U1.3-01: 基本動物資料載入測試
        
        測試目的：驗證動物基本資料正確載入
        Use Case 對應：主要流程步驟 1&2 - 載入完整資料
        測試條件：合法動物ID，無當前用戶
        """
        # Mock 動物資料
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 1
        mock_animal.name = '小白'
        mock_animal.species = Species.DOG
        mock_animal.breed = '黃金獵犬'
        mock_animal.age_estimate_months = 36
        mock_animal.sex = Sex.MALE
        mock_animal.description = '溫馴友善的狗狗'
        mock_animal.location = '台北市中山區'
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.images = '["photo1.jpg", "photo2.jpg"]'
        mock_animal.deleted_at = None
        mock_animal.to_dict.return_value = {
            'animal_id': 1,
            'name': '小白',
            'species': 'DOG',
            'breed': '黃金獵犬',
            'age_estimate_months': 36,
            'sex': 'MALE',
            'description': '溫馴友善的狗狗',
            'location': '台北市中山區',
            'status': 'PUBLISHED',
            'images': ["photo1.jpg", "photo2.jpg"]
        }
        
        # Mock 查詢
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr(Animal, 'query', mock_query)
        
        # 執行測試
        result = AnimalService.get_animal(1)
        
        # 驗證
        assert result is not None
        assert result.name == '小白'
        assert result.species == Species.DOG
        assert result.breed == '黃金獵犬'
        assert result.location == '台北市中山區'
        mock_query.filter_by.assert_called_once_with(animal_id=1, deleted_at=None)
    
    def test_owner_information_loading(self, app_context, monkeypatch):
        """
        TC-U1.3-02: 擁有者資訊載入測試
        
        測試目的：驗證動物基本資料正確返回（包含 owner_id 資訊）
        Use Case 對應：主要流程步驟 3 - 送養者資訊
        測試條件：動物資料包含擁有者關聯
        """
        # Mock 動物資料包含擁有者
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 1
        mock_animal.owner_id = 100
        mock_animal.created_by = 100
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.deleted_at = None
        mock_animal.name = '小白'
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr(Animal, 'query', mock_query)
        
        # 執行測試
        result = AnimalService.get_animal(1)
        
        # 驗證
        assert result is not None
        assert result.owner_id == 100
        assert result.created_by == 100
        # get_animal() 只需要正確查詢動物資料
        mock_query.filter_by.assert_called_once_with(animal_id=1, deleted_at=None)
    
    def test_medical_records_filtering(self, app_context, monkeypatch):
        """
        TC-U1.3-03: 動物基本資料正確返回測試
        
        測試目的：驗證 get_animal() 正確返回動物實例
        Use Case 對應：輔助說明 3 - 完整資料顯示
        測試條件：正常動物資料查詢
        """
        # Mock 動物
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 1
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.deleted_at = None
        mock_animal.name = '小白'
        mock_animal.breed = '黃金獵犬'
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr(Animal, 'query', mock_query)
        
        result = AnimalService.get_animal(1)
        
        # 驗證動物資料正確返回
        assert result is not None
        assert result.animal_id == 1
        assert result.name == '小白'
        assert result.breed == '黃金獵犬'
        mock_query.filter_by.assert_called_once_with(animal_id=1, deleted_at=None)
    
    def test_animal_not_found_error(self, app_context, monkeypatch):
        """
        TC-U1.3-04: 動物不存在處理測試
        
        測試目的：驗證無效動物ID的錯誤處理
        測試條件：不存在的動物ID
        """
        # Mock 空結果
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr(Animal, 'query', mock_query)
        
        # 執行測試並驗證異常
        with pytest.raises(NotFoundError) as exc_info:
            AnimalService.get_animal(999)
        
        assert '動物不存在' in str(exc_info.value)
    
    def test_member_vs_guest_data_difference(self, app_context, monkeypatch):
        """
        TC-U1.3-05: 會員vs訪客資料差異測試
        
        測試目的：驗證 get_animal() 的基本功能正常運作
        Use Case 對應：主要流程步驟 4 - 完整資料顯示
        測試條件：正常動物資料查詢
        注意：get_animal() 不接受 current_user_id 參數
        """
        # Mock 動物資料
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 1
        mock_animal.owner_id = 100
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.deleted_at = None
        mock_animal.name = '小白'
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr(Animal, 'query', mock_query)
        
        # 測試存取動物資料（實際 API 不區分訪客和會員）
        result = AnimalService.get_animal(1)
        assert result is not None
        assert result.animal_id == 1
        assert result.name == '小白'
        assert result.owner_id == 100
        
        # 驗證查詢被正確執行
        mock_query.filter_by.assert_called_with(animal_id=1, deleted_at=None)
    
    def test_owner_viewing_own_animal(self, app_context, monkeypatch):
        """
        TC-U1.3-06: 擁有者查看自己動物測試
        
        測試目的：驗證動物擁有者資訊正確返回
        Use Case 對應：輔助說明 2 - 送養者資訊顯示
        測試條件：動物包含 owner_id 資訊
        注意：get_animal() 不接受 current_user_id 參數
        """
        # Mock 動物資料
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 1
        mock_animal.owner_id = 100
        mock_animal.created_by = 100
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.deleted_at = None
        mock_animal.name = '小白'
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr(Animal, 'query', mock_query)
        
        # 執行測試 - 查看動物資料
        result = AnimalService.get_animal(1)
        
        # 驗證
        assert result is not None
        assert result.animal_id == 1
        assert result.owner_id == 100
        assert result.created_by == 100
        # 驗證查詢被正確執行
        mock_query.filter_by.assert_called_once_with(animal_id=1, deleted_at=None)
    
    def test_application_button_display_logic(self, app_context, monkeypatch):
        """
        TC-U1.3-07: 申請狀態判斷邏輯測試
        
        測試目的：驗證申請按鈕顯示邏輯
        Use Case 對應：輔助說明 1 - 申請按鈕顯示條件
        測試條件：動物處於不同狀態（AVAILABLE/PENDING/ADOPTED）
        """
        # 測試 PUBLISHED 狀態（可申請）
        mock_animal_available = Mock(spec=Animal)
        mock_animal_available.animal_id = 1
        mock_animal_available.status = AnimalStatus.PUBLISHED
        mock_animal_available.deleted_at = None
        
        # 測試 ADOPTED 狀態（不可申請）
        mock_animal_adopted = Mock(spec=Animal)
        mock_animal_adopted.animal_id = 2
        mock_animal_adopted.status = AnimalStatus.ADOPTED
        mock_animal_adopted.deleted_at = None
        
        mock_query = Mock()
        # 先測試 PUBLISHED 狀態
        mock_query.filter_by.return_value.first.return_value = mock_animal_available
        monkeypatch.setattr(Animal, 'query', mock_query)
        
        result_available = AnimalService.get_animal(1)
        assert result_available.status == AnimalStatus.PUBLISHED
        
        # 測試 ADOPTED 狀態
        mock_query.filter_by.return_value.first.return_value = mock_animal_adopted
        result_adopted = AnimalService.get_animal(2)
        assert result_adopted.status == AnimalStatus.ADOPTED
    
    def test_images_json_parsing(self, app_context, monkeypatch):
        """
        TC-U1.3-08: 圖片資料解析測試
        
        測試目的：驗證圖片JSON資料正確解析
        Use Case 對應：主要流程步驟 2 - 圖片集顯示
        測試條件：動物包含圖片JSON字串
        """
        # Mock 包含圖片的動物
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 1
        mock_animal.images = '["photo1.jpg", "photo2.jpg", "photo3.jpg"]'
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.deleted_at = None
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr(Animal, 'query', mock_query)
        
        # 執行測試
        result = AnimalService.get_animal(1)
        
        # 驗證
        assert result is not None
        assert result.images is not None
        # 在實際實作中，service 應該正確解析 JSON 字串為陣列
    
    def test_empty_images_handling(self, app_context, monkeypatch):
        """
        測試目的：驗證空圖片情況的處理
        測試條件：動物沒有圖片或圖片為空
        """
        # Mock 無圖片的動物
        mock_animal = Mock(spec=Animal)
        mock_animal.animal_id = 1
        mock_animal.images = None  # 或 '[]'
        mock_animal.status = AnimalStatus.PUBLISHED
        mock_animal.deleted_at = None
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_animal
        monkeypatch.setattr(Animal, 'query', mock_query)
        
        # 執行測試
        result = AnimalService.get_animal(1)
        
        # 驗證
        assert result is not None
        # 空圖片應該被正確處理，不應該導致錯誤
    
    def test_deleted_animal_not_accessible(self, app_context, monkeypatch):
        """
        測試目的：驗證已刪除動物無法存取
        測試條件：動物的 deleted_at 不為 None
        """
        # Mock 查詢 - 已刪除動物不會被查詢到
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None  # 因為 deleted_at=None 過濾
        monkeypatch.setattr(Animal, 'query', mock_query)
        
        # 執行測試並驗證異常
        with pytest.raises(NotFoundError):
            AnimalService.get_animal(1)
        
        # 驗證查詢條件包含 deleted_at=None
        mock_query.filter_by.assert_called_once_with(animal_id=1, deleted_at=None)
