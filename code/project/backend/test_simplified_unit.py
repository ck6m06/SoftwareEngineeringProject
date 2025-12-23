"""
Use Case 1.2 動物搜尋篩選 - 簡化版單元測試

測試目標：只測試核心業務邏輯，避免複雜的 ORM Mock
測試範圍：輸入驗證和業務規則
測試方法：針對具體功能進行單一測試
"""
import pytest
from unittest.mock import Mock, patch

from app import create_app
from app.services.animal_service import AnimalService
from app.models.animal import Species, Sex, AnimalStatus
from app.exceptions import ValidationError


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


class TestAnimalServiceValidation:
    """測試動物服務的輸入驗證邏輯"""
    
    def test_invalid_species_validation(self, app_context):
        """
        TC-U1.2-01: 無效物種驗證測試
        
        測試重點：
        - 輸入無效物種時應拋出 ValidationError
        - 錯誤訊息應包含 '無效的物種值'
        """
        filters = {'species': 'INVALID_ANIMAL'}
        
        with pytest.raises(ValidationError) as exc_info:
            AnimalService.list_animals(filters)
        
        assert '無效的物種值' in str(exc_info.value)
    
    def test_invalid_sex_validation(self, app_context):
        """
        TC-U1.2-02: 無效性別驗證測試
        
        測試重點：
        - 輸入無效性別時應拋出 ValidationError
        - 錯誤訊息應包含 '無效的性別值'
        """
        filters = {'sex': 'UNKNOWN_GENDER'}
        
        with pytest.raises(ValidationError) as exc_info:
            AnimalService.list_animals(filters)
        
        assert '無效的性別值' in str(exc_info.value)
    
    def test_valid_species_conversion(self, app_context):
        """
        TC-U1.2-03: 有效物種轉換測試
        
        測試重點：
        - 字串 'DOG' 應該不拋出錯誤
        - 能正常進入業務邏輯流程
        """
        # Mock ORM 以避免資料庫操作，但讓驗證邏輯執行
        with patch('app.services.animal_service.Animal') as mock_animal:
            # 創建一個簡單的 mock chain
            mock_query = Mock()
            mock_filter_by = Mock()
            mock_order_by = Mock()
            mock_pagination = Mock()
            
            # 設定 Mock 鏈式調用
            mock_animal.query.filter_by.return_value = mock_filter_by
            mock_filter_by.filter_by.return_value = mock_filter_by
            mock_filter_by.order_by.return_value = mock_order_by
            mock_order_by.paginate.return_value = mock_pagination
            
            # 設定 pagination 屬性
            mock_pagination.items = []
            mock_pagination.total = 0
            mock_pagination.page = 1
            mock_pagination.per_page = 20
            mock_pagination.pages = 0
            
            # Mock to_dict 方法避免錯誤
            for item in mock_pagination.items:
                item.to_dict = Mock(return_value={})
            
            filters = {'species': 'DOG'}
            
            try:
                result = AnimalService.list_animals(filters)
                # 如果沒有拋出異常，說明 species 轉換成功
                assert isinstance(result, dict)
                assert 'animals' in result
            except ValidationError:
                pytest.fail("Valid species 'DOG' should not raise ValidationError")
    
    def test_valid_sex_conversion(self, app_context):
        """
        TC-U1.2-04: 有效性別轉換測試
        
        測試重點：
        - 字串 'FEMALE' 應該不拋出錯誤
        - 能正常進入業務邏輯流程
        """
        with patch('app.services.animal_service.Animal') as mock_animal:
            # 簡化的 Mock 設置
            mock_pagination = Mock()
            mock_pagination.items = []
            mock_pagination.total = 0
            mock_pagination.page = 1
            mock_pagination.per_page = 20
            mock_pagination.pages = 0
            
            mock_animal.query.filter_by.return_value.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination
            
            filters = {'sex': 'FEMALE'}
            
            try:
                result = AnimalService.list_animals(filters)
                # 如果沒有拋出異常，說明 sex 轉換成功
                assert isinstance(result, dict)
                assert 'animals' in result
            except ValidationError:
                pytest.fail("Valid sex 'FEMALE' should not raise ValidationError")


class TestAnimalServiceBusinessLogic:
    """測試動物服務的業務邏輯"""
    
    @patch('app.services.animal_service.Animal')
    @patch('app.services.animal_service.db')
    def test_per_page_limit_enforcement(self, mock_db, mock_animal, app_context):
        """
        TC-U1.2-05: 分頁限制測試
        
        測試重點：
        - per_page 超過 100 應被限制為 100
        - min() 函數的正確使用
        """
        # 設定簡單的 Mock 鏈
        mock_pagination = Mock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.page = 1
        mock_pagination.per_page = 100  # 期望被限制的值
        mock_pagination.pages = 1
        
        mock_animal.query.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination
        
        filters = {'per_page': 200}  # 超過限制的值
        
        result = AnimalService.list_animals(filters)
        
        # 驗證分頁被正確限制
        paginate_call = mock_animal.query.filter_by.return_value.order_by.return_value.paginate
        paginate_call.assert_called_once()
        
        # 檢查調用參數中的 per_page 是否被限制
        call_args = paginate_call.call_args
        assert call_args[1]['per_page'] == 100
        
        # 驗證回傳結果結構
        assert isinstance(result, dict)
        assert 'per_page' in result
        assert result['per_page'] == 100


if __name__ == "__main__":
    pytest.main([__file__, '-v'])