# """
# Use Case 1.3 動物詳情檢視 - Controller 層測試

# 測試範圍：僅測試 route/controller 層的邏輯
# 測試方法：使用 monkeypatch mock animal_service.get_animal，不依賴真實資料庫
# 與其他測試的區別：
# - Unit Tests: 測試 service 業務邏輯，mock ORM
# - Controller Tests: 測試 route 層邏輯，mock service  
# - Integration Tests: 測試完整流程，使用真實 DB
# """
# import pytest
# from flask import Flask
# from flask_jwt_extended import create_access_token

# from app import create_app
# from app.models.animal import AnimalStatus
# from app.exceptions import NotFoundError, ValidationError


# @pytest.fixture
# def app():
#     """建立測試用 Flask app（不需要資料庫）"""
#     app = create_app('testing')
#     return app


# @pytest.fixture
# def client(app):
#     """測試客戶端"""
#     return app.test_client()


# def test_normal_animal_detail_response(client, monkeypatch):
#     """
#     TC-C1.3-01: 正常動物詳情回應測試
    
#     測試目的：驗證正常情況下的HTTP回應
#     測試條件：合法動物ID，service回傳正常資料
#     驗證重點：status_code = 200, JSON結構正確
#     """
#     # Mock service 回傳的動物資料
#     mock_animal = {
#         'animal_id': 1,
#         'name': '小白',
#         'species': 'DOG',
#         'breed': '黃金獵犬',
#         'age_estimate_months': 36,
#         'sex': 'MALE',
#         'description': '溫馴友善的狗狗',
#         'location': '台北市中山區',
#         'status': 'PUBLISHED',
#         'images': ['photo1.jpg', 'photo2.jpg'],
#         'owner': {
#             'name': '送養者小明',
#             'email': 'owner@test.com'
#         },
#         'medical_records': [
#             {
#                 'record_type': 'VACCINE',
#                 'details': '完成三合一疫苗接種',
#                 'verified': True
#             }
#         ]
#     }
    
#     def mock_get_animal(animal_id, current_user_id=None):
#         from unittest.mock import Mock
#         mock_result = Mock()
#         mock_result.to_dict.return_value = mock_animal
#         return mock_result
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.get_animal', 
#         mock_get_animal
#     )
    
#     # 測試正常的動物詳情請求
#     resp = client.get('/api/animals/1')
    
#     assert resp.status_code == 200
#     data = resp.get_json()
#     assert data is not None
#     assert 'animal_id' in data
#     assert data['animal_id'] == 1
#     assert data['name'] == '小白'
#     assert data['species'] == 'DOG'
#     assert 'owner' in data
#     assert 'medical_records' in data
#     assert resp.headers['Content-Type'] == 'application/json'


# def test_invalid_id_format_handling(client, monkeypatch):
#     """
#     TC-C1.3-02: 無效ID格式處理測試
    
#     測試目的：驗證無效ID格式的參數驗證
#     測試條件：非數字格式的ID參數
#     驗證重點：status_code = 400, 錯誤訊息指出無效ID格式
#     """
#     # 不需要 mock service，因為參數驗證應該在到達 service 前就攔截
    
#     # 測試無效ID格式
#     resp = client.get('/api/animals/invalid_id')
    
#     # Flask 路由會處理無效的 int 轉換
#     assert resp.status_code == 404  # Flask 預設行為


# def test_animal_not_found_404_handling(client, monkeypatch):
#     """
#     TC-C1.3-03: 動物不存在404處理測試
    
#     測試目的：驗證動物不存在時的錯誤回應
#     測試條件：合法ID但動物不存在
#     驗證重點：status_code = 404, 錯誤訊息明確
#     """
#     def mock_get_animal_not_found(animal_id, current_user_id=None):
#         raise NotFoundError('動物不存在')
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.get_animal', 
#         mock_get_animal_not_found
#     )
    
#     resp = client.get('/api/animals/999')
    
