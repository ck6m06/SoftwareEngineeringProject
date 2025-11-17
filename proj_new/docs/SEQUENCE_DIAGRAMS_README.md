# 後端循序圖文檔 (Backend Sequence Diagrams)

本文檔包含兩個核心業務流程的 PlantUML 循序圖，詳細描述了用戶與各 Python 模組之間的互動。

## 📋 目錄

1. [個人送養發佈流程](#1-個人送養發佈流程)
2. [領養申請提交流程](#2-領養申請提交流程)
3. [架構設計原則](#3-架構設計原則)
4. [如何查看循序圖](#4-如何查看循序圖)

---

## 1. 個人送養發佈流程

**檔案**: `sequence-personal-adoption.puml`

### 流程概述

描述一般會員從建立動物資料、上傳圖片、更新資料到提交審核，最後由管理員發布的完整流程。

### 主要參與者

- **一般會員 (Owner)**: 個人送養者
- **管理員 (Admin)**: 系統管理員

### 涉及的 Python 模組

| 模組 | 職責 |
|------|------|
| `animals.py` (Blueprint) | 動物 API 端點，處理 HTTP 請求與回應 |
| `Animal` (Model) | 動物資料模型，ORM 映射 |
| `User` (Model) | 用戶資料模型，角色權限管理 |
| `AnimalImage` (Model) | 動物圖片資料模型 |
| `minio_helper.py` (Utils) | MinIO 對象存儲操作工具 |

### 流程階段

1. **建立動物資料 (草稿狀態)**
   - 用戶提交動物基本資訊
   - 系統根據用戶角色決定動物類型 (個人送養 vs 收容所)
   - 初始狀態設為 `DRAFT`

2. **上傳動物圖片**
   - 接收 base64 編碼的圖片
   - 上傳到 MinIO 對象存儲
   - 建立圖片記錄並關聯到動物

3. **更新動物資料**
   - 權限驗證（只有擁有者可編輯）
   - 更新動物屬性

4. **提交審核**
   - 狀態從 `DRAFT` → `SUBMITTED`
   - 權限檢查與狀態驗證

5. **管理員審核發布**
   - 管理員權限驗證
   - 狀態從 `SUBMITTED` → `PUBLISHED`

### 權限控制邏輯

```python
# 個人送養動物權限檢查
if animal.owner_id and animal.owner_id == current_user_id:
    has_permission = True

# 收容所動物權限檢查
elif animal.shelter_id and user.role == UserRole.SHELTER_MEMBER 
     and user.primary_shelter_id == animal.shelter_id:
    has_permission = True

# 管理員權限
elif user.role == UserRole.ADMIN:
    has_permission = True
```

### Decouple 設計原則

- ✅ **分層架構**: Blueprint (API) → Model (ORM) → Database
- ✅ **工具類解耦**: `minio_helper.py` 獨立處理存儲邏輯
- ✅ **JWT 認證中介層**: `@jwt_required()` 裝飾器統一認證
- ✅ **狀態機管理**: 清晰的狀態轉換流程

---

## 2. 領養申請提交流程

**檔案**: `sequence-adoption-application.puml`

### 流程概述

描述申請人提交領養申請、送養人審核、系統發送通知和 Email 的完整流程，包含異步任務處理。

### 主要參與者

- **申請人 (Applicant)**: 想要領養動物的一般會員
- **送養人 (Rehome Owner)**: 動物擁有者或收容所成員

### 涉及的 Python 模組

| 模組 | 職責 |
|------|------|
| `applications.py` (Blueprint) | 領養申請 API 端點 |
| `Application` (Model) | 申請資料模型 |
| `Animal` (Model) | 動物資料模型 |
| `User` (Model) | 用戶資料模型 |
| `notification_service.py` (Service) | 通知業務邏輯服務 |
| `Notification` (Model) | 站內通知資料模型 |
| `email_tasks.py` (Celery Task) | 異步 Email 發送任務 |
| `audit_service.py` (Service) | 審計日誌服務 |
| `AuditLog` (Model) | 審計記錄資料模型 |

### 流程階段

#### 階段 1: 提交領養申請

**業務規則驗證**:
- ✅ 只有 `GENERAL_MEMBER` 可以申請
- ✅ 動物狀態必須是 `PUBLISHED`
- ✅ 動物未被領養 (`status != ADOPTED`)
- ✅ 申請人不是刊登者本人
- ✅ 沒有其他人的待審核申請
- ✅ 申請人未重複申請

**冪等性設計**:
```http
POST /api/applications
Headers:
  Idempotency-Key: unique-uuid-string
```
如果找到相同 `idempotency_key` 的申請，直接返回該申請，避免重複提交。

#### 階段 2: 發送通知給動物擁有者

- 建立站內通知 (`Notification` model)
- 通知類型: `application_submitted`
- 確定接收者:
  - 個人送養 → `animal.owner_id`
  - 收容所動物 → `shelter.primary_account_user_id`

#### 階段 3: 送養人審核申請

**權限邏輯**:
```python
# 個人送養: 只有動物擁有者可審核
if animal.owner_id and animal.owner_id == current_user_id:
    has_permission = True

# 收容所動物: 收容所成員可審核
elif animal.shelter_id and user.role == UserRole.SHELTER_MEMBER 
     and user.primary_shelter_id == animal.shelter_id:
    has_permission = True

# 注意: 管理員無權審核領養申請
```

**審核動作**:
- `approve`: 申請狀態 → `APPROVED`，動物狀態 → `ADOPTED`
- `reject`: 申請狀態 → `REJECTED`

**樂觀鎖 (Optimistic Locking)**:
```python
# 檢查 version 避免併發衝突
if 'version' in data:
    if application.version != data['version']:
        abort(409, message='申請已被其他人修改，請重新載入')

application.version += 1
```

#### 階段 4: 記錄審計日誌

- 通過 `audit_service` 統一記錄
- 記錄內容:
  - 操作類型: `application.review`
  - 執行者: `reviewer_id`
  - 目標: `application_id`
  - 狀態變更: `before_state` → `after_state`

#### 階段 5: 發送通知給申請人

- 站內通知類型:
  - `application_approved`: 申請通過
  - `application_rejected`: 申請被拒絕

#### 階段 6-7: 異步 Email 發送

**Celery 任務流程**:
```python
# 將任務加入 Redis 隊列
send_application_notification_email_task.delay(
    recipient_email, animal_name, status, review_notes, contact_info
)
```

**重試機制**:
- 最多重試 3 次
- 指數退避: 60 秒 → 120 秒 → 240 秒

**Email 內容**:
- `approved`: 包含送養人聯絡資訊 (email, phone)
- `rejected`: 包含拒絕原因
- `under_review`: 審核中通知

### Decouple 設計原則

- ✅ **服務層解耦**: `notification_service`, `audit_service` 獨立業務邏輯
- ✅ **異步任務**: Celery + Redis 處理耗時操作
- ✅ **冪等性設計**: `Idempotency-Key` 防止重複提交
- ✅ **樂觀鎖**: `version` 欄位防止併發衝突
- ✅ **通知系統分離**: 站內通知 + Email 通知雙軌制
- ✅ **審計追蹤**: 統一的審計日誌記錄
- ✅ **重試機制**: Celery 自動重試與指數退避

---

## 3. 架構設計原則

### 3.1 分層架構 (Layered Architecture)

```
┌─────────────────────────────────────┐
│   API Layer (Blueprints)            │  ← HTTP 請求處理
├─────────────────────────────────────┤
│   Service Layer (Services)          │  ← 業務邏輯
├─────────────────────────────────────┤
│   Data Access Layer (Models)        │  ← ORM 模型
├─────────────────────────────────────┤
│   Database Layer (PostgreSQL)       │  ← 資料持久化
└─────────────────────────────────────┘
```

### 3.2 解耦原則 (Decoupling Principles)

| 原則 | 實現方式 |
|------|---------|
| **關注點分離** | Blueprint 處理 HTTP，Service 處理業務邏輯，Model 處理資料 |
| **依賴注入** | 通過 Flask 的 `db` 和 `current_app` 注入依賴 |
| **介面隔離** | 每個 Service 提供清晰的公開方法 |
| **單一職責** | 每個模組只負責一項核心功能 |

### 3.3 異步處理模式

```python
# 同步操作 (影響響應時間)
ApplicationsBlueprint -> DB: 保存申請
ApplicationsBlueprint -> NotificationService: 建立通知

# 異步操作 (不阻塞響應)
ApplicationsBlueprint -> Celery: 排程 Email 任務
Celery Worker -> Email Service: 發送郵件 (背景執行)
```

### 3.4 錯誤處理策略

- **審計日誌失敗**: 不影響主流程，記錄錯誤日誌
- **通知發送失敗**: 不影響主流程，記錄錯誤日誌
- **Email 發送失敗**: Celery 自動重試，最終失敗記錄到任務狀態

---

## 4. 如何查看循序圖

### 方法 1: VS Code 擴充功能

1. 安裝 **PlantUML** 擴充功能
2. 安裝 **Graphviz** (`choco install graphviz` 或從官網下載)
3. 打開 `.puml` 檔案
4. 按 `Alt + D` 預覽圖表

### 方法 2: 線上編輯器

訪問 [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)，複製 `.puml` 檔案內容貼上即可。

### 方法 3: 命令列生成圖片

```bash
# 安裝 PlantUML
npm install -g node-plantuml

# 生成 PNG
puml generate sequence-personal-adoption.puml
puml generate sequence-adoption-application.puml
```

---

## 📚 相關文件

- [API 文檔](./api/)
- [開發指南](./development.md)
- [資料庫 Schema](./database-schema.md)

---

## 🔄 更新記錄

| 日期 | 更新內容 |
|------|---------|
| 2025-11-15 | 初次建立，包含個人送養發佈與領養申請提交兩個循序圖 |

---

**Author**: GitHub Copilot (Claude Sonnet 4.5)  
**Last Updated**: 2025-11-15
