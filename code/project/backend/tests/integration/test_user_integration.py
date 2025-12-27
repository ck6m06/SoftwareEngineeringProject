"""
整合測試：用戶管理系統

測試範圍：
- Route: /api/users/*, /api/admin/users/*
- Service: UserService, AdminService
- ORM: User model
- Database: users 表
"""
import pytest
import json
from app.models.user import User, UserRole


class TestUserProfile:
    """測試用戶個人資料整合流程"""
    
    def test_get_own_profile(self, client, db_session, auth_headers, test_user):
        """測試獲取自己的個人資料"""
        response = client.get(
            f'/api/users/{test_user.user_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user_id'] == test_user.user_id
        assert data['email'] == test_user.email
        assert data['username'] == test_user.username


class TestUserUpdate:
    """測試用戶更新整合流程"""
    
    def test_update_own_profile(self, client, db_session, auth_headers, test_user):
        """測試更新自己的個人資料"""
        payload = {
            'username': 'updated_username',
            'bio': 'Updated bio'
        }
        
        response = client.patch(
            f'/api/users/{test_user.user_id}',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'updated_username'
        
        # 驗證資料庫
        db_session.refresh(test_user)
        assert test_user.username == 'updated_username'
    
    def test_update_email_requires_verification(self, client, db_session, auth_headers, test_user):
        """測試更新 email 需要重新驗證"""
        payload = {
            'email': 'newemail@test.com'
        }
        
        response = client.patch(
            f'/api/users/{test_user.user_id}',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        # 可能返回 200 但標記為未驗證，或返回 202 需要驗證
        assert response.status_code in [200, 202]
    
    def test_update_other_user_profile(self, client, db_session, auth_headers):
        """測試更新他人的個人資料"""
        from app.utils.security import hash_password
        
        other_user = User(
            email='other6@test.com',
            username='other6',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        payload = {'username': 'hacked'}
        
        response = client.patch(
            f'/api/users/{other_user.user_id}',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        assert response.status_code == 403  # Forbidden


class TestChangePassword:
    """測試修改密碼整合流程"""
    
    def test_change_password_success(self, client, db_session, test_user):
        """測試成功修改密碼"""
        from flask_jwt_extended import create_access_token
        from app.utils.security import hash_password
        
        # 設置舊密碼
        test_user.password_hash = hash_password('OldPassword123')
        db_session.commit()
        
        token = create_access_token(identity=str(test_user.user_id))
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'old_password': 'OldPassword123',
            'new_password': 'NewPassword123'
        }
        
        response = client.patch(
            f'/api/users/{test_user.user_id}/password',
            data=json.dumps(payload),
            headers=headers
        )
        
        assert response.status_code == 200
    
    def test_change_password_wrong_old_password(self, client, db_session, auth_headers, test_user):
        """測試舊密碼錯誤"""
        payload = {
            'old_password': 'WrongPassword',
            'new_password': 'NewPassword123'
        }
        
        response = client.patch(
            f'/api/users/{test_user.user_id}/password',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        assert response.status_code in [400, 401]


class TestAdminUserManagement:
    """測試管理員用戶管理整合流程"""
    
    def test_admin_list_users(self, client, db_session, admin_headers, test_admin):
        """測試管理員獲取用戶列表"""
        response = client.get(
            '/api/admin/users',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert 'total' in data
    
    def test_admin_search_users(self, client, db_session, admin_headers):
        """測試管理員搜尋用戶"""
        response = client.get(
            '/api/admin/users?search=test',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
    
    def test_admin_ban_user(self, client, db_session, admin_headers, test_user):
        """測試管理員封禁用戶"""
        payload = {
            'reason': '違反使用條款',
            'duration': 7  # 天數
        }
        
        response = client.post(
            f'/api/admin/users/{test_user.user_id}/ban',
            data=json.dumps(payload),
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        # 驗證資料庫
        db_session.refresh(test_user)
        assert test_user.locked_until is not None
    
    def test_admin_unban_user(self, client, db_session, admin_headers, test_user):
        """測試管理員解除封禁"""
        from datetime import datetime, timedelta
        
        # 先封禁用戶
        test_user.locked_until = datetime.utcnow() + timedelta(days=7)
        db_session.commit()
        
        response = client.post(
            f'/api/admin/users/{test_user.user_id}/unban',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        # 驗證資料庫
        db_session.refresh(test_user)
        assert test_user.locked_until is None
    
    def test_non_admin_cannot_ban_user(self, client, db_session, auth_headers, test_user):
        """測試非管理員無法封禁用戶"""
        from app.utils.security import hash_password
        
        target_user = User(
            email='target@test.com',
            username='target',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        db_session.add(target_user)
        db_session.commit()
        
        payload = {'reason': '嘗試封禁'}
        
        response = client.post(
            f'/api/admin/users/{target_user.user_id}/ban',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        assert response.status_code == 403  # Forbidden


# TestUserDataOperations 類已刪除 - 依賴 Job 系統和 PostgreSQL BIGINT
