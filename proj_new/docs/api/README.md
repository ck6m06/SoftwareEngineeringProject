# API 文檔

## 概述

本 API 使用 RESTful 風格設計，所有請求和回應均使用 JSON 格式。

## 基本資訊

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **Authentication**: Bearer Token (JWT)

## 身份驗證

### 註冊

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "username": "myusername",
  "first_name": "John",
  "last_name": "Doe"
}
```

**回應**:
```json
{
  "message": "註冊成功",
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "username": "myusername",
    "role": "GENERAL_MEMBER"
  }
}
```

### 登入

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**回應**:
```json
{
  "message": "登入成功",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "role": "GENERAL_MEMBER"
  }
}
```

### 刷新 Token

```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

**回應**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 取得當前使用者

```http
GET /auth/me
Authorization: Bearer <access_token>
```

**回應**:
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "username": "myusername",
  "role": "GENERAL_MEMBER",
  "verified": true
}
```

## 通知管理

### 取得通知列表

```http
GET /notifications
Authorization: Bearer <access_token>
```

**查詢參數**:
- `read`: 是否已讀 (true, false)
- `type`: 通知類型
- `page`: 頁碼
- `per_page`: 每頁筆數

**回應**:
```json
{
  "notifications": [
    {
      "notification_id": 1,
      "recipient_id": 1,
      "type": "application_submitted",
      "actor_id": 2,
      "payload": {
        "animal_name": "Lucky",
        "applicant_name": "John"
      },
      "read": false,
      "created_at": "2025-10-26T10:00:00"
    }
  ],
  "total": 10,
  "page": 1,
  "per_page": 20
}
```

### 標記通知為已讀

```http
POST /notifications/{notification_id}/read
Authorization: Bearer <access_token>
```

### 標記全部已讀

```http
POST /notifications/read-all
Authorization: Bearer <access_token>
```

### 刪除通知

```http
DELETE /notifications/{notification_id}
Authorization: Bearer <access_token>
```

## 任務管理

### 取得任務列表

```http
GET /jobs
Authorization: Bearer <access_token>
```

**查詢參數**:
- `status`: 任務狀態 (PENDING, RUNNING, SUCCEEDED, FAILED)
- `type`: 任務類型 (user_data_deletion, data_export, batch_update)

**回應**:
```json
{
  "jobs": [
    {
      "job_id": 1,
      "type": "user_data_deletion",
      "status": "PENDING",
      "created_by": 1,
      "created_at": "2025-10-26T10:00:00"
    }
  ],
  "total": 5
}
```

### 審批任務 (僅管理員)

```http
POST /jobs/{job_id}/approve
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "notes": "已審核通過"
}
```

### 拒絕任務 (僅管理員)

```http
POST /jobs/{job_id}/reject
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "reason": "資料不完整"
}
```

## 管理員功能

### 取得用戶列表 (僅管理員)

```http
GET /admin/users
Authorization: Bearer <access_token>
```

**查詢參數**:
- `search`: 搜尋關鍵字 (用戶名或 Email)
- `role`: 角色篩選 (ADMIN, SHELTER_MEMBER, GENERAL_MEMBER)
- `page`: 頁碼
- `per_page`: 每頁筆數

**回應**:
```json
{
  "users": [
    {
      "user_id": 1,
      "email": "user@example.com",
      "username": "myusername",
      "role": "GENERAL_MEMBER",
      "verified": true,
      "created_at": "2025-01-01T00:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

### 封禁用戶 (僅管理員)

```http
POST /admin/users/{user_id}/ban
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "days": 30,
  "reason": "違反社群規範"
}
```

## 動物管理

### 取得動物列表

```http
GET /animals?species=DOG&page=1&per_page=20
```

**查詢參數**:
- `species`: 物種 (CAT, DOG)
- `sex`: 性別 (MALE, FEMALE, UNKNOWN)
- `status`: 狀態 (PUBLISHED)
- `shelter_id`: 收容所 ID
- `page`: 頁碼
- `per_page`: 每頁筆數

**回應**:
```json
{
  "animals": [
    {
      "animal_id": 1,
      "name": "Lucky",
      "species": "DOG",
      "breed": "混種犬",
      "sex": "MALE",
      "age": 2,
      "status": "PUBLISHED",
      "images": [...]
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

### 取得單一動物

```http
GET /animals/{animal_id}
```

### 建立動物

```http
POST /animals
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Lucky",
  "species": "DOG",
  "breed": "混種犬",
  "sex": "MALE",
  "dob": "2022-01-15",
  "description": "活潑可愛的狗狗",
  "status": "DRAFT"
}
```

**說明**: 
- 預設狀態為 `DRAFT` (草稿)
- 草稿會儲存到資料庫,不會因清除瀏覽器快取而遺失
- 使用 `status: "DRAFT"` 明確指定草稿狀態

### 提交動物審核

```http
POST /animals/{animal_id}/submit
Authorization: Bearer <access_token>
```

**說明**: 將草稿狀態的動物提交審核 (DRAFT → SUBMITTED)

### 更新動物

```http
PATCH /animals/{animal_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "PUBLISHED"
}
```

### 刪除動物

```http
DELETE /animals/{animal_id}
Authorization: Bearer <access_token>
```

## 申請管理

### 建立申請

```http
POST /applications
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "animal_id": 1,
  "type": "ADOPTION",
  "notes": "我非常希望能領養這隻狗狗..."
}
```

**說明**: 
- 成功後會自動發送通知給動物擁有者
- 通知類型: `application_submitted`

### 取得申請列表

```http
GET /applications?status=PENDING
Authorization: Bearer <access_token>
```

**查詢參數**:
- `status`: 申請狀態 (PENDING, APPROVED, REJECTED, UNDER_REVIEW)
- `animal_id`: 動物 ID
- `applicant_id`: 申請人 ID

### 審核申請

```http
POST /applications/{application_id}/review
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "APPROVED",
  "review_notes": "申請條件符合,核准領養"
}
```

**說明**: 
- 審核後會自動發送通知給申請人
- 通知類型: `application_reviewed`

## 通知類型說明

系統支援以下 7 種通知類型:

1. **application_submitted**: 收到新的領養申請
   - 接收者: 動物擁有者
   - 觸發時機: 用戶提交領養申請

2. **application_reviewed**: 申請已審核
   - 接收者: 申請人
   - 觸發時機: 管理員審核申請 (核准/拒絕)

3. **application_under_review**: 申請審核中
   - 接收者: 申請人
   - 觸發時機: 申請被指派給審核人員

4. **rehome_application_received**: 收到送養申請
   - 接收者: 送養人
   - 觸發時機: 有人申請領養送養動物

5. **animal_status_changed**: 動物狀態變更
   - 接收者: 動物擁有者
   - 觸發時機: 動物狀態改變 (草稿→已發布→已下架)

6. **job_completed**: 任務完成
   - 接收者: 任務創建者
   - 觸發時機: 背景任務執行完成

7. **system_notification**: 系統通知
   - 接收者: 指定用戶或全體用戶
   - 觸發時機: 系統廣播訊息

## 軟刪除機制

系統使用軟刪除機制保護資料:

- 用戶刪除帳號時,設定 `deleted_at` 時間戳記
- 軟刪除的帳號無法登入
- 所有查詢自動過濾 `deleted_at IS NULL`
- 管理員可以恢復被刪除的帳號

**恢復帳號 (資料庫操作)**:
```sql
UPDATE users 
SET deleted_at = NULL 
WHERE email = 'user@example.com';
```

## 錯誤處理

API 使用標準 HTTP 狀態碼：

- `200`: 成功
- `201`: 建立成功
- `400`: 請求錯誤
- `401`: 未授權
- `403`: 禁止訪問
- `404`: 資源不存在
- `409`: 衝突
- `500`: 伺服器錯誤

錯誤回應格式：
```json
{
  "error": "錯誤訊息描述"
}
```

## Rate Limiting

API 實作速率限制：
- 每分鐘最多 60 次請求
- 超過限制將返回 `429 Too Many Requests`

## 測試帳號

開發環境提供以下測試帳號:

### 管理員帳號
- **Email**: admin@test.com
- **密碼**: Admin123
- **權限**: 完整管理權限

### 收容所會員
- **Email**: shelter@test.com
- **密碼**: Shelter123
- **權限**: 收容所管理功能

### 一般會員
- **Email**: test@example.com
- **密碼**: Test123
- **權限**: 基本用戶功能

**注意**: 
- 測試帳號僅供開發環境使用
- 生產環境請使用強密碼
- 測試帳號可能會定期重置

## 最近更新 (2025-10-26)

### 新增功能
1. ✅ **通知系統完整實作**
   - 7 種通知類型支援
   - 已讀/未讀狀態管理
   - 自動通知觸發

2. ✅ **任務審批系統**
   - 管理員審批/拒絕任務
   - 審批結果通知
   - 審計日誌記錄

3. ✅ **用戶管理介面**
   - 搜尋、篩選、分頁
   - 用戶封禁功能
   - 角色管理

4. ✅ **草稿儲存改進**
   - 草稿持久化到資料庫
   - 避免重複創建記錄
   - 編輯模式支援

### 修復問題
1. ✅ 通知下拉選單立即關閉問題
2. ✅ 草稿只儲存到 localStorage 問題
3. ✅ AdminUsers.vue 編譯錯誤
4. ✅ 軟刪除帳號登入問題

## 完整 API 文檔

完整的 OpenAPI 規範文檔可在以下位置查看：
- Swagger UI: http://localhost:5000/api/docs
- ReDoc: http://localhost:5000/api/redoc
- OpenAPI JSON: http://localhost:5000/api/openapi.json
