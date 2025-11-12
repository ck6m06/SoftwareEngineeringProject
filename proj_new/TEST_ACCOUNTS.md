# 測試帳號文件 - 貓狗領養平台

## 📋 系統測試帳號列表

**系統 URL**: http://localhost:5173/  
**API URL**: http://localhost:5000/  
**測試日期**: 2025-10-26

---

## 🔑 可用測試帳號

### 1. **管理員帳號 (ADMIN)**

#### 帳號 1 - 主要測試管理員
- **Email**: admin@test.com
- **密碼**: Admin123
- **使用者名稱**: admin
- **身分**: ADMIN (管理員)
- **驗證狀態**: ✅ 已驗證
- **權限**:
  - ✅ 訪問管理後台 (/admin/dashboard)
  - ✅ 審核領養申請 (/admin/applications)
  - ✅ 管理醫療記錄 (/medical-records)
  - ✅ 驗證醫療記錄
  - ✅ 查看任務狀態 (/jobs)
  - ✅ 管理所有動物資料
  - ✅ 管理所有用戶
  - ✅ 查看審計日誌

#### 帳號 2 - 測試用管理員
- **Email**: test@example.com
- **密碼**: (需確認)
- **使用者名稱**: testuser
- **身分**: ADMIN
- **驗證狀態**: ✅ 已驗證

---

### 2. **收容所會員帳號 (SHELTER_MEMBER)**

#### 帳號 1 - 測試收容所 ✅
- **Email**: shelter@test.com
- **密碼**: Shelter123
- **使用者名稱**: shelter_tester
- **身分**: SHELTER_MEMBER (收容所會員)
- **驗證狀態**: ✅ 已驗證
- **關聯收容所**: 測試收容所 (shelter_id: 6)
- **收容所資訊**:
  - 名稱: 測試收容所
  - 地址: 台北市測試區測試路123號
  - 電話: 02-12345678
  - 驗證狀態: ✅ 已驗證
- **權限**:
  - ✅ 管理收容所資料
  - ✅ 新增/編輯動物資料
  - ✅ 管理領養申請
  - ✅ 批次匯入動物資料
  - ✅ 查看任務狀態 (/jobs)
  - ✅ 查看收容所統計

---

**如何建立額外收容所會員帳號**:

\\\sql
-- 方法 1: 將現有帳號升級為收容所會員
UPDATE users 
SET role = 'SHELTER_MEMBER', verified = 1 
WHERE email = 'test_phase1@example.com';

-- 方法 2: 插入新的收容所會員帳號 (需要先生成密碼雜湊)
-- 密碼: Shelter123 的雜湊值需要透過 Flask 生成
\\\

**權限**:
- ✅ 訪問收容所管理頁面 (/shelter/dashboard)
- ✅ 審核領養申請 (/admin/applications)
- ✅ 管理醫療記錄 (/medical-records)
- ✅ 查看任務狀態 (/jobs)
- ✅ 管理所屬收容所的動物資料
- ❌ 無法訪問管理後台

---

### 3. **一般會員帳號 (GENERAL_MEMBER)**

#### 帳號 1 - 已驗證會員
- **Email**: test_final_1761356974@example.com
- **密碼**: (註冊時設定)
- **使用者名稱**: test_final
- **身分**: GENERAL_MEMBER (一般會員)
- **驗證狀態**: ✅ 已驗證
- **權限**:
  - ✅ 瀏覽動物列表 (/animals)
  - ✅ 查看動物詳情 (/animals/:id)
  - ✅ 提交領養申請
  - ✅ 查看我的申請 (/my/applications)
  - ✅ 發佈送養資訊 (/rehome-form)
  - ✅ 查看我的送養 (/my-rehomes)
  - ✅ 查看通知 (/notifications)
  - ❌ 無法訪問管理後台
  - ❌ 無法管理醫療記錄
  - ❌ 無法審核申請

#### 帳號 2 - 已驗證會員
- **Email**: test_verify_1761356994@example.com
- **密碼**: (註冊時設定)
- **使用者名稱**: test_verify_1761356994
- **身分**: GENERAL_MEMBER
- **驗證狀態**: ✅ 已驗證

#### 帳號 3 - Phase 1 測試帳號
- **Email**: test_phase1@example.com
- **密碼**: (註冊時設定)
- **使用者名稱**: yee
- **身分**: GENERAL_MEMBER
- **驗證狀態**: ❌ 未驗證

---

## 🔧 建立新測試帳號

### 方法 1: 透過註冊頁面
1. 訪問 http://localhost:5173/register
2. 填寫註冊資訊
3. 新帳號預設為 GENERAL_MEMBER 角色
4. 需要驗證 email (開發環境可跳過)

### 方法 2: 透過 SQL 直接插入

