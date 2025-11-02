#!/usr/bin/env python
import pytest

# This is a legacy interactive API test script intended to be run as a
# standalone script. Pytest will attempt to collect functions starting with
# `test_` which breaks automated runs because this module's functions expect
# positional arguments. Skip this module during automated pytest runs.
pytest.skip("Skip legacy interactive API script during automated test runs", allow_module_level=True)
"""
Backend API 完整測試腳本
測試所有主要 API endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

# 測試結果統計
results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def test_endpoint(name, method, url, data=None, headers=None, expected_status=None):
    """測試單一 endpoint"""
    try:
        print(f'\n🧪 測試: {name}')
        print(f'   {method} {url}')
        
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f'Unsupported method: {method}')
        
        status_ok = expected_status is None or response.status_code == expected_status
        
        if status_ok:
            print(f'   ✅ 狀態碼: {response.status_code}')
            results['passed'] += 1
            return response
        else:
            print(f'   ❌ 狀態碼: {response.status_code} (預期: {expected_status})')
            print(f'   回應: {response.text[:200]}')
            results['failed'] += 1
            results['errors'].append(f'{name}: {response.status_code}')
            return None
            
    except Exception as e:
        print(f'   ❌ 錯誤: {str(e)}')
        results['failed'] += 1
        results['errors'].append(f'{name}: {str(e)}')
        return None

def main():
    print('=' * 60)
    print('🚀 Backend API 測試開始')
    print('=' * 60)
    
    # ========== 1. Auth API ==========
    print('\n' + '=' * 60)
    print('📝 1. Authentication API')
    print('=' * 60)
    
    # 註冊測試帳號
    register_data = {
        'email': f'test_{datetime.now().timestamp()}@test.com',
        'password': 'Test123456',
        'username': 'testuser'
    }
    test_endpoint('註冊新帳號', 'POST', f'{BASE_URL}/auth/register', register_data, expected_status=201)
    
    # 登入
    login_data = {'email': 'admin@test.com', 'password': 'Admin123'}
    login_response = test_endpoint('管理員登入', 'POST', f'{BASE_URL}/auth/login', login_data, expected_status=200)
    
    if not login_response:
        print('\n❌ 登入失敗,無法繼續測試需要驗證的 API')
        return
    
    token = login_response.json().get('access_token')
    auth_headers = {'Authorization': f'Bearer {token}'}
    
    # 獲取當前用戶
    test_endpoint('獲取當前用戶', 'GET', f'{BASE_URL}/auth/me', headers=auth_headers, expected_status=200)
    
    # ========== 2. Users API ==========
    print('\n' + '=' * 60)
    print('👥 2. Users API')
    print('=' * 60)
    
    test_endpoint('獲取用戶資料', 'GET', f'{BASE_URL}/users/1', headers=auth_headers, expected_status=200)
    
    # ========== 3. Animals API ==========
    print('\n' + '=' * 60)
    print('🐾 3. Animals API')
    print('=' * 60)
    
    animals_response = test_endpoint('獲取動物列表', 'GET', f'{BASE_URL}/animals?status=PUBLISHED&page=1&per_page=10', expected_status=200)
    
    # 如果有動物,測試獲取詳情
    if animals_response and animals_response.json().get('animals'):
        first_animal = animals_response.json()['animals'][0]
        animal_id = first_animal['animal_id']
        test_endpoint('獲取動物詳情', 'GET', f'{BASE_URL}/animals/{animal_id}', expected_status=200)
    else:
        print('   ⚠️ 跳過動物詳情測試 (無動物資料)')

    
    # ========== 4. Applications API ==========
    print('\n' + '=' * 60)
    print('📋 4. Applications API')
    print('=' * 60)
    
    test_endpoint('獲取申請列表', 'GET', f'{BASE_URL}/applications?page=1&per_page=10', headers=auth_headers, expected_status=200)
    
    # ========== 5. Shelters API ==========
    print('\n' + '=' * 60)
    print('🏠 5. Shelters API')
    print('=' * 60)
    
    test_endpoint('獲取收容所列表', 'GET', f'{BASE_URL}/shelters?page=1&per_page=10', expected_status=200)
    test_endpoint('獲取收容所詳情', 'GET', f'{BASE_URL}/shelters/1', expected_status=200)
    
    # ========== 6. Notifications API ==========
    print('\n' + '=' * 60)
    print('🔔 6. Notifications API')
    print('=' * 60)
    
    test_endpoint('獲取未讀通知數', 'GET', f'{BASE_URL}/notifications/unread-count', headers=auth_headers, expected_status=200)
    test_endpoint('獲取通知列表', 'GET', f'{BASE_URL}/notifications?page=1&per_page=10', headers=auth_headers, expected_status=200)
    
    # ========== 7. Admin API ==========
    print('\n' + '=' * 60)
    print('⚙️ 7. Admin API')
    print('=' * 60)
    
    test_endpoint('獲取審計日誌', 'GET', f'{BASE_URL}/admin/audit?page=1&per_page=10', headers=auth_headers, expected_status=200)
    test_endpoint('獲取統計資料', 'GET', f'{BASE_URL}/admin/statistics', headers=auth_headers, expected_status=200)
    
    # ========== 8. 登出 ==========
    print('\n' + '=' * 60)
    print('🚪 8. Logout')
    print('=' * 60)
    
    test_endpoint('登出', 'POST', f'{BASE_URL}/auth/logout', headers=auth_headers, expected_status=200)
    
    # ========== 測試結果 ==========
    print('\n' + '=' * 60)
    print('📊 測試結果摘要')
    print('=' * 60)
    print(f'\n✅ 通過: {results["passed"]} 個測試')
    print(f'❌ 失敗: {results["failed"]} 個測試')
    
    if results['errors']:
        print('\n❌ 失敗的測試:')
        for error in results['errors']:
            print(f'   - {error}')
    
    success_rate = (results['passed'] / (results['passed'] + results['failed']) * 100) if (results['passed'] + results['failed']) > 0 else 0
    print(f'\n📈 成功率: {success_rate:.1f}%')
    
    if success_rate >= 90:
        print('\n🎉 測試結果優秀!')
    elif success_rate >= 70:
        print('\n👍 測試結果良好')
    else:
        print('\n⚠️ 需要修復失敗的 API')
    
    print('\n' + '=' * 60)

if __name__ == '__main__':
    main()