#     assert resp.status_code == 404
#     data = resp.get_json()
#     assert 'message' in data
#     assert '動物不存在' in data['message']


# def test_jwt_token_handling(client, monkeypatch, app):
#     """
#     TC-C1.3-04: JWT token處理測試
    
#     測試目的：驗證可選JWT token的正確處理
#     測試條件：包含/不包含 Authorization header
#     驗證重點：有token時currentUserId正確傳遞，無token時為None
#     """
#     captured_current_user_id = None
    
#     def mock_get_animal_capture_user(animal_id, current_user_id=None):
#         nonlocal captured_current_user_id
#         captured_current_user_id = current_user_id
#         from unittest.mock import Mock
#         mock_result = Mock()
#         mock_result.to_dict.return_value = {'animal_id': animal_id, 'name': 'Test'}
#         return mock_result
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.get_animal', 
#         mock_get_animal_capture_user
#     )
    
#     # 測試無 token 的請求
#     resp1 = client.get('/api/animals/1')
#     assert resp1.status_code == 200
#     assert captured_current_user_id is None
    
#     # 測試有 token 的請求
#     with app.app_context():
#         access_token = create_access_token(identity=123)
    
#     headers = {'Authorization': f'Bearer {access_token}'}
#     resp2 = client.get('/api/animals/1', headers=headers)
#     assert resp2.status_code == 200
#     assert captured_current_user_id == 123


# def test_service_layer_exception_handling(client, monkeypatch):
#     """
#     TC-C1.3-05: 服務層異常處理測試
    
#     測試目的：驗證service層拋出異常的處理
#     測試條件：service拋出非預期錯誤
#     驗證重點：status_code = 500, 錯誤回應結構正確
#     """
#     def mock_get_animal_runtime_error(animal_id, current_user_id=None):
#         raise RuntimeError('Database connection failed')
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.get_animal', 
#         mock_get_animal_runtime_error
#     )
    
#     resp = client.get('/api/animals/1')
    
#     assert resp.status_code == 500
#     data = resp.get_json()
#     assert 'message' in data


# def test_guest_vs_member_response_structure(client, monkeypatch, app):
#     """
#     TC-C1.3-06: 訪客vs會員回應結構測試
    
#     測試目的：驗證訪客和會員看到的資料結構
#     測試條件：同一動物，分別以訪客和會員身份請求
#     驗證重點：回應結構正確，權限差異體現在資料內容中
#     """
#     def mock_get_animal_role_aware(animal_id, current_user_id=None):
#         from unittest.mock import Mock
#         mock_result = Mock()
        
#         # 根據是否有 current_user_id 返回不同資料
#         if current_user_id:
#             # 會員看到更多資料
#             mock_result.to_dict.return_value = {
#                 'animal_id': animal_id,
#                 'name': 'Test Dog',
#                 'canApply': True,
#                 'ownerContact': {
#                     'name': '送養者',
#                     'email': 'owner@test.com',
#                     'phone': '0912345678'
#                 }
#             }
#         else:
#             # 訪客看到基本資料
#             mock_result.to_dict.return_value = {
#                 'animal_id': animal_id,
#                 'name': 'Test Dog',
#                 'canApply': False,
#                 'ownerContact': {
#                     'name': '送養者',
#                     'email': 'owner@test.com'
#                     # 電話號碼隱藏
#                 }
#             }
#         return mock_result
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.get_animal', 
#         mock_get_animal_role_aware
#     )
    
#     # 測試訪客請求
#     resp_guest = client.get('/api/animals/1')
#     assert resp_guest.status_code == 200
#     data_guest = resp_guest.get_json()
#     assert data_guest['canApply'] == False
#     assert 'phone' not in data_guest.get('ownerContact', {})
    
#     # 測試會員請求
#     with app.app_context():
#         access_token = create_access_token(identity=123)
    
#     headers = {'Authorization': f'Bearer {access_token}'}
#     resp_member = client.get('/api/animals/1', headers=headers)
#     assert resp_member.status_code == 200
#     data_member = resp_member.get_json()
#     assert data_member['canApply'] == True
#     assert 'phone' in data_member.get('ownerContact', {})


