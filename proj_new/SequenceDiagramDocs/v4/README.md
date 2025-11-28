# 後端循序圖說明 (v4)

本目錄包含針對兩個主要使用案例的 PlantUML 循序圖，**專注描述 Blueprint (API層) 與 Service (業務邏輯層) 之間的互動流程**。

## 檔案清單

### 1. sequence-personal-rehome.puml
**使用案例1: 個人送養發佈 (BP-REHOME-002)**

描述一般會員如何建立個人送養資料的完整流程：

**涉及的後端檔案:**
- `animals.py` (Blueprint) - 動物相關 API 端點
- `animal_service.py` - 動物業務邏輯服務
- `permission_service.py` - 權限檢查服務  
- `uploads.py` (Blueprint) - 檔案上傳 API 端點
- `minio_helper.py` - MinIO 物件儲存輔助工具
- Database - 資料庫操作
- MinIO - 物件儲存系統

**主要流程:**
1. 初始化頁面 - 載入使用者的動物列表
2. 上傳動物圖片（支援多張）- 透過 `/uploads/direct` API
3. 上傳醫療記錄檔案 - PDF 或圖片格式
4. 發佈送養資料 - 建立動物記錄（狀態為 DRAFT）
5. 新增動物圖片關聯 - 將上傳的圖片與動物資料關聯
6. 提交審核 - 將狀態從 DRAFT 改為 SUBMITTED

**商業規則:**
- 一般會員建立的動物  個人送養 (owner_id = user_id)
- 收容所會員建立的動物  收容所送養 (shelter_id = primary_shelter_id)
- 必填欄位: 動物名稱、物種、性別、年齡、所在縣市、描述
- 圖片至少 1 張，支援 JPG/PNG/GIF，單檔最大 5MB
- 送養資料需經管理員審核通過後才會公開顯示

### 2. sequence-application-review.puml
**使用案例2: 申請審核作業 (BP-APPLICATION-005)**

描述送養者（一般會員或收容所會員）如何執行領養申請審核作業的完整流程：

**涉及的後端檔案:**
- `applications.py` (Blueprint) - 領養申請相關 API 端點
- `application_service.py` - 申請業務邏輯服務
- `permission_service.py` - 權限檢查服務
- `notification_service.py` - 通知服務
- `email_tasks.py` (Celery Task) - Email 非同步任務
- Database - 資料庫操作
- Celery Queue - 任務佇列

**主要流程:**
1. 瀏覽申請列表 - 查看待審核的申請 (mode=review)
2. 查看申請詳細資料 - 包含申請人資訊和動物資料
3. 進行審核評估與填寫意見 - 送養者進行評估
4. 提交審核結果 - 核准 (approve) 或拒絕 (reject)
5. 記錄審計日誌 - 記錄審核操作
6. 發送通知給申請人 - 站內通知
7. 發送 Email 通知（非同步）- 透過 Celery 任務

**商業規則:**
- **管理員不能審核送養申請**（重要規則）
- 個人送養：只有動物擁有者 (owner_id) 可以審核
- 收容所送養：該收容所的成員 (shelter_id) 可以審核
- 使用樂觀鎖 (version) 避免並發衝突
- 核准後動物狀態改為 ADOPTED，不會在公開清單顯示
- 拒絕後動物狀態不變，仍可接受其他申請

## 架構設計

### 三層架構 (Three-Tier Architecture)

本專案採用清晰的分層架構，職責分離明確：

```

   Blueprint Layer (API 層)             HTTP 請求/回應處理

   Service Layer (業務邏輯層)           業務規則、事務管理

   Data Layer (資料存取層)              資料庫操作

```

#### 1. Blueprint Layer (API 層) 職責
- **路由管理**: 定義 API 端點
- **認證控管**: JWT Token 驗證 (`@jwt_required()`)
- **請求解析**: `request.get_json()` 解析 HTTP 請求
- **回應格式化**: `jsonify()` 序列化為 JSON
- **HTTP 狀態碼**: 設定適當的狀態碼 (200, 201, 403, 404...)
- **異常處理**: 捕捉 Service 層的異常並轉換為 HTTP 回應

**範例檔案**: `animals.py`, `applications.py`, `uploads.py`