\\\sql
-- 插入管理員帳號 (密碼: Admin123)
INSERT INTO users (email, username, password_hash, role, verified, created_at, updated_at, failed_login_attempts)
VALUES (
    'newadmin@test.com',
    'newadmin',
    '\\\.xHOGt.zVqYZqJ8vZ.xHOGt.zVqYZqJ8vZ.xHO',  -- 需使用實際雜湊值
    'ADMIN',
    1,
    NOW(),
    NOW(),
    0
);

-- 插入收容所會員 (密碼: Shelter123)
INSERT INTO users (email, username, password_hash, role, verified, created_at, updated_at, failed_login_attempts)
VALUES (
    'shelter@test.com',
    'shelter_staff',
    '\\\$...',  -- 需使用實際雜湊值
    'SHELTER_MEMBER',
    1,
    NOW(),
    NOW(),
    0
);
\\\

### 方法 3: 透過 Python 腳本生成密碼雜湊

\\\python
from werkzeug.security import generate_password_hash

# 生成密碼雜湊
password = "Admin123"
hash = generate_password_hash(password, method='pbkdf2:sha256')
print(hash)
\\\

---

## 📝 測試場景對應帳號

### 場景 1: 管理後台測試
- **使用帳號**: admin@test.com / Admin123
- **測試頁面**: 
  - 管理後台 Dashboard
  - 申請審核管理
  - 醫療記錄管理
  - 任務狀態
  - 動物管理

### 場景 2: 收容所會員測試
- **使用帳號**: (需建立)
- **測試頁面**:
  - 收容所 Dashboard
  - 申請審核
  - 醫療記錄管理
  - 動物管理 (限本所)

### 場景 3: 一般會員測試
- **使用帳號**: test_phase1@example.com (或任意 GENERAL_MEMBER)
- **測試頁面**:
  - 動物瀏覽與搜尋
  - 領養申請流程
  - 我的申請列表
  - 送養發佈
  - 通知中心

### 場景 4: 權限控制測試
- **管理員帳號**: admin@test.com
- **一般會員帳號**: test_phase1@example.com
- **測試目的**: 確認一般會員無法訪問管理功能

---

## 🚨 重要提醒

1. **密碼安全**: 以上密碼僅供測試環境使用，生產環境務必使用強密碼
2. **測試資料**: 這些帳號包含測試資料，可能會被重置
3. **收容所會員**: 目前系統中缺少 SHELTER_MEMBER 測試帳號,需要手動建立
4. **密碼雜湊**: 直接插入 SQL 時需要使用正確的 bcrypt/pbkdf2 雜湊值
5. **Email 驗證**: 開發環境可以透過資料庫直接設定 `verified = 1` 跳過驗證

---

## ⚠️ 常見登入問題

### 問題 1: 帳號被鎖定

**錯誤訊息**: `帳號已被鎖定至 YYYY-MM-DD HH:MM:SS`

**原因**: 連續登入失敗 5 次導致帳號被鎖定 15 分鐘

**解決方法**:

```sql
-- 立即解鎖帳號
UPDATE users 
SET failed_login_attempts = 0, locked_until = NULL 
WHERE email = 'admin@test.com';
```

或等待 15 分鐘後自動解鎖。

### 問題 2: 密碼錯誤

**錯誤訊息**: `Email 或密碼錯誤`

**解決方法**: 
1. 確認密碼正確 (區分大小寫)
2. 使用「忘記密碼」功能重置
3. 直接修改資料庫密碼雜湊值

### 問題 3: 帳號未驗證

**錯誤訊息**: `請先驗證您的 Email`

**解決方法**:

```sql
-- 手動設定為已驗證
UPDATE users 
SET verified = 1 
WHERE email = 'your_email@example.com';
```

---

## 🔄 重置測試帳號密碼

如果忘記密碼，可以透過以下方式重置:

\\\sql
-- 重置為 Admin123
UPDATE users 
SET password_hash = '\\\$...',  -- 需要實際的雜湊值
    password_changed_at = NOW()
WHERE email = 'admin@test.com';
\\\

或使用「忘記密碼」功能: http://localhost:5173/forgot-password

---

**文件版本**: 1.1  
**更新日期**: 2025-10-26  
**維護者**: Development Team

---

## 🆕 近期問題修復記錄

### ✅ 問題: 刪除帳號後還是可以登入 (已修復 - 2025-10-26)

**問題描述**: 用戶申請刪除帳號後 (設定 `deleted_at` 欄位),仍然可以使用舊的 email/password 登入系統,也可以使用舊的 JWT token 訪問 API。

**影響範圍**:
- POST `/api/auth/login` - 未檢查 `deleted_at`
- GET `/api/auth/me` - 未檢查 `deleted_at`

**修復內容**:

1. **登入端點** (`/api/auth/login`):
   ```python
   # 修改前
   user = User.query.filter_by(email=data['email']).first()
   
   # 修改後
   user = User.query.filter_by(email=data['email'], deleted_at=None).first()
   ```

