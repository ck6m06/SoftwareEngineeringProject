# """
# Animal Service 搜尋篩選功能測試檔案
# 只驗證業務邏輯是否正確觸發相關的篩選方法
# """

# import pytest
# from unittest.mock import Mock, patch, MagicMock
# from app.services.animal_service import AnimalService
# from app.exceptions import ValidationError
# from app.models.animal import Species, Sex


# class TestAnimalServiceSearchFilters:

#     @pytest.fixture
#     def app_context(self):
#         """建立 Flask app context"""
#         from app import create_app
#         app = create_app()
#         with app.app_context():
#             yield app

#     @pytest.fixture
#     def mock_db(self):
#         """Mock 資料庫"""
#         with patch('app.services.animal_service.db') as mock:
#             yield mock

#     def test_species_filter_conversion(self, app_context, mock_db):
#         """測試物種篩選邏輯"""
#         mock_pagination = Mock()
#         mock_pagination.items = []
#         mock_pagination.total = 0
#         mock_pagination.page = 1
#         mock_pagination.per_page = 20
#         mock_pagination.pages = 1

#         with patch('app.services.animal_service.Animal') as mock_animal:
#             mock_animal.query.filter_by.return_value.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination

#             filters = {'species': 'DOG'}
#             result = AnimalService.list_animals(filters)

#             # 驗證species篩選被觸發
#             mock_animal.query.filter_by.assert_any_call(deleted_at=None)
#             assert 'animals' in result

#     def test_age_range_filter_logic(self, app_context, mock_db):
#         """測試年齡範圍篩選邏輯"""
#         mock_pagination = Mock()
#         mock_pagination.items = []
#         mock_pagination.total = 0

#         with patch('app.services.animal_service.Animal') as mock_animal, \
#              patch('app.services.animal_service.func') as mock_func, \
#              patch('app.services.animal_service.db') as mock_db_patch:

#             mock_animal.query.filter_by.return_value.filter.return_value.filter.return_value.order_by.return_value.paginate.return_value = mock_pagination
#             mock_db_patch.engine.name = 'sqlite'  # 模擬 SQLite 環境
            
#             filters = {'min_age': 2, 'max_age': 5}
#             result = AnimalService.list_animals(filters)

#             # 驗證年齡篩選邏輯被觸發
#             assert mock_func.julianday.called  # SQLite 日期函數被調用
#             assert 'animals' in result

#     def test_keyword_search_across_multiple_fields(self, app_context, mock_db):
#         """測試關鍵字搜尋邏輯"""
#         mock_pagination = Mock()
#         mock_pagination.items = []
#         mock_pagination.total = 0

#         with patch('app.services.animal_service.Animal') as mock_animal, \
#              patch('app.services.animal_service.or_') as mock_or:

#             mock_animal.query.filter_by.return_value.filter.return_value.order_by.return_value.paginate.return_value = mock_pagination
#             # Mock Animal 的欄位屬性
#             mock_animal.name.like = Mock(return_value=Mock())
#             mock_animal.description.like = Mock(return_value=Mock())
#             mock_animal.breed.like = Mock(return_value=Mock())

#             filters = {'q': 'Golden Retriever'}
#             result = AnimalService.list_animals(filters)

#             # 驗證關鍵字搜尋邏輯被觸發
#             assert mock_or.called  # or_ 函數被調用
#             assert mock_animal.name.like.called  # name 欄位被搜尋
#             assert 'animals' in result

#     def test_region_filter_logic(self, app_context, mock_db):
#         """測試地區篩選邏輯"""
#         mock_pagination = Mock()
#         mock_pagination.items = []
#         mock_pagination.total = 0

#         with patch('app.services.animal_service.Animal') as mock_animal, \
#              patch('app.services.animal_service.exists') as mock_exists, \
#              patch('app.services.animal_service.or_') as mock_or:

#             mock_animal.query.filter_by.return_value.filter.return_value.order_by.return_value.paginate.return_value = mock_pagination
#             mock_exists.return_value.where.return_value = Mock()

#             filters = {'region': '台北市'}
#             result = AnimalService.list_animals(filters)

#             # 驗證地區篩選邏輯被觸發
#             assert mock_exists.called  # exists() 子查詢被調用
#             assert mock_or.called  # 用於合併 shelter 和 user 地區條件
#             assert 'animals' in result

#     def test_per_page_limit_enforcement(self, app_context, mock_db):
#         """測試分頁限制邏輯"""
#         mock_pagination = Mock()
#         mock_pagination.items = []
#         mock_pagination.total = 0

#         with patch('app.services.animal_service.Animal') as mock_animal:
#             mock_animal.query.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination

#             filters = {'per_page': 200}  # 超過限制
#             result = AnimalService.list_animals(filters)