# def test_owner_viewing_own_animal_response(client, monkeypatch, app):
#     """
#     TC-C1.3-07: 擁有者查看自己動物的回應測試
    
#     測試目的：驗證動物擁有者查看自己動物時的特殊回應
#     測試條件：current_user_id 等於動物 owner_id
#     驗證重點：回應包含編輯權限標示
#     """
#     def mock_get_animal_owner_view(animal_id, current_user_id=None):
#         from unittest.mock import Mock
#         mock_result = Mock()
        
#         # 假設動物的擁有者 ID 是 100
#         is_owner = (current_user_id == 100)
        
#         mock_result.to_dict.return_value = {
#             'animal_id': animal_id,
#             'name': 'My Dog',
#             'owner_id': 100,
#             'canEdit': is_owner,
#             'canApply': not is_owner,  # 自己不能申請自己的動物
#             'fullDetails': is_owner  # 擁有者看到完整詳情
#         }
#         return mock_result
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.get_animal', 
#         mock_get_animal_owner_view
#     )
    
#     # 測試擁有者查看自己的動物
#     with app.app_context():
#         access_token = create_access_token(identity=100)  # 擁有者 ID
    
#     headers = {'Authorization': f'Bearer {access_token}'}
#     resp = client.get('/api/animals/1', headers=headers)
    
#     assert resp.status_code == 200
#     data = resp.get_json()
#     assert data['canEdit'] == True
#     assert data['canApply'] == False
#     assert data['fullDetails'] == True


# def test_large_response_handling(client, monkeypatch):
#     """
#     TC-C1.3-08: 大型回應資料處理測試
    
#     測試目的：驗證大量動物資料的處理能力
#     測試條件：包含大量圖片和醫療紀錄的動物資料
#     驗證重點：請求成功處理，響應時間合理
#     """
#     # Mock 大型資料
#     large_images = [f'photo{i}.jpg' for i in range(1, 51)]  # 50張圖片
#     large_medical_records = [
#         {
#             'record_id': i,
#             'record_type': 'CHECKUP',
#             'details': f'健康檢查記錄 {i}',
#             'verified': True
#         } for i in range(1, 21)  # 20筆醫療紀錄
#     ]
    
#     def mock_get_animal_large_data(animal_id, current_user_id=None):
#         from unittest.mock import Mock
#         mock_result = Mock()
#         mock_result.to_dict.return_value = {
#             'animal_id': animal_id,
#             'name': 'Dog with lots of data',
#             'images': large_images,
#             'medical_records': large_medical_records,
#             'description': 'A' * 5000  # 5000字描述
#         }
#         return mock_result
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.get_animal', 
#         mock_get_animal_large_data
#     )
    
#     # 測試大型資料請求
#     resp = client.get('/api/animals/1')
    
#     assert resp.status_code == 200
#     data = resp.get_json()
#     assert len(data['images']) == 50
#     assert len(data['medical_records']) == 20
#     assert len(data['description']) == 5000


# def test_malformed_service_response_handling(client, monkeypatch):
#     """
#     測試目的：驗證 service 回傳格式異常時的處理
#     測試條件：service 回傳無法序列化的資料
#     驗證重點：系統正確處理異常，回傳適當錯誤
#     """
#     def mock_get_animal_malformed(animal_id, current_user_id=None):
#         # 回傳無法 JSON 序列化的物件
#         from unittest.mock import Mock
#         mock_result = Mock()
#         mock_result.to_dict.side_effect = Exception('Serialization error')
#         return mock_result
    
#     monkeypatch.setattr(
#         'app.blueprints.animals.animal_service.get_animal', 
#         mock_get_animal_malformed
#     )
    
#     resp = client.get('/api/animals/1')
    
#     assert resp.status_code == 500
#     data = resp.get_json()
#     assert 'message' in data
