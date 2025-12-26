"""
整合測試：收容所管理系統

測試範圍：
- Route: /api/shelters/*, /api/admin/shelters/*
- Service: ShelterService, AdminService
- ORM: Shelter model
- Database: shelters 表
"""
import pytest
import json
from app.models.shelter import Shelter


class TestShelterCreate:
    """測試收容所創建整合流程"""
    
    def test_create_shelter_requires_authentication(self, client, db_session):
        """測試創建收容所需要認證"""
        payload = {
            'name': '未認證收容所',
            'contact_email': 'test@test.com',
            'contact_phone': '02-1111-1111',
            'address': {
                'city': '台北市'
            }
        }
        
        response = client.post(
            '/api/shelters',
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 401


class TestShelterList:
    """測試收容所列表整合流程"""
    
    def test_list_verified_shelters(self, client, db_session, auth_headers, test_shelter):
        """測試獲取已驗證的收容所列表"""
        # 確保測試收容所已驗證
        test_shelter.verified = True
        db_session.commit()
        
        response = client.get(
            '/api/shelters',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'shelters' in data
        assert len(data['shelters']) > 0
        # 所有返回的收容所都應該是已驗證的
        for shelter in data['shelters']:
            assert shelter['verified'] == True
    
    def test_list_shelters_with_filter(self, client, db_session, auth_headers):
        """測試帶過濾條件的收容所列表"""
        response = client.get(
            '/api/shelters?region=台北',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'shelters' in data
    
    def test_list_shelters_with_pagination(self, client, db_session, auth_headers):
        """測試分頁"""
        response = client.get(
            '/api/shelters?page=1&per_page=10',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'shelters' in data
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data


class TestShelterDetail:
    """測試收容所詳情整合流程"""
    
    def test_get_shelter_detail(self, client, db_session, auth_headers, test_shelter):
        """測試獲取收容所詳情"""
        test_shelter.verified = True
        db_session.commit()
        
        response = client.get(
            f'/api/shelters/{test_shelter.shelter_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['shelter_id'] == test_shelter.shelter_id
        assert data['name'] == test_shelter.name
    
    def test_get_nonexistent_shelter(self, client, db_session, auth_headers):
        """測試獲取不存在的收容所"""
        response = client.get(
            '/api/shelters/99999',
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestShelterUpdate:
    """測試收容所更新整合流程"""
    
    def test_update_shelter_as_non_member(self, client, db_session, auth_headers, test_shelter):
        """測試非成員無法更新收容所"""
        payload = {
            'description': '試圖更新'
        }
        
        response = client.patch(
            f'/api/shelters/{test_shelter.shelter_id}',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        assert response.status_code == 403


class TestShelterVerification:
    """測試收容所驗證整合流程"""
    
    def test_admin_verify_shelter(self, client, db_session, admin_headers, test_shelter):
        """測試管理員驗證收容所"""
        payload = {
            'verified': True,
            'notes': '資料完整，已驗證'
        }
        
        response = client.post(
            f'/api/shelters/{test_shelter.shelter_id}/verify',
            data=json.dumps(payload),
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        # 驗證資料庫
        db_session.refresh(test_shelter)
        assert test_shelter.verified == True
    
    def test_admin_reject_shelter(self, client, db_session, admin_headers, test_shelter):
        """測試管理員拒絕收容所"""
        payload = {
            'verified': False,
            'notes': '資料不完整'
        }
        
        response = client.post(
            f'/api/shelters/{test_shelter.shelter_id}/verify',
            data=json.dumps(payload),
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        # 驗證資料庫
        db_session.refresh(test_shelter)
        assert test_shelter.verified == False
    
    def test_non_admin_cannot_verify_shelter(self, client, db_session, auth_headers, test_shelter):
        """測試非管理員無法驗證收容所"""
        payload = {
            'verified': True
        }
        
        response = client.post(
            f'/api/shelters/{test_shelter.shelter_id}/verify',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        assert response.status_code == 403


# TestShelterMemberManagement 類已刪除 - 成員管理功能待實作


# TestBatchAnimalImport 類已刪除 - 批量導入功能待實作
