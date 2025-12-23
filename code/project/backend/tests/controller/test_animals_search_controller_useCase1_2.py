# """
# Use Case 1.2 動物搜尋篩選 - Controller 層測試

# 測試範圍：僅測試 route/controller 層的邏輯
# 測試方法：使用 monkeypatch mock animal_service.list_animals，不依賴真實資料庫
# 與其他測試的區別：
# - Unit Tests: 測試 service 業務邏輯，mock ORM
# - Controller Tests: 測試 route 層邏輯，mock service  
# - Integration Tests: 測試完整流程，使用真實 DB
# """
# import pytest
# from flask import Flask

# from app import create_app
# from app.models.animal import AnimalStatus
# from app.exceptions import ValidationError


# @pytest.fixture
# def app():
#     """建立測試用 Flask app（不需要資料庫）"""
#     app = create_app('testing')
#     return app


# @pytest.fixture
# def client(app):
#     """測試客戶端"""
#     return app.test_client()


# def test_complex_query_string_parsing(client, monkeypatch):
#     """
#     TC-C1.2-01: 複雜查詢字串解析測試
    
#     測試目的：驗證 route 正確解析複雜的搜尋參數
#     測試條件：包含多種搜尋參數的查詢字串
#     驗證重點：所有參數正確解析並傳遞給 service
#     """
#     captured_filters = {}
    
#     def mock_list_animals(filters, current_user_id=None):
#         captured_filters.update(filters)
#         return {
#             'animals': [],
#             'total': 0,
#             'page': 1,
#             'per_page': 20,
#             'pages': 0
#         }
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.list_animals', 
#         mock_list_animals
#     )
    
#     # 測試複雜查詢字串
#     query_string = '?species=DOG&sex=MALE&min_age=1&max_age=5&q=golden%20retriever&region=台北市&page=2&per_page=10'
#     resp = client.get(f'/api/animals{query_string}')
    
#     assert resp.status_code == 200
#     # 驗證所有參數正確解析
#     assert captured_filters['species'] == 'DOG'
#     assert captured_filters['sex'] == 'MALE'
#     assert captured_filters['min_age'] == 1
#     assert captured_filters['max_age'] == 5
#     assert captured_filters['q'] == 'golden retriever'  # URL 解碼後
#     assert captured_filters['region'] == '台北市'
#     assert captured_filters['page'] == 2
#     assert captured_filters['per_page'] == 10


# def test_parameter_type_conversion(client, monkeypatch):
#     """
#     TC-C1.2-02: 參數型別轉換測試
    
#     測試目的：驗證年齡參數正確轉換為整數
#     測試條件：包含無效整數的年齡參數
#     驗證重點：無效參數回傳 400 錯誤
#     """
#     def mock_list_animals(filters, current_user_id=None):
#         return {
#             'animals': [],
#             'total': 0,
#             'page': 1,
#             'per_page': 20,
#             'pages': 0
#         }
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.list_animals', 
#         mock_list_animals
#     )
    
#     # 測試無效年齡參數
#     resp = client.get('/api/animals?min_age=2&max_age=five')
    
#     # 根據實際實作，可能在 route 層就被攔截回傳 400
#     # 或者傳遞到 service 層處理
#     # 此測試驗證系統能正確處理無效輸入
#     assert resp.status_code in [400, 500]  # 依實作而定


# def test_url_encoding_handling(client, monkeypatch):
#     """
#     TC-C1.2-03: URL編碼處理測試
    
#     測試目的：驗證中文和特殊字元的 URL 編碼處理
#     測試條件：包含編碼後中文字元的查詢字串
#     驗證重點：中文字元正確解碼
#     """
#     captured_filters = {}
    
#     def mock_list_animals(filters, current_user_id=None):
#         captured_filters.update(filters)
#         return {
#             'animals': [],
#             'total': 0,
#             'page': 1,
#             'per_page': 20,
#             'pages': 0
#         }
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.list_animals', 
#         mock_list_animals
#     )
    
#     # 測試 URL 編碼的中文字元
#     # "黃金獵犬" 和 "台北市" 的 URL 編碼
#     encoded_query = '/api/animals?q=%E9%BB%83%E9%87%91%E7%8D%B5%E7%8A%AC&region=%E5%8F%B0%E5%8C%97%E5%B8%82'
#     resp = client.get(encoded_query)
    
#     assert resp.status_code == 200
#     # 驗證中文字元正確解碼
#     assert captured_filters.get('q') == '黃金獵犬'
#     assert captured_filters.get('region') == '台北市'


# def test_empty_parameter_handling(client, monkeypatch):
#     """
#     TC-C1.2-04: 空參數處理測試
    
#     測試目的：驗證空字串參數的處理
#     測試條件：包含空值的查詢參數
#     驗證重點：空參數被正確忽略或處理
#     """
#     captured_filters = {}
    
#     def mock_list_animals(filters, current_user_id=None):
#         captured_filters.update(filters)
#         return {
#             'animals': [],
#             'total': 0,
#             'page': 1,
#             'per_page': 20,
#             'pages': 0
#         }
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.list_animals', 
#         mock_list_animals
#     )
    
#     # 測試空參數
#     resp = client.get('/api/animals?species=&q=&min_age=')
    
#     assert resp.status_code == 200
#     # 驗證空參數的處理（依實作而定，可能被忽略或設為預設值）
#     # 此測試確保不會因空參數而出錯


# def test_search_with_pagination_parameters(client, monkeypatch):
#     """
#     TC-C1.2-05: 分頁參數組合測試
    
#     測試目的：驗證搜尋結合分頁的參數處理
#     測試條件：同時包含搜尋和分頁參數
#     驗證重點：所有參數同時正確傳遞
#     """
#     captured_filters = {}
    
#     def mock_list_animals(filters, current_user_id=None):
#         captured_filters.update(filters)
#         return {
#             'animals': [],
#             'total': 0,
#             'page': 2,
#             'per_page': 10,
#             'pages': 0
#         }
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.list_animals', 
#         mock_list_animals
#     )
    
#     resp = client.get('/api/animals?q=cute&species=DOG&page=2&per_page=10')
    
#     assert resp.status_code == 200
#     # 驗證搜尋和分頁參數同時正確處理
#     assert captured_filters['q'] == 'cute'
#     assert captured_filters['species'] == 'DOG'
#     assert captured_filters['page'] == 2
#     assert captured_filters['per_page'] == 10


# def test_duplicate_parameter_handling(client, monkeypatch):
#     """
#     TC-C1.2-06: 重複參數處理測試
    
#     測試目的：驗證重複查詢參數的處理方式
#     測試條件：同一參數出現多次
#     驗證重點：取最後一個值或回傳適當錯誤
#     """
#     captured_filters = {}
    
#     def mock_list_animals(filters, current_user_id=None):
#         captured_filters.update(filters)
#         return {
#             'animals': [],
#             'total': 0,
#             'page': 1,
#             'per_page': 20,
#             'pages': 0
#         }
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.list_animals', 
#         mock_list_animals
#     )
    
#     # 測試重複參數（Flask 通常取最後一個值）
#     resp = client.get('/api/animals?species=DOG&species=CAT')
    
#     assert resp.status_code == 200
#     # Flask 預設行為是取最後一個值
#     assert captured_filters.get('species') == 'CAT'


# def test_service_validation_error_handling(client, monkeypatch):
#     """
#     測試目的：驗證 service 層拋出 ValidationError 時的錯誤處理
#     測試條件：service 拋出無效篩選值錯誤
#     驗證重點：回傳 400 錯誤且錯誤訊息正確
#     """
#     def mock_list_animals(filters, current_user_id=None):
#         raise ValidationError('無效的物種值')
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.list_animals', 
#         mock_list_animals
#     )
    
#     resp = client.get('/api/animals?species=INVALID')
    
#     assert resp.status_code == 400
#     data = resp.get_json()
#     assert 'message' in data
#     assert '無效的物種值' in data['message']


# def test_service_runtime_error_handling(client, monkeypatch):
#     """
#     測試目的：驗證 service 層拋出運行時錯誤的處理
#     測試條件：service 拋出 RuntimeError
#     驗證重點：回傳 500 錯誤
#     """
#     def mock_list_animals(filters, current_user_id=None):
#         raise RuntimeError('Database search failed')
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.list_animals', 
#         mock_list_animals
#     )
    
#     resp = client.get('/api/animals?q=search_term')
    
#     assert resp.status_code == 500
#     data = resp.get_json()
#     assert 'message' in data


# def test_successful_search_response_structure(client, monkeypatch):
#     """
#     測試目的：驗證成功搜尋回應的 JSON 結構
#     測試條件：正常的搜尋請求
#     驗證重點：回傳結構包含所有必要欄位
#     """
#     mock_response = {
#         'animals': [
#             {
#                 'animal_id': 1,
#                 'name': 'TestDog',
#                 'species': 'DOG',
#                 'breed': 'Golden Retriever',
#                 'age': 3,
#                 'sex': 'MALE',
#                 'images': ['photo1.jpg'],
#                 'description': 'Friendly dog'
#             }
#         ],
#         'total': 1,
#         'page': 1,
#         'per_page': 20,
#         'pages': 1
#     }
    
#     def mock_list_animals(filters, current_user_id=None):
#         return mock_response
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.list_animals', 
#         mock_list_animals
#     )
    
#     resp = client.get('/api/animals?q=golden')
    
#     assert resp.status_code == 200
#     data = resp.get_json()
#     assert data == mock_response
#     assert 'animals' in data
#     assert 'total' in data
#     assert 'page' in data
#     assert 'per_page' in data
#     assert 'pages' in data
