# 整合測試詳細文檔 - Part 3: Auth Integration Tests

## test_auth_integration.py - 認證系統整合測試（7 個測試）

---

### TestAuthRegistration - 用戶註冊測試類

**測試編號：IT-AUTH-001**

**測試目標**：驗證新用戶成功註冊  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 準備有效的註冊資料（email, username, password）
2. 發送 POST 請求到 `/api/auth/register`
3. 驗證用戶創建成功並返回註冊確認資訊

**測試角色**：訪客  
**測試流程**：
- Request Payload：
  ```json
  {
    "email": "newuser@test.com",
    "username": "newuser",
    "password": "Password123"
  }
  ```
- HTTP 請求：`POST /api/auth/register` with content_type='application/json'
- 驗證斷言：
  - `assert response.status_code == 201`
  - `assert 'pending_id' in data`
  - `assert 'masked_email' in data`
  - `assert 'message' in data`
- 資料庫驗證：
  ```python
  from app.models.pending_registration import PendingRegistration
  pending = PendingRegistration.query.filter_by(
      email='newuser@test.com'
  ).first()
  
  assert pending is not None
  assert pending.email == 'newuser@test.com'
  assert pending.username == 'newuser'
  assert pending.verification_code_hash is not None
  ```
- AC (Acceptance Criteria)：
  - AC #1: 端點已建立且可接受 POST 請求
  - AC #2: 驗證請求正文（email, password, username）
  - AC #3: 資料正確寫入 pending_registrations 表
  - AC #4: 密碼使用 bcrypt 加密
  - AC #5: 返回成功訊息和 pending_id
- 預期行為：用戶註冊請求創建成功，發送驗證碼到郵箱

**測試結果**：✅ 通過

---

**測試編號：IT-AUTH-002**

**測試目標**：驗證重複郵箱無法註冊  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 使用已存在的郵箱地址
2. 嘗試註冊新帳號
3. 驗證返回 409 Conflict

**測試角色**：訪客  
**測試流程**：
- Fixture 準備：
  - `test_user` - 已存在的用戶（email='user@test.com'）
- Request Payload：
  ```json
  {
    "email": "user@test.com",
    "username": "anotheruser",
    "password": "Password123"
  }
  ```
- HTTP 請求：`POST /api/auth/register` with content_type='application/json'
- 驗證斷言：
  - `assert response.status_code == 409`
  - `assert '已被註冊' in data.get('message', '')`
- AC (Acceptance Criteria)：
  - AC #1: 檢測到重複 email
  - AC #2: 返回 409 狀態碼
  - AC #3: 返回清晰的錯誤訊息
- 預期行為：系統拒絕重複郵箱註冊

**測試結果**：✅ 通過

---

### TestAuthLogin - 用戶登入測試類

**測試編號：IT-AUTH-003**

**測試目標**：驗證用戶成功登入並獲取 Token  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 準備有效的登入憑證（email, password）
2. 發送 POST 請求到 `/api/auth/login`
3. 驗證返回 access_token 和 refresh_token

**測試角色**：已註冊且已驗證的用戶  
**測試流程**：
- 測試資料準備：
  ```python
  from app.utils.security import hash_password
  
  user = User(
      email='login@test.com',
      username='loginuser',
      password_hash=hash_password('Password123'),
      role=UserRole.GENERAL_MEMBER,
      verified=True
  )
  db_session.add(user)
  db_session.commit()
  ```
- Request Payload：
  ```json
  {
    "email": "login@test.com",
    "password": "Password123"
  }
  ```
- HTTP 請求：`POST /api/auth/login` with content_type='application/json'
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'access_token' in data`
  - `assert 'refresh_token' in data`
  - `assert data['user']['email'] == 'login@test.com'`
- 預期行為：返回 JWT Token 和用戶資訊

**測試結果**：✅ 通過

---

**測試編號：IT-AUTH-004**

**測試目標**：驗證錯誤密碼無法登入  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 使用正確的 email 但錯誤的密碼
2. 嘗試登入
3. 驗證返回 401 Unauthorized

**測試角色**：訪客  
**測試流程**：
- Fixture 準備：已註冊的用戶
- Request Payload：
  ```json
  {
    "email": "login@test.com",
    "password": "WrongPassword"
  }
  ```
- HTTP 請求：`POST /api/auth/login` with content_type='application/json'
- 驗證斷言：
  - `assert response.status_code == 401`
  - 錯誤訊息包含「密碼錯誤」或類似內容
- 預期行為：系統拒絕錯誤密碼登入

**測試結果**：✅ 通過

---

**測試編號：IT-AUTH-005**

**測試目標**：驗證未驗證用戶無法登入  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 創建未驗證的用戶（verified=False）
2. 嘗試登入
3. 驗證返回錯誤狀態

**測試角色**：未驗證的註冊用戶  
**測試流程**：
- 測試資料準備：
  ```python
  unverified_user = User(
      email='unverified@test.com',
      username='unverified',
      password_hash=hash_password('Password123'),
      role=UserRole.GENERAL_MEMBER,
      verified=False
  )
  db_session.add(unverified_user)
  db_session.commit()
  ```
- Request Payload：
  ```json
  {
    "email": "unverified@test.com",
    "password": "Password123"
  }
  ```
- HTTP 請求：`POST /api/auth/login` with content_type='application/json'
- 驗證斷言：
  - `assert response.status_code in [401, 403]`
  - 錯誤訊息包含「未驗證」或類似內容
- 預期行為：系統拒絕未驗證用戶登入

**測試結果**：✅ 通過

---

### TestAuthMe - 當前用戶資訊測試類

**測試編號：IT-AUTH-006**

**測試目標**：驗證獲取當前登入用戶的資訊  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 使用有效的 Token 發送請求
2. 發送 GET 請求到 `/api/auth/me`
3. 驗證返回當前用戶的完整資訊

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備：
  - `auth_headers` - 有效的認證標頭
  - `test_user` - 當前登入用戶
- HTTP 請求：`GET /api/auth/me` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert data['user_id'] == test_user.user_id`
  - `assert data['email'] == test_user.email`
  - `assert data['username'] == test_user.username`
  - `assert 'password_hash' not in data`（密碼不應該被返回）
- 預期行為：返回當前用戶的個人資訊（不包含敏感欄位）

**測試結果**：✅ 通過

---

**測試編號：IT-AUTH-007**

**測試目標**：驗證無 Token 無法獲取用戶資訊  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 嘗試獲取當前用戶資訊
3. 驗證返回 401 Unauthorized

**測試角色**：訪客（未登入）  
**測試流程**：
- HTTP 請求：`GET /api/auth/me`（無 auth headers）
- 驗證斷言：
  - `assert response.status_code == 401`
- 預期行為：未認證無法獲取用戶資訊

**測試結果**：✅ 通過

---