2. **獲取用戶資訊端點** (`/api/auth/me`):
   ```python
   # 修改前
   user = User.query.get(current_user_id)
   
   # 修改後
   user = User.query.filter_by(user_id=current_user_id, deleted_at=None).first()
   ```

**測試結果**:

\\\bash
# 測試步驟
1. 註冊測試帳號: test_delete2@test.com / Test123
2. 登入獲取 token ✅
3. 使用 SQL 軟刪除帳號: UPDATE users SET deleted_at = NOW() WHERE email = 'test_delete2@test.com'
4. 嘗試登入 → ❌ 401 Unauthorized "Email 或密碼錯誤" (正確)
5. 使用舊 token 訪問 /auth/me → ❌ 404 "使用者不存在或已刪除" (正確)
\\\

**相關文件**:
- 修改檔案: `backend/app/blueprints/auth.py`
- 修改行數: Lines 89, 155
- Commit: [待提交]

**後續改進建議**:
- [ ] 實作 JWT Token Blacklist (Redis)
- [ ] 在所有需要用戶資訊的端點統一檢查 `deleted_at`
- [ ] 增加單元測試覆蓋已刪除帳號的場景
- [ ] 考慮實作硬刪除功能 (GDPR 完全刪除)

---

## 🆕 近期問題修復記錄 #2

### ✅ 問題: 測試帳號被軟刪除導致無法登入 (已修復 - 2025-10-26)

**問題描述**: 在測試任務審批功能時,批准了 `user_data_deletion` 任務,導致測試帳號被軟刪除 (設定 `deleted_at` 欄位)。之後所有測試帳號都無法登入,管理後台無法訪問。

**影響範圍**:
- admin@test.com (user_id=24) - 管理員帳號被軟刪除
- test@example.com (user_id=1) - 測試帳號被軟刪除
- AdminDashboard 無法加載 (因為無法登入)

**問題根源**: 
任務審批系統正常運作 - 當批准 `user_data_deletion` 任務時,系統正確執行了軟刪除邏輯 (設定 `deleted_at = NOW()`)。但這導致用於測試的重要帳號被標記為已刪除。

**發現過程**:
1. 用戶報告 "admin dashboard加載錯誤"
2. 檢查編譯錯誤 → 無錯誤
3. 檢查後端日誌 → 無異常
4. 測試登入 API → 所有測試帳號返回 401 Unauthorized
5. 查詢資料庫 → **發現 `deleted_at` 欄位有時間戳記**

**修復方法**:

```sql
-- 恢復所有測試帳號
UPDATE users 
SET deleted_at = NULL 
WHERE email IN (
    'admin@test.com', 
    'test@example.com', 
    'shelter@test.com'
);

-- 確認恢復結果
SELECT user_id, email, role, deleted_at 
FROM users 
WHERE email IN ('admin@test.com', 'test@example.com', 'shelter@test.com');
```

**執行結果**:
```
+--------+--------------------+----------------+------------+
| user_id | email              | role           | deleted_at |
+--------+--------------------+----------------+------------+
| 1      | test@example.com   | ADMIN          | NULL       |
| 24     | admin@test.com     | ADMIN          | NULL       |
| 25     | shelter@test.com   | SHELTER_MEMBER | NULL       |
+--------+--------------------+----------------+------------+
```

**驗證測試**:
```bash
# 1. 測試登入
POST http://localhost:5000/api/auth/login
Body: {"email":"admin@test.com","password":"Admin123"}
結果: ✅ 登入成功,獲得 JWT token

# 2. 測試 AdminDashboard API
GET http://localhost:5000/api/animals?status=SUBMITTED&per_page=5
Headers: Authorization: Bearer {token}
結果: ✅ 返回 0 筆待審核動物

GET http://localhost:5000/api/animals?status=PUBLISHED&per_page=1
結果: ✅ 返回 5 筆已發布動物
```

**相關文件**:
- 問題檔案: 所有測試帳號
- 修復方式: SQL UPDATE
- 修復時間: 2025-10-26 19:45

**經驗教訓**:
- ⚠️ 測試任務審批功能時,避免使用重要測試帳號作為刪除目標
- ⚠️ `user_data_deletion` 任務一旦批准,會立即執行軟刪除邏輯
- ✅ 任務審批系統工作正常 - 正確執行了預期的刪除動作
- ✅ 軟刪除機制工作正常 - auth.py 正確拒絕已刪除帳號登入
- ✅ 通知系統工作正常 - 任務完成後發送了通知

**建議**:
- 為任務審批測試建立專用的測試帳號 (如 `delete_test@example.com`)
- 在批准敏感任務前,確認不會影響系統關鍵帳號
- 考慮在開發環境增加"恢復已刪除帳號"的管理介面

---
