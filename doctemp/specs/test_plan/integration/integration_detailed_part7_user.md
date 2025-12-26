# 整合測試計劃 - 用戶管理系統 (User)

## test_user_integration.py - 用戶管理整合測試

### TestUserProfile - 用戶個人資料測試類

**測試編號：IT-USER-001**

**測試目標**：驗證用戶可以獲取自己的完整個人資料  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 使用認證 Token 發送 GET 請求到 `/api/users/{user_id}`
2. 驗證返回完整的個人資料（user_id, email, username）

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備測試用戶和認證標頭（test_user, auth_headers）
- 發送 `GET /api/users/{test_user.user_id}` 帶 headers=auth_headers
- 驗證 response.status_code == 200
- 驗證 data['user_id'] == test_user.user_id
- 驗證 data['email'] == test_user.email
- 驗證 data['username'] == test_user.username

**測試結果**：✅ 通過

---

### TestUserUpdate - 用戶更新測試類

**測試編號：IT-USER-002**

**測試目標**：驗證用戶可以更新自己的個人資料  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 準備更新資料（username, bio）
2. 發送 PATCH 請求到 `/api/users/{user_id}`
3. 驗證資料更新成功

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備測試用戶和認證標頭（test_user, auth_headers）
- 準備更新資料：
  ```json
  {
    "username": "updated_username",
    "bio": "Updated bio"
  }
  ```
- 發送 `PATCH /api/users/{test_user.user_id}` 帶 data=json 和 headers=auth_headers
- 驗證 response.status_code == 200
- 驗證 data['username'] == 'updated_username'
- 刷新資料庫記錄：db_session.refresh(test_user)
- 驗證 test_user.username == 'updated_username'

**測試結果**：✅ 通過

---

**測試編號：IT-USER-003**

**測試目標**：驗證更新 email 需要重新驗證  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 準備新的 email 地址
2. 發送 PATCH 請求更新 email
3. 驗證返回成功但可能需要驗證（200 或 202 Accepted）

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備測試用戶和認證標頭（test_user, auth_headers）
- 準備更新資料：
  ```json
  {
    "email": "newemail@test.com"
  }
  ```
- 發送 `PATCH /api/users/{test_user.user_id}` 帶 data=json 和 headers=auth_headers
- 驗證 response.status_code in [200, 202]
  - 200: 更新成功但標記為未驗證
  - 202: 已接受請求，需要郵件驗證

**測試結果**：✅ 通過

---

**測試編號：IT-USER-004**

**測試目標**：驗證用戶無法更新其他用戶的資料  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 創建另一個用戶
2. 使用當前用戶身份嘗試更新該用戶資料
3. 驗證返回 403 Forbidden 錯誤

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備認證標頭
- 創建其他用戶：
  ```python
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
  ```
- 準備更新資料：
  ```json
  {
    "username": "hacked"
  }
  ```
- 發送 `PATCH /api/users/{other_user.user_id}` 帶 data=json 和 headers=auth_headers
- 驗證 response.status_code == 403

**測試結果**：✅ 通過

---

### TestChangePassword - 修改密碼測試類

**測試編號：IT-USER-005**

**測試目標**：驗證用戶成功修改密碼  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 準備舊密碼和新密碼
2. 發送 PATCH 請求到 `/api/users/{user_id}/password`
3. 驗證密碼修改成功

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備測試用戶
- 設置舊密碼：
  ```python
  from flask_jwt_extended import create_access_token
  from app.utils.security import hash_password
  
  test_user.password_hash = hash_password('OldPassword123')
  db_session.commit()
  
  token = create_access_token(identity=test_user.user_id)
  headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json'
  }
  ```
- 準備修改密碼資料：
  ```json
  {
    "old_password": "OldPassword123",
    "new_password": "NewPassword123"
  }
  ```
- 發送 `PATCH /api/users/{test_user.user_id}/password` 帶 data=json 和 headers
- 驗證 response.status_code == 200

**測試結果**：✅ 通過

---

**測試編號：IT-USER-006**

**測試目標**：驗證舊密碼錯誤時無法修改密碼  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備錯誤的舊密碼
2. 嘗試修改密碼
3. 驗證返回 400 或 401 錯誤

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備測試用戶和認證標頭（test_user, auth_headers）
- 準備修改密碼資料：
  ```json
  {
    "old_password": "WrongPassword",
    "new_password": "NewPassword123"
  }
  ```
- 發送 `PATCH /api/users/{test_user.user_id}/password` 帶 data=json 和 headers=auth_headers
- 驗證 response.status_code in [400, 401]

**測試結果**：✅ 通過

---

### TestAdminUserManagement - 管理員用戶管理測試類

**測試編號：IT-USER-007**

**測試目標**：驗證管理員可以獲取用戶列表  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 使用管理員認證 Token
2. 發送 GET 請求到 `/api/admin/users`
3. 驗證返回用戶列表和總數

**測試角色**：系統管理員  
**測試流程**：
- Fixture 準備管理員用戶和認證標頭（test_admin, admin_headers）
- 發送 `GET /api/admin/users` 帶 headers=admin_headers
- 驗證 response.status_code == 200
- 驗證 'users' in data
- 驗證 'total' in data

**測試結果**：✅ 通過

---

**測試編號：IT-USER-008**

**測試目標**：驗證管理員可以搜尋用戶  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 使用管理員認證 Token
2. 發送帶搜尋參數的 GET 請求到 `/api/admin/users?search=test`
3. 驗證返回符合條件的用戶列表

**測試角色**：系統管理員  
**測試流程**：
- Fixture 準備管理員認證標頭（admin_headers）
- 發送 `GET /api/admin/users?search=test` 帶 headers=admin_headers
- 驗證 response.status_code == 200
- 驗證 'users' in data

**測試結果**：✅ 通過

---

**測試編號：IT-USER-009**

**測試目標**：驗證管理員可以封禁用戶  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 使用管理員認證 Token
2. 準備封禁資料（reason, duration）
3. 發送 POST 請求到 `/api/admin/users/{user_id}/ban`
4. 驗證用戶被封禁且設置 locked_until 時間

**測試角色**：系統管理員  
**測試流程**：
- Fixture 準備管理員認證標頭和測試用戶（admin_headers, test_user）
- 準備封禁資料：
  ```json
  {
    "reason": "違反使用條款",
    "duration": 7
  }
  ```
- 發送 `POST /api/admin/users/{test_user.user_id}/ban` 帶 data=json 和 headers=admin_headers
- 驗證 response.status_code == 200
- 刷新資料庫記錄：db_session.refresh(test_user)
- 驗證 test_user.locked_until is not None

**測試結果**：✅ 通過

---

**測試編號：IT-USER-010**

**測試目標**：驗證管理員可以解除用戶封禁  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 先封禁用戶（設置 locked_until）
2. 使用管理員身份發送解除封禁請求
3. 驗證 locked_until 被清除

**測試角色**：系統管理員  
**測試流程**：
- Fixture 準備管理員認證標頭和測試用戶（admin_headers, test_user）
- 先封禁用戶：
  ```python
  from datetime import datetime, timedelta
  
  test_user.locked_until = datetime.utcnow() + timedelta(days=7)
  db_session.commit()
  ```
- 發送 `POST /api/admin/users/{test_user.user_id}/unban` 帶 headers=admin_headers
- 驗證 response.status_code == 200
- 刷新資料庫記錄：db_session.refresh(test_user)
- 驗證 test_user.locked_until is None

**測試結果**：✅ 通過

---

**測試編號：IT-USER-011**

**測試目標**：驗證非管理員無法封禁用戶  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 使用普通用戶身份
2. 嘗試封禁其他用戶
3. 驗證返回 403 Forbidden 錯誤

**測試角色**：普通用戶  
**測試流程**：
- Fixture 準備普通用戶認證標頭（auth_headers）
- 創建目標用戶：
  ```python
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
  ```
- 準備封禁資料：
  ```json
  {
    "reason": "嘗試封禁"
  }
  ```
- 發送 `POST /api/admin/users/{target_user.user_id}/ban` 帶 data=json 和 headers=auth_headers
- 驗證 response.status_code == 403

**測試結果**：✅ 通過

---

## 📊 User 模組測試統計

- **總測試數**：11 個
- **通過測試**：11 個 ✅ (100%)
- **失敗測試 (xfail)**：0 個
- **跳過測試**：0 個 ⏭️
- **已註解測試**：0 個 💤

**測試覆蓋範圍**：
- ✅ 用戶個人資料查詢
- ✅ 用戶資料更新（含權限檢查）
- ✅ 修改密碼功能（含錯誤密碼驗證）
- ✅ 管理員用戶列表和搜尋
- ✅ 管理員封禁/解除封禁用戶
- ✅ 權限控制（非管理員無法執行管理操作）