#### 2. Service Layer (業務邏輯層) 職責
- **業務規則**: 實作核心業務邏輯
- **資料驗證**: 驗證業務規則和資料完整性
- **事務管理**: `db.session.commit()` / `db.session.rollback()`
- **狀態流轉**: 管理實體狀態變更
- **服務協作**: 調用其他 Service (如 PermissionService)
- **異常拋出**: 拋出業務異常 (BusinessException, ValidationError)

**範例檔案**: `animal_service.py`, `application_service.py`, `permission_service.py`, `notification_service.py`

#### 3. Service 之間的協作

Service Layer 採用 **服務導向架構 (SOA)**，各服務可互相調用：

```python
# ApplicationService 調用多個其他服務
ApplicationService
   PermissionService.can_review_application()  # 權限檢查
   AuditService.log_application_review()        # 審計日誌
   NotificationService.notify_application_reviewed()  # 通知
```

**優點**:
- 權限邏輯集中管理，避免重複代碼
- 每個 Service 職責單一，易於測試
- 業務邏輯與資料存取分離

### 資料流動

#### 請求流程 (Request Flow)
```
User  Blueprint  Service  Database
     (HTTP)    (業務邏輯)   (資料存取)
```

#### 回應流程 (Response Flow)
```
Database  Service  Blueprint  User
(ORM Model) (處理)  (JSON序列化) (HTTP)
```

### 循序圖中的視覺標記

為了更清楚地展示各層職責，循序圖中使用了視覺標記：

- 🔵 **淺藍色框** (`#LightBlue`): API Blueprint 層
- 🟢 **淺綠色框** (`#LightGreen`): Service 業務邏輯層
- 🟡 **淺黃色框** (`#LightYellow`): Permission Service 層
- 🔴 **淺粉色框** (`#LightPink`): Notification Service 層

## 技術細節

### 認證與授權
- **Blueprint 層**: 使用 `@jwt_required()` 裝飾器驗證 JWT Token
- **Service 層**: 透過 `permission_service.py` 檢查業務權限
- **分離關注點**: 認證(Authentication)在 API 層，授權(Authorization)在 Service 層

### 資料一致性
- **樂觀鎖**: 使用 `version` 欄位處理並發更新 (在 Service 層實作)
- **事務管理**: Service 層負責 `db.session.commit()` 和 `db.session.rollback()`
- **ACID 保證**: 透過 SQLAlchemy 的 session 管理確保事務一致性

### 異常處理機制

```python
# Blueprint 層捕捉 Service 層異常
try:
    result = service.do_something()
    return jsonify(result), 200
except BusinessException as e:
    return jsonify({'message': str(e)}), e.status_code
except Exception as e:
    db.session.rollback()
    return jsonify({'message': '系統錯誤'}), 500
```

### 非同步處理
- **Celery 任務**: Email 發送在 Service 層調度，但不阻塞主流程
- **延遲執行**: 使用 `.delay()` 方法將任務加入佇列
- **失敗隔離**: 任務失敗不影響主要業務流程

### 檔案上傳
- **Blueprint 層**: 處理 multipart/form-data 請求
- **MinIO 整合**: 直接上傳到物件儲存
- 生成永久公開 URL 供前端使用
- 儲存 key 格式: `uploads/{user_id}/{uuid}.{ext}`

## 權限檢查邏輯

### 查看申請列表
- **ADMIN**: 可看所有申請
- **GENERAL_MEMBER**: 只能看自己提交的申請或針對自己動物的申請
- **SHELTER_MEMBER**: 可看自己提交的申請、個人動物的申請、收容所動物的申請

### 審核申請
- **個人送養動物**: `owner_id == user.user_id`
- **收容所送養動物**: `user.role == SHELTER_MEMBER && user.primary_shelter_id == animal.shelter_id`
- **管理員**: 明確禁止審核（回傳 403 Forbidden）

## 如何使用

### 查看循序圖
使用支援 PlantUML 的工具查看：
1. VS Code + PlantUML 擴充套件
2. IntelliJ IDEA（內建支援）
3. 線上工具: http://www.plantuml.com/plantuml/

### 產生圖片
```bash
# 使用 PlantUML CLI
java -jar plantuml.jar sequence-personal-rehome.puml
java -jar plantuml.jar sequence-application-review.puml
```

## 相關文件
- 後端 API 文件: `../api/`
- 系統設計文件: `../DESIGN_PATTERNS.md`
- 開發指南: `../development.md`

---
最後更新: 2025-11-18
文件版本: v4 (強化 Service 與 Blueprint 互動說明)
