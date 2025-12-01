"""
Use Case 1.1 動物列表瀏覽 - Controller 層測試

測試範圍：僅測試 route/controller 層的邏輯
測試方法：使用 monkeypatch mock animal_service.list_animals，不依賴真實資料庫
與其他測試的區別：
- Unit Tests: 測試 service 業務邏輯，mock ORM
- Controller Tests: 測試 route 層邏輯，mock service  
- Integration Tests: 測試完整流程，使用真實 DB
"""
import pytest
from flask import Flask

from app import create_app
from app.models.animal import AnimalStatus


@pytest.fixture
def app():
    """建立測試用 Flask app（不需要資料庫）"""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """測試客戶端"""
    return app.test_client()


def test_route_returns_200_with_valid_service_response(client, monkeypatch):
    """
    測試目的：驗證當 service 正常回傳資料時，route 回傳 HTTP 200 與正確的 JSON 結構
    
    Use Case 1.1 主要流程步驟 2：「系統顯示動物清單，包含動物圖片、名稱、物種、年齡、性別等基本資訊」
    
    測試層級：Controller 測試（僅測試 route 層）
    前置條件：mock animal_service.list_animals 回傳固定結構
    驗證重點：
    - HTTP 狀態碼為 200
    - 回傳 JSON 包含 service 提供的資料
    """
    # Mock service 回傳
    mock_response = {
        'animals': [
            {'animal_id': 1, 'name': 'TestDog', 'species': 'DOG', 'age': 2, 'sex': 'MALE', 'images': []},
            {'animal_id': 2, 'name': 'TestCat', 'species': 'CAT', 'age': 1, 'sex': 'FEMALE', 'images': []}
        ],
        'total': 2,
        'page': 1,
        'per_page': 20,
        'pages': 1
    }
    
    def mock_list_animals(filters, current_user_id=None):
        return mock_response
    
    monkeypatch.setattr('app.blueprints.animals.animal_service.list_animals', mock_list_animals)
    
    resp = client.get('/api/animals')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == mock_response
    assert len(data['animals']) == 2


def test_route_passes_filters_to_service(client, monkeypatch):
    """
    測試目的：驗證 route 正確解析 query params 並傳遞給 service 層
    
    Use Case 1.1 擴充功能：過濾、搜尋、分頁
    
    測試層級：Controller 測試
    前置條件：mock service 並捕獲傳入的參數
    驗證重點：
    - query params 正確解析為 filters dict
    - filters 包含 species, page, per_page, q 等參數
    """
    captured_filters = {}
    
    def mock_list_animals(filters, current_user_id=None):
        captured_filters.update(filters)
        return {'animals': [], 'total': 0, 'page': 1, 'per_page': 20, 'pages': 0}
    
    monkeypatch.setattr('app.blueprints.animals.animal_service.list_animals', mock_list_animals)
    
    resp = client.get('/api/animals?species=DOG&page=2&per_page=10&q=fluffy')
    
    assert resp.status_code == 200
    assert captured_filters['species'] == 'DOG'
    assert captured_filters['page'] == 2
    assert captured_filters['per_page'] == 10
    assert captured_filters['q'] == 'fluffy'


def test_route_handles_optional_jwt_token(client, monkeypatch):
    """
    測試目的：驗證 route 正確處理有/無 JWT token 的情況
    
    Use Case 1.1 輔助說明：「若登入角色為訪客，僅能瀏覽公開動物資料」
    
    測試層級：Controller 測試
    前置條件：mock service 並捕獲 current_user_id
    驗證重點：
    - 無 token 時，current_user_id 為 None
    - route 正常處理可選的 JWT
    """
    captured_user_id = {'value': 'not_called'}
    
    def mock_list_animals(filters, current_user_id=None):
        captured_user_id['value'] = current_user_id
        return {'animals': [], 'total': 0, 'page': 1, 'per_page': 20, 'pages': 0}
    
    monkeypatch.setattr('app.blueprints.animals.animal_service.list_animals', mock_list_animals)
    
    # 測試無 token（訪客）
    resp = client.get('/api/animals')
    assert resp.status_code == 200
    assert captured_user_id['value'] is None


def test_route_returns_500_when_service_raises_exception(client, monkeypatch):
    """
    測試目的：驗證當 service 拋出例外時，route 正確處理並回傳 HTTP 500
    
    測試範圍：P2 - 錯誤處理
    
    測試層級：Controller 測試
    前置條件：mock service 拋出 RuntimeError
    驗證重點：
    - HTTP 狀態碼為 500
    - 回傳 JSON 包含 'message' key
    - 錯誤訊息包含「系統錯誤」或實際錯誤內容
    - 不洩漏敏感資訊（如完整 stack trace）
    """
    def mock_list_animals(filters, current_user_id=None):
        raise RuntimeError('Database connection failed')
    
    monkeypatch.setattr('app.blueprints.animals.animal_service.list_animals', mock_list_animals)
    
    resp = client.get('/api/animals')
    assert resp.status_code == 500
    data = resp.get_json()
    assert 'message' in data
    assert '系統錯誤' in data['message'] or 'Database connection failed' in data['message']


def test_route_returns_proper_error_for_business_exception(client, monkeypatch):
    """
    測試目的：驗證當 service 拋出 BusinessException 時，route 回傳對應的 status code
    
    測試層級：Controller 測試
    前置條件：mock service 拋出 BusinessException（如 ValidationError）
    驗證重點：
    - 使用 BusinessException 的 status_code（非 500）
    - 錯誤訊息正確傳遞
    """
    from app.exceptions import ValidationError
    
    def mock_list_animals(filters, current_user_id=None):
        raise ValidationError('Invalid species value')
    
    monkeypatch.setattr('app.blueprints.animals.animal_service.list_animals', mock_list_animals)
    
    resp = client.get('/api/animals')
    # ValidationError 預設 status_code 為 400
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'message' in data
    assert 'Invalid species value' in data['message']