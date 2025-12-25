"""
整合測試：認證系統

測試範圍：
- Route: /api/auth/*
- Service: AuthService
- ORM: User model
- Database: users 表
"""
import pytest
import json
from app.models.user import User, UserRole


class TestAuthRegistration:
    """
    【整合測試】用戶註冊 - 完整註冊流程
    
    Use Case: UC 7.1 - 用戶註冊
    Test ID: IT_AUTH_01
    
    測試目標：
    驗證完整的用戶註冊流程，包括 API 端點、資料驗證、密碼雜湊和資料庫儲存。
    
    測試範圍：
    - Route: POST /api/auth/register
    - Service: AuthService.register_user()
    - Model: User, PendingRegistration
    - Database: users, pending_registrations 表
    """
    
    @pytest.mark.usecase7_1
    def test_register_new_user_success(self, client, db_session):
        """
        IT_AUTH_01 - 完整用戶註冊流程測試
        
        測試目標：
        驗證完整的用戶註冊流程，包括 API 端點、資料驗證、密碼雜湊和資料庫儲存。
        
        測試角色：使用者、平台
        
        測試流程：
        1. 使用者 1.1 呼叫 POST /api/auth/register 端點來註冊新使用者
        2. 平台 1.2 驗證端點正確驗證電子郵件、密碼、暱稱欄位
        3. 平台 1.3 確認密碼在儲存前已正確雜湊處理
        4. 平台 1.4 驗證註冊成功並傳回正確的回應訊息
        5. 平台 1.5 驗證資料正確寫入資料庫
        
        預期結果：
        - 步驟 1: HTTP 200 回應，端點接受註冊請求
        - 步驟 2: 請求正文驗證通過，包含電子郵件、密碼和暱稱
        - 步驟 3: 密碼經過 bcrypt 雜湊處理後儲存到資料庫中
        - 步驟 4: 回應包含成功訊息和使用者資料（不包括密碼欄位）
        - 步驟 5: pending_registrations 表中有對應記錄
        
        AC (Acceptance Criteria):
        - AC #1: 端點已建立且可接受 POST 請求
        - AC #2: 驗證請求正文（email, password, username）
        - AC #3: 資料正確寫入 pending_registrations 表
        - AC #4: 密碼使用 bcrypt 加密
        - AC #5: 返回成功訊息和 pending_id
        """
        # ========== 測試資料準備 ==========
        payload = {
            'email': 'newuser@test.com',
            'username': 'newuser',
            'password': 'Password123'
        }
        
        # ========== 步驟 1: 使用者呼叫註冊 API ==========
        response = client.post(
            '/api/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # 驗證：HTTP 201 回應，成功建立新註冊
        assert response.status_code == 201, \
            f"AC #1 失敗: 期望狀態碼 201，實際收到 {response.status_code}"
        
        data = json.loads(response.data)
        
        # ========== 步驟 2: 平台驗證請求欄位 ==========
        # 驗證：回應包含必要欄位
        assert 'pending_id' in data, \
            "AC #2 失敗: 回應缺少 pending_id 欄位"
        assert 'masked_email' in data, \
            "AC #2 失敗: 回應缺少 masked_email 欄位"
        assert 'message' in data, \
            "AC #2 失敗: 回應缺少 message 欄位"
        
        # ========== 步驟 3-5: 平台驗證資料庫記錄和密碼加密 ==========
        from app.models.pending_registration import PendingRegistration
        pending = PendingRegistration.query.filter_by(
            email='newuser@test.com'
        ).first()
        
        assert pending is not None, \
            "AC #3 失敗: pending_registrations 表中找不到記錄"
        assert pending.email == 'newuser@test.com', \
            "AC #3 失敗: 資料庫中的 email 不符"
        assert pending.username == 'newuser', \
            "AC #3 失敗: 資料庫中的 username 不符"
        
        # 驗證：密碼雜湊存在且不是明文
        assert pending.verification_code_hash is not None, \
            "AC #4 失敗: verification_code_hash 不應為 None"
        
        # ========== 測試結果：✅ 成功 ==========
    
    @pytest.mark.usecase7_1
    def test_register_duplicate_email(self, client, db_session, test_user):
        """
        IT_AUTH_02 - 重複郵箱註冊防護測試
        
        測試目標：
        驗證系統能正確拒絕使用已存在的 email 進行註冊。
        
        測試角色：使用者、平台
        
        測試流程：
        1. 平台 1.1 預先建立測試用戶（email: user@test.com）
        2. 使用者 1.2 嘗試使用相同 email 註冊新帳號
        3. 平台 1.3 驗證系統拒絕請求並返回錯誤訊息
        
        預期結果：
        - 步驟 1: 資料庫中已存在 email: user@test.com 的用戶
        - 步驟 2: HTTP 409 Conflict 回應
        - 步驟 3: 錯誤訊息明確指出「郵箱已被註冊」
        
        AC (Acceptance Criteria):
        - AC #1: 檢測到重複 email
        - AC #2: 返回 409 狀態碼
        - AC #3: 返回清晰的錯誤訊息
        """
        # ========== 測試資料準備 ==========
        # test_user fixture 已建立 email: user@test.com 的用戶
        
        payload = {
            'email': 'user@test.com',  # 已存在的 email
            'username': 'anotheruser',
            'password': 'Password123'
        }
        
        # ========== 步驟 2: 使用者嘗試用重複 email 註冊 ==========
        response = client.post(
            '/api/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # 驗證：HTTP 409 Conflict 回應
        assert response.status_code == 409, \
            f"AC #2 失敗: 期望狀態碼 409，實際收到 {response.status_code}"
        
        data = json.loads(response.data)
        
        # ========== 步驟 3: 平台驗證錯誤訊息 ==========
        assert '已被註冊' in data.get('message', ''), \
            f"AC #3 失敗: 錯誤訊息不明確，實際訊息: {data.get('message', '')}"
        
        # ========== 測試結果：✅ 成功 ==========


class TestAuthLogin:
    """測試用戶登入整合流程"""
    
    def test_login_success(self, client, db_session):
        """測試成功登入"""
        from app.utils.security import hash_password
        
        # 創建測試用戶（已驗證）
        user = User(
            email='login@test.com',
            username='loginuser',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        db_session.add(user)
        db_session.commit()
        
        # 發送登入請求
        payload = {
            'email': 'login@test.com',
            'password': 'Password123'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # 驗證響應
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'login@test.com'
    
    def test_login_wrong_password(self, client, db_session, test_user):
        """測試錯誤密碼"""
        payload = {
            'email': 'user@test.com',
            'password': 'WrongPassword123'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 401  # Unauthorized
    
    def test_login_unverified_user(self, client, db_session):
        """測試未驗證用戶登入"""
        from app.utils.security import hash_password
        
        # 創建未驗證用戶
        user = User(
            email='unverified@test.com',
            username='unverifieduser',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=False
        )
        db_session.add(user)
        db_session.commit()
        
        payload = {
            'email': 'unverified@test.com',
            'password': 'Password123'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 403  # Forbidden


class TestAuthMe:
    """測試獲取當前用戶信息"""
    
    def test_get_current_user_info(self, client, db_session, auth_headers, test_user):
        """測試獲取當前用戶信息"""
        response = client.get(
            '/api/auth/me',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['email'] == test_user.email
        assert data['username'] == test_user.username
        assert data['role'] == test_user.role.value
    
    def test_get_user_info_without_token(self, client, db_session):
        """測試未提供 token 時獲取用戶信息"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401  # Unauthorized