#             # 驗證 paginate 被調用且 per_page 被限制為 100
#             mock_animal.query.filter_by.return_value.order_by.return_value.paginate.assert_called_once_with(
#                 page=1,
#                 per_page=100,  # 應該被限制為 100
#                 error_out=False
#             )
#             assert 'animals' in result

#     def test_multiple_conditions_and_logic(self, app_context, mock_db):
#         """測試多條件AND邏輯"""
#         mock_pagination = Mock()
#         mock_pagination.items = []
#         mock_pagination.total = 0

#         with patch('app.services.animal_service.Animal') as mock_animal, \
#              patch('app.services.animal_service.func') as mock_func, \
#              patch('app.services.animal_service.or_') as mock_or, \
#              patch('app.services.animal_service.db') as mock_db_patch:

#             # 建立複雜的調用鏈
#             mock_filter_by = Mock()
#             mock_filter_by.filter_by.return_value = mock_filter_by  # species
#             mock_filter_by.filter.return_value = mock_filter_by  # age filters
#             mock_filter_by.order_by.return_value.paginate.return_value = mock_pagination
            
#             mock_animal.query.filter_by.return_value = mock_filter_by
#             mock_db_patch.engine.name = 'sqlite'
            
#             # Mock Animal 的欄位屬性
#             mock_animal.name.like = Mock(return_value=Mock())
#             mock_animal.description.like = Mock(return_value=Mock())
#             mock_animal.breed.like = Mock(return_value=Mock())

#             filters = {
#                 'species': 'DOG',
#                 'sex': 'MALE', 
#                 'min_age': 1,
#                 'max_age': 3,
#                 'q': 'cute'
#             }
#             result = AnimalService.list_animals(filters)

#             # 驗證多個篩選條件都被應用
#             assert mock_filter_by.filter_by.call_count >= 2  # species, sex
#             assert mock_func.julianday.called  # 年齡篩選
#             assert mock_or.called  # 關鍵字搜尋
#             assert 'animals' in result

#     def test_invalid_species_validation(self, app_context, mock_db):
#         """測試無效物種驗證"""
#         filters = {'species': 'INVALID_ANIMAL'}
        
#         with pytest.raises(ValidationError) as exc_info:
#             AnimalService.list_animals(filters)
        
#         assert '無效的物種值' in str(exc_info.value)

#     def test_invalid_sex_validation(self, app_context, mock_db):
#         """測試無效性別驗證"""
#         filters = {'sex': 'INVALID_SEX'}
        
#         with pytest.raises(ValidationError) as exc_info:
#             AnimalService.list_animals(filters)
        
#         assert '無效的性別值' in str(exc_info.value)

#     def test_empty_filters_default_behavior(self, app_context, mock_db):
#         """測試空篩選預設行為"""
#         mock_pagination = Mock()
#         mock_pagination.items = []
#         mock_pagination.total = 0

#         with patch('app.services.animal_service.Animal') as mock_animal:
#             mock_animal.query.filter_by.return_value.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination

#             filters = {}
#             result = AnimalService.list_animals(filters)

#             # 驗證預設狀態篩選被應用
#             assert 'animals' in result

#     def test_sex_filter_conversion(self, app_context, mock_db):
#         """測試性別篩選轉換"""
#         mock_pagination = Mock()
#         mock_pagination.items = []
#         mock_pagination.total = 0

#         with patch('app.services.animal_service.Animal') as mock_animal:
#             mock_animal.query.filter_by.return_value.filter_by.return_value.order_by.return_value.paginate.return_value = mock_pagination

#             filters = {'sex': 'FEMALE'}
#             result = AnimalService.list_animals(filters)

#             # 驗證性別篩選被正確套用
#             assert 'animals' in result

#     def test_keyword_special_character_handling(self, app_context, mock_db):
#         """測試特殊字符處理"""
#         mock_pagination = Mock()
#         mock_pagination.items = []
#         mock_pagination.total = 0

#         with patch('app.services.animal_service.Animal') as mock_animal, \
#              patch('app.services.animal_service.or_') as mock_or:

#             mock_animal.query.filter_by.return_value.filter.return_value.order_by.return_value.paginate.return_value = mock_pagination
            
#             # Mock Animal 的欄位屬性
#             mock_animal.name.like = Mock(return_value=Mock())
#             mock_animal.description.like = Mock(return_value=Mock())
#             mock_animal.breed.like = Mock(return_value=Mock())

#             # 測試包含特殊字元的搜索
#             filters = {'q': "小白's 100% 可愛貓咪"}
#             result = AnimalService.list_animals(filters)

#             # 驗證關鍵字搜尋邏輯被觸發
#             assert mock_or.called  # or_ 函數被調用
#             assert 'animals' in result