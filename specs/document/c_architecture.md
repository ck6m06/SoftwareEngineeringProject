(c) 軟體設計文件 (架構設計)    
大綱：

1. 系統架構概述  
2. 模組分解 (前端、後端)  
3. 資料庫  

4. **系統架構概述：**  
   本系統採用三層式架構（Presentation / Application / Data），下列為每一層的技術選擇與主要職責：  
5. 表示層（Presentation Layer）  
   1. 技術選擇：  
      1. 框架：Vue 3.4.21 + Vite 5.1.6 + TypeScript 5.4.2（SPA）  
      2. 狀態管理：Pinia 2.1.7；Server-state: @tanstack/vue-query 5.28.4  
      3. 表單驗證：vee-validate 4.12.5 + zod 3.22.4  
      4. UI樣式：Tailwind CSS 3.4.1
      5. HTTP 客戶端：Axios 1.6.7
      6. 測試框架：Vitest + Playwright
      7. 代碼品質：ESLint + Prettier  
   2. 主要職責：  
      1. 呈現使用者介面與互動。  
      2. 處理表單驗證、草稿快取與本地輸入暫存（LocalStorage / indexedDB）。  
      3. 與後端 REST API 交換資料（HTTP/JSON）：發起請求、顯示回應、錯誤處理與 retry 策略。  
      4. 實作 presign 上傳流程：  
         1. 前端向 API 取得 presigned URL  
         2. 前端直接上傳檔案至 Object Storage  
         3. 上傳完成後回報 metadata  
      5. 顯示長時間任務狀態與通知（/jobs/{jobId} 輪詢或透過 websocket / pubsub）。  
      6. 客戶端路由守衛與基本存取導向（基於角色或所有權的 UI 控制）。  
   3. 主要功能頁面：  
      1. Landing — 平台首頁、導向登入或主要功能入口。  
      2. Listings — 動物清單搜尋與篩選。  
      3. Listing Detail — 動物詳細資訊、圖片與申請入口。  
      4. My Applications — 顯示使用者申請紀錄與狀態。(一般會員)  
      5. My Rehomes — 管理使用者的刊登資料，並進行審核。(一般會員)  
      6. Shelter Dashboard —收容所會員專屬管理介面（刊登、申請審核）  
      7. Admin Dashboard — 管理員後台，用於審核與系統監控。
      8. Medical Records — 醫療紀錄管理頁面
      9. Audit Logs — 系統審計日誌查詢頁面
      10. Notification Center — 通知中心頁面
      11. User Profile — 用戶個人資料管理
      12. Jobs — 背景任務狀態監控頁面  
   4. 與其他層互動：  
      1. 透過 HTTPS REST API 與應用層（Application Layer）交換資料；上傳流程為 presign → 直傳 MinIO (Object Storage物件儲存系統) → 回傳 metadata 給 API。  
      2. 接收 JSON 資料並更新前端狀態與 UI 呈現。  
6. 應用層（Application Layer）  
   1. 技術選擇：Flask 3.0.0（Blueprints 組織），使用 flask-smorest 0.42.3 以便與 OpenAPI contract 整合。
      - ORM：SQLAlchemy 2.0.23 + Alembic 1.13.0
      - 認證：JWT (flask-jwt-extended 4.5.3)
      - 安全加密：bcrypt 4.1.2 + argon2-cffi 23.1.0
      - 限流保護：Flask-Limiter 3.5.0
      - 監控追蹤：Sentry SDK 1.39.1
      - 測試框架：pytest 7.4.3 + pytest-flask  
   2. 主要職責：  
      1. 提供清晰且可版本化的 RESTful API（遵循 OpenAPI contract）。  
      2. 驗證 (authentication) 與授權 (authorization / RBAC / ownership checks)。  
      3. 實作業務邏輯並管理資料一致性與交易（transaction / optimistic locking）。  
      4. 管理檔案中繼資料（File Metadata）。  
      5. 管理附件 metadata、生成 presigned URLs 並驗證上傳擁有權。  
      6. 對外排程長時間任務（enqueue job \-\> 202 \+ jobId）並監控 job lifecycle。  
      7. 寫入 AuditLog、處理 idempotency、rate-limiting 與錯誤重試策略。  
   3. 背景任務處理（Worker）：  
      Celery 5.3.4 + Redis 5.0.1（或 RQ 為替代）負責處理長時間任務（batch import/export、檔案處理、外部系統整合、郵件發送）；API 使用 202 + jobId 模式回應並將工作放入 Redis 佇列。  
7. 資料層（Data Layer）  
   1. 資料庫：MySQL 8.0 (InnoDB)，使用 SQLAlchemy 2.0.23 (Declarative) 與 Alembic 1.13.0 管理 schema 與 migrations。  
   2. 物件儲存（Object Storage）：  
      1. 採用 MinIO 7.2.0：開發可在 docker-compose 使用單節點 MinIO 快速啟動，生產則採用 MinIO 分散式模式或透過 MinIO Operator / Helm 在 Kubernetes 部署以確保可用性與擴充性。
      2. 整合 boto3 1.34.12 作為 S3 兼容客戶端
   3. 緩存與隊列：Redis 7.x 用於會話管理、Celery 任務隊列和應用層緩存  
8. 資料流說明  
   1. 整體資料流如下：  
      1. 前端（Vue3）透過 HTTPS 向後端 Flask API 發送請求（JSON body / Bearer token）。  
      2. API 層負責：  
         1. 驗證請求身份與權限；  
         2. 執行業務邏輯；  
         3. 存取 MySQL；  
         4. 處理 presigned upload 與 attachments metadata；  
         5. 若為長時間任務，將工作排入 Celery/Redis 佇列，並立即回傳 HTTP 202（Accepted）與 jobId。  
      3. 背景工作處理器（Celery workers）從佇列中取出任務，進行非同步處理（如 CSV 匯入、圖片處理、外部 API 呼叫），並於完成後更新資料庫與 job/notification 狀態。

 


2. **模組分解**  
1. 前端：  
   設計原則：  
* Feature-first：以 domain/feature 為單位拆分模組，模組內包含 UI、composables、types、stories、tests。  
* Contract-first：OpenAPI 作為 source-of-truth；前端使用 \`openapi-typescript\` 產出 types，並用 msw 建立 mock handlers。  
* 單向資料流：components (presentational) 與 composables/stores (data & effects) 分離。  
* 可測試：每個 composable 有 unit tests；主要流程（發佈、申請、上傳）有 E2E 覆蓋。  

  前端模組分解（feature-first）：  
1) Auth  
* 責任：登入/登出、token 管理、route-guards  
* 檔案：\`stores/useAuth.ts\`、\`composables/useAuth.ts\`、\`components/auth/LoginForm.vue\`  
* Endpoint：POST /auth/login, POST /auth/refresh


2) Browsing (Animals / Listings)  
* 責任：列表、篩選、分頁/無限滾動、快取策略  
* 檔案：\`pages/Animals.vue\`, \`composables/useInfiniteAnimals.ts\`, \`components/AnimalCard.vue\`  
* Endpoint：GET /animals?...


  

3) Animal Detail & Rehome  
* 責任：詳情頁、Rehome 表單（含 upload presign）、申請按鈕  
* 檔案：`pages/AnimalDetail.vue`, `pages/RehomeForm.vue`, `pages/MyRehomes.vue`, `composables/useUploadPresign.ts`  
* Endpoint：GET /animals/{id}, POST /animals, PATCH /animals/{id}


4) Uploads / Attachments  
* 責任：取得 presign URL、執行直接上傳、POST metadata、提供上傳 progress 與 retry  
* 檔案：`composables/useUploadPresign.ts`, `components/uploads/FileUploader.vue`, `api/uploads.ts`  
* Endpoint：POST /uploads/presign, POST /attachments

5) Applications  
* 責任：提交與查詢申請、idempotency header 管理、顯示 409 錯誤 UX、申請審核流程  
* 檔案：`pages/MyApplications.vue`, `pages/ApplicationReview.vue`, `composables/useApplication.ts`  
* Endpoint：POST /applications, GET /applications, POST /applications/{id}/review

6) Medical Records
* 責任：醫療紀錄建立、查詢、驗證流程
* 檔案：`pages/MedicalRecords.vue`, `api/medicalRecords.ts`
* Endpoint：POST /animals/{id}/medical-records, POST /medical-records/{id}/verify

7) Jobs / Admin / Notifications  
* 責任：job polling、admin pages、通知中心、審計日誌、用戶管理  
* 檔案：`composables/useJobStatus.ts`, `components/JobProgress.vue`, `stores/useNotifications.ts`, `pages/AdminDashboard.vue`, `pages/AdminUsers.vue`, `pages/AuditLogs.vue`  
* Endpoint：GET /jobs/{jobId}, GET /notifications, GET /admin/audit, GET /admin/users

8) Shelter Management
* 責任：收容所資訊管理、批次上傳、收容所專屬功能
* 檔案：`pages/Shelters.vue`, `pages/ShelterDashboard.vue`, `pages/ShelterBatch.vue`
* Endpoint：GET /shelters, POST /shelters/{id}/animals/batch

  **b. 後端模組分解：**

1. Auth 模組  
* 功能：使用者註冊、登入、JWT access/refresh token 發放與刷新、登出、電子郵件驗證（email verification）、密碼重置流程支援。  
* 路由範例：  
  * POST /auth/register  
  * POST /auth/login  
  * POST /auth/refresh  
  * POST /auth/logout  
  * GET /auth/verify?token=
  * POST /auth/confirm-email  
  * POST /auth/forgot-password
  * POST /auth/reset-password  
* 說明：  
  * 負責身份驗證（authentication）與基礎授權（authorization）工具。建議使用短生命 access token (JWT) \+ refresh token (httpOnly cookie 或安全儲存) 並實作 token rotation / revoke 機制。  
  * 實作細節建議：使用安全的雜湊演算法（bcrypt/argon2）儲存密碼、加入登入失敗次數鎖定與 rate limiting、防止暴力破解；使用 \`flask-smorest\` 或類似工具做 schema 驗證與 OpenAPI 綁定。  
* 安全建議：refresh token 儘量放 httpOnly, Secure cookie；若採用 SPA 並使用 localStorage，需妥善設計 refresh 與 CSRF 保護；管理員高風險操作考慮 MFA。  
* 其他：提供 endpoints 支援 email verification 與 password reset（含 expire token），並在所有重要狀態變更寫入 AuditLog。  
    
2. Users 模組  
* 功能：使用者 CRUD、個人檔案管理、角色管理、primaryShelterId、個資匯出/刪除請求（job pattern）、用戶封禁管理。  
* 路由：  
  * GET /users/{id}  
  * PATCH /users/{id}
  * GET /admin/users
  * POST /admin/users/{id}/ban
  * POST /data/export
* 說明：實作應包含欄位級別的隱私控制（PII masking）、匯出/刪除走 job pattern（需審核），並在敏感操作寫入 AuditLog。管理員可搜尋、篩選和管理用戶。


3. Shelters 模組  
* 功能：收容所資料管理、收容所驗證流程、收容所批次匯入（batch upload）入口、收容所專屬動物管理。  
* 路由：  
  * GET /shelters
  * GET /shelters/{id}
  * POST /shelters/{id}/animals/batch  (enqueue job -> 202)
  * GET /shelters/{id}/animals
* 說明：batch import 使用 multipart upload + job pattern；需記錄 jobId，worker 由 Celery 處理並回填結果至 Job 表與 Notification。支援收容所專屬的動物管理介面。


4. Animals / Rehomes 模組  
* 功能：動物資料與送養刊登管理（CRUD）、狀態流（DRAFT, SUBMITTED, PUBLISHED, RETIRED）、圖片/附件關聯管理、我的送養管理。  
* 路由：  
  * GET /animals  
  * GET /animals/{id}  
  * POST /animals
  * PATCH /animals/{id}
  * POST /animals/{id}/submit
  * DELETE /animals/{id}
  * GET /my-animals
* 說明：支援 filters (species, sex, shelter, q, featured)、pagination/infinite scroll；圖片與 attachments 為 polymorphic metadata，實際檔案存 S3/MinIO。支援草稿保存和提交審核流程。  
    
5. Applications 模組  
* 功能：申請 (Application) 建立、查詢、審核流程（含 assignment）、狀態管理與並發控制（optimistic locking）、我的申請管理。  
* 路由：  
  * POST /applications  
  * GET /applications
  * GET /my-applications
  * POST /applications/{id}/review
  * POST /applications/{id}/assign
* 說明：支援 Idempotency-Key header 去重、application.version 作為 optimistic locking 欄位；service 層需驗證申請人資格（不得為刊登者本人）。支援申請審核工作流程。


6. MedicalRecords 模組  
* 功能：動物醫療紀錄建立、附件關聯、驗證流程（verify）。  
* 路由：  
  * POST /animals/{id}/medical-records  
  * POST /medical-records/{id}/verify  
* 說明：初始紀錄為 unverified，管理員可標示為 verified；醫療附件應能鏈結至 attachments 並記錄來源與上傳者。


7. Attachments / Uploads 模組  
* 功能：產生 presigned URL、處理 multipart presign（大檔案）、管理 attachment metadata（storageKey, url, ownerType, ownerId）。  
* 路由：  
  * POST /uploads/presign  
  * POST /attachments  
  * GET /attachments/{id}  
* 說明：presign TTL 建議 5–15 分鐘；上傳成功後前端呼叫 POST /attachments 建立 metadata；後端在 metadata 接收時驗證檔案存在、大小/checksum（若提供）與擁有權。  
8. Notifications 模組  
* 功能：建立與查詢通知紀錄（DB）、enqueue delivery job、標記已讀、通知中心管理。  
* 路由：  
  * GET /notifications  
  * POST /notifications/{id}/mark-read
  * POST /notifications/mark-all-read
  * DELETE /notifications/{id}
* 說明：通知產生可由 worker 處理外部投遞（email/push）；前端可透過 GET /notifications?recipientId= 查詢未讀/已讀狀態。支援多種通知類型和批次操作。  
9. Jobs 模組  
* 功能：統一 Job table、查詢 job 狀態、重試與 metrics、管理與觀察長時間任務生命周期、管理員審批功能。  
* 路由：
  * GET /jobs/{jobId}
  * GET /jobs
  * POST /jobs/{id}/approve
  * POST /jobs/{id}/reject
* 說明：所有長時間任務採 202 + jobId 模式；worker（Celery）更新 job table（attempts, progress, resultSummary），並在完成/失敗時發 Notification。管理員可審批和監控任務。


10. Audit 模組  
* 功能：寫入並查詢 AuditLog（actorId, action, before, after, notes, timestamp）。  
* 路由：  
  * GET /admin/audit  
* 說明：在所有重要狀態變更中調用 auditService.log；對於寫入失敗應具備重試/enqueue 機制，且一般使用者不可刪除 audit 紀錄。


11. Admin 模組  
* 功能：管理端專用操作（資源恢復、審核、報表、系統查詢）、用戶管理、系統監控。  
* 路由：  
  * /admin/* （例如 /admin/animals, /admin/users, /admin/applications）
  * GET /admin/dashboard
  * GET /admin/statistics
* 說明：需嚴格 RBAC 控制（角色與 scope），並記錄所有管理動作至 AuditLog；管理面板功能可搭配限速與多因素驗證。包含管理員專用的控制台和統計功能。


12. Health & Observability 模組  
* 功能：健康檢查、metrics、tracing、錯誤收集整合。  
* 路由：  
  * GET /healthz  
  * GET /readyz  
  * GET /metrics  
* 說明：支援 OpenTelemetry traces、Prometheus metrics endpoint 與 Sentry 錯誤監控；在容器化環境提供 readiness/liveness endpoints 以利 k8s probe。

13. Email Service 模組
* 功能：郵件發送服務、註冊驗證郵件、密碼重置郵件、通知郵件
* 服務：email_service.py
* 說明：使用 Celery 異步發送郵件，支援 HTML 模板和重試機制，整合 Gmail SMTP 服務。


1. 資料庫設計  
   資料表：

| Table：users |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| userId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵。 |
| email | VARCHAR(320) |  |  | X | 使用者電子郵件（唯一，作為登入帳號）。 |
| username | VARCHAR(150) |  |  | O | 使用者公開顯示的帳號或暱稱。 |
| phoneNumber | VARCHAR(32) |  |  | O | 使用者電話。 |
| firstName | VARCHAR(120) |  |  | O |  |
| lastNmae | VARCHAR(120) |  |  | O |  |
| role | ENUM( 'GENERAL\_MEMBER', 'SHELTER\_MEMBER', 'ADMIN') |  |  | X | 代表使用者的身分，用於授權檢查。 Defualt：‘GENERAL\_MEMBER’。 |
| verified | TINYINT(1) |  |  | X | 是否已驗證電子郵件（布林）。 DEFAULT 0。 |
| primaryShelterId | BIGINT UNSIGNED |  | V | O | 使用者所屬或代表的主要收容所 id。(FK) |
| profilePhotoUrl | VARCHAR(1024) |  |  | O | 使用者的像檔案的 URL。 |
| settings | JSON |  |  | O | 儲存使用者偏好設定（例如通知設定）。 |
| passwordHash | VARCHAR(255) |  |  | X | 密碼雜湊（例如 bcrypt/argon2 的結果），永遠不要儲存明文密碼。 |
| passwordChangedAt | DATETIME(6) |  |  | O | 使用者上次變更密碼的時間。 |
| lastLoginAt | DATETIME(6) |  |  | O | 用者最近一次成功登入時間（供審計與安全通知）。 |
| failedLoginAttempts | INT |  |  | X | Defualt 0。連續失敗的登入次數，用於實作鎖定策略或 threshold-based 風控。 |
| lockedUntil | DATETIME(6) |  |  | O | 若因多次失敗而暫時鎖定帳號，記錄解鎖時間（timestamp），NULL 表示未鎖定。 |
| createdAt | DATETIME(6) |  |  | X | 建立間戳。 |
| updatedAt | DATETIME(6) |  |  | X | 更新時間戳。(預設為建立時間) |
| deletedAt | DATETIME(6) |  |  | O | 軟刪除時間戳；若不為 NULL 表示帳號已被刪除但保留紀錄。 |

| Table：pendingRegistrations |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| pendingId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵。 |
| email | VARCHAR(320) |  |  | X | 待驗證的電子郵件地址。 |
| username | VARCHAR(150) |  |  | O | 用戶名稱。 |
| firstName | VARCHAR(120) |  |  | O | 名字。 |
| lastName | VARCHAR(120) |  |  | O | 姓氏。 |
| phoneNumber | VARCHAR(32) |  |  | O | 電話號碼。 |
| role | ENUM('GENERAL\_MEMBER', 'SHELTER\_MEMBER', 'ADMIN') |  |  | X | 用戶角色，預設為 GENERAL\_MEMBER。 |
| passwordHash | VARCHAR(255) |  |  | X | 密碼雜湊。 |
| verificationCodeHash | VARCHAR(255) |  |  | O | 6位數驗證碼的雜湊值。 |
| verificationToken | VARCHAR(255) |  |  | O | 24小時有效的驗證 token。 |
| expiresAt | DATETIME(6) |  |  | X | 驗證過期時間。 |
| createdAt | DATETIME(6) |  |  | X | 建立時間戳。 |

   

   

   

   

| Table：shelters |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| shelterId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵。 |
| name | VARCHAR(255) |  |  | X | 使用者電子郵件（唯一，作為登入帳號）。 |
| slug | VARCHAR(255) |  |  | O | 使用者暱稱或帳號名稱，可為空。 |
| contactEmail | VARCHAR(320) |  |  | X |  |
| contactPhone | VARCHAR(32) |  |  | X |  |
| address | JSON |  |  | X | JSON 格式的地址欄位，可包含街道、城市、縣市與郵遞區號，便於顯示與地圖整合。 |
| verified | TINYINT(1) |  |  | X | 收容所是否通過系統管理員審核（布林），影響是否可被標註為「官方認可」。 |
| primaryAccountUserId | BIGINT UNSIGNED |  | V | O | 指向管理此收容所的主要使用者(userId)（FK），用於角色與通知路徑。 |
| createdAt | DATETIME(6) |  |  | X | 建立間戳。 |
| updatedAt | DATETIME(6) |  |  | X | 更新時間戳。(預設為建立時間) |
| deletedAt | DATETIME(6) |  |  | O | 軟刪除時間戳；若不為 NULL 表示帳號已被刪除但保留紀錄。 |

   

	status (這裡有點奇怪 應該是要動物的狀態 是否被領養嗎?)

| Table：animals |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| animalId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵。 |
| name | VARCHAR(200) |  |  | O | 動物的稱呼或暱稱，供前端卡片與列表顯示。 |
| species | ENUM('CAT','DOG') |  |  | O | 動物種類（ENUM），便於分類與篩選。 |
| breed | VARCHAR(200) |  |  | O | 品種欄位，用於細分搜尋與顯示。 |
| sex | ENUM('MALE', 'FEMALE', 'UNKNOWN') |  |  | O | 性別（ENUM)。 |
| dob | DATE |  |  | O | 出生日期（若已知），可用於計算年齡。 |
| description | TEXT |  |  | O | 文字敘述，包括性情、背景故事或特殊需求。 |
| status | ENUM('DRAFT', 'SUBMITTED', 'PUBLISHED', 'RETIRED') |  |  | X | 工作流程狀態（DRAFT: 草稿, SUBMITTED: 已送審, PUBLISHED: 上架, RETIRED: 下架），控制是否曝光與可申請。 |
| shelterId | BIGINT UNSIGNED |  | V | O | 若動物由收容所管理，記錄該 shelterId（FK）。 |
| ownerId | BIGINT UNSIGNED |  | V | O | 若有原持有人或個人刊登者，記錄 userId。 |
| medicalSummary | TEXT |  |  | O | 針對醫療資訊的摘要（例如疫苗、手術、慢性病），常用於列表快覽。 |
| createdBy | BIGINT UNSIGNED |  | V | X | 建立此動物紀錄的使用者 userId（FK），便於追溯與權限判斷。 |
| createdAt | DATETIME(6) |  |  | X | 建立間戳。 |
| updatedAt | DATETIME(6) |  |  | X | 更新時間戳。(預設為建立時間) |
| deletedAt | DATETIME(6) |  |  | O | 軟刪除時間戳；若不為 NULL 表示帳號已被刪除但保留紀錄。 |

	

| Table：animalImages |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| animalImageId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵。 |
| animalId | BIGINT UNSIGNED |  | V | X | 外鍵，指向所屬 animal，用於查詢該動物所有圖片。 |
| storageKey | VARCHAR(150) |  |  | X | object storage（MinIO）內的物件鍵，用於直接上傳/下載。 |
| url | VARCHAR(2048) |  |  | X | 圖片對外存取的 URL（可為 CDN URL 或 presigned URL），供前端顯示。 |
| mimeType | VARCHAR(128) |  |  | O | 檔案的類型。 |
| width | INT |  |  | O | 影像寬高，可用於產生佔位圖或 lazy loading 決策。 |
| height | INT |  |  | O | 影像寬高，可用於產生佔位圖或 lazy loading 決策。 |
| order | INT |  |  | X | 圖片的顯示順序（整數），用於排序， Defult 0。 |
| createdAt | DATETIME(6) |  |  | X | 上傳/紀錄時間。 |

	申請狀態

| Table：applications |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| applicationId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵。 |
| applicantId | BIGINT UNSIGNED |  | V | X | 申請人 userId（FK），代表誰提出申請。 |
| animalId | BIGINT UNSIGNED |  |  | X | 申請對象的 animalId（FK）。 |
| type | ENUM('ADOPTION', 'REHOME') |  |  | X | 申請類型（ADOPTION 或 REHOME）。 |
| status | ENUM('PENDING', 'UNDER\_REVIEW', 'APPROVED', 'REJECTED', 'WITHDRAWN') |  |  | X | 申請狀態（PENDING / UNDER\_REVIEW / APPROVED / REJECTED / WITHDRAWN）。 |
| submittedAt | DATETIME(6) |  |  | O | 提交與審核時間，用於審計與 SLA 計算。 |
| reviewedAt | DATETIME(6) |  |  | O | 提交與審核時間，用於審計與 SLA 計算。 |
| reviewNotes | TEXT |  |  | O | 核者留下的文字備註（理由或拒絕原因）。 |
| assigneeId | BIGINT UNSIGNED |  |  | O | 負責處理該申請的審核者 userId（FK）。 |
| version | INT |  |  | X | 樂觀鎖欄位（int），在更新時檢查以避免競爭條件。 |
| idempotencyKey | VARCHAR(255) |  |  | O | 用於 POST 去重，避免重複建立相同申請（例如 client 重試情況）。 |
| attachments | JSON |  |  | O | JSON 陣列，儲存申請所附檔案的 metadata 或 attachment ids。 |
| createdAt | DATETIME(6) |  |  | X | 建立間戳。 |
| updatedAt | DATETIME(6) |  |  | X | 更新時間戳。(預設為建立時間) |
| deletedAt | DATETIME(6) |  |  | O | 軟刪除時間戳；若不為 NULL 表示帳號已被刪除但保留紀錄。 |

| Table：medicalRecords |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| medicalRecordId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵。 |
| animalId | BIGINT UNSIGNED |  | V | X | 對應該紀錄所屬的animalId。 |
| recordType | ENUM('TREATMENT', 'CHECKUP', 'VACCINE', 'SURGERY', 'OTHER') |  |  | O | 醫療紀錄類型，用於分類與過濾。 |
| date | DATE |  |  | O | 紀錄發生日期（若已知）。 |
| provider | VARCHAR(255) |  |  | O | 提供醫療服務者或醫療機構名稱。 |
| details | TEXT |  |  | O | 記錄詳述（文本），包含診斷、處置、醫囑等。 |
| attachments | JSON |  |  | O | JSON 陣列，連結相關檔案（例如病歷表、影像、檢驗結果）。 |
| verified | TINYINT(1) |  |  | X | 布林，表示該紀錄是否已經被授權人員(Admin)驗證。 |
| verifiedBy | BIGINT UNSIGNED |  | V | O | 驗證者的 userId（FK），在驗證時填入，用於追蹤誰完成驗證。 |
| createdBy | BIGINT UNSIGNED |  |  | O | 建立此紀錄的 userId（FK），通常是上傳或輸入紀錄的人。 |
| createdAt | DATETIME(6) |  |  | X | 建立間戳。 |
| updatedAt | DATETIME(6) |  |  | X | 更新時間戳。(預設為建立時間) |
| deletedAt | DATETIME(6) |  |  | O | 軟刪除時間戳；若不為 NULL 表示帳號已被刪除但保留紀錄。 |

| Table：notifications |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| notificationId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵。 |
| recipientId | BIGINT UNSIGNED |  | V | X | 接收者 userId（FK），是查詢通知的主要索引。 |
| actorId | BIGINT UNSIGNED |  |  | O | 執行該動作的 userId（可為 NULL，例如系統通知）。 |
| type | VARCHAR(128) |  |  | X | 通知類型字串（例如 'application\_submitted'），用於選擇 template 與處理邏輯。 |
| payload | VARCHAR(128) |  |  | O | JSON，儲存模板變數或原始事件資料，供通知服務解析並送出。 |
| read | TINYINT(1) |  |  | X | 是否已讀（布林）；用於前端顯示未讀 badge。 |
| createdAt | DATETIME(6) |  |  | X | 建立時間。 |
| readAt | DATETIME(6) |  |  | O | 讀取的時間。 |

| Table：jobs |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| jobId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵。 |
| type | VARCHAR(320) |  |  | X | 工作類型（例如 'shelter\_batch\_import'），用於 worker 路由與 metrics。 |
| status | ENUM('PENDING' ,'RUNNING', 'SUCCEEDED', 'FAILED') |  |  | X | 動作類別字串（例如 'application.approve', 'user.update'），便於篩選與搜尋。 |
| payload | JSON |  |  | O | 被操作的資源類型（例如 'application'、'animal'）。 |
| resultSummary | JSON |  |  | O | 執行結果摘要（例如 { total:100, ok:95, failed:5 }）。 |
| createdBy | BIGINT UNSIGNED |  | V | O | 建立這個 job 的 userId（或 NULL 表示系統）。 |
| createdAt | DATETIME(6) |  |  | X | 建立的時間。 |
| startedAt | DATETIME(6) |  |  | O | worker 開始處理時間。 |
| finishedAt | DATETIME(6) |  |  | O | 結束時間。用於 SLA/時長統計。 |
| attempts | INT |  |  | X | 重試次數，用於防止無限重試或判定重試策略。 Default 0。 |

| Table：attachments |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| attachmentId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵 |
| ownerType | VARCHAR(64) |  |  | x | 表示此附件屬於哪種類型的實體（例如 'animal', 'application', 'medical\_record'），用於在應用層解析擁有者。 |
| ownerId | BIGINT UNSIGNED  |  |  | X | 與 ownerType 配合，表示具體的資源 id（例如 animal.id 或 application.id）。此欄不是 DB FK，而是應用層維護關聯。 |
| storageKey | VARCHAR(1024) |  |  | X | 在 object storage 中的鍵值，用於直接上傳/下載。 |
| url | VARCHAR(2048) |  |  | X | 可供前端顯示或下載的完整 URL（可能為經由 CDN 的網址）。 |
| filename | VARCHAR(1024) |  |  | O | 原始檔名，方便展示與下載時使用者識別。 |
| mimeType | VARCHAR(128) |  |  | O | 檔案類型（image/jpeg, application/pdf 等），可用於安全檢查或顯示判斷。 |
| size | INT |  |  | O | 檔案大小（位元組），可用於 quota 與顯示。 |
| createdBy | BIGINT UNSIGNED |  | V | O | userId（FK），方便追蹤上傳者。 |
| createdAt | DATETIME(6) |  |  | X | 上傳時間。 |
| deletedAt | DATETIME(6) |  |  | O | 軟刪除時間。 |

| Table：auditLogs |  |  |  |  |  |
| ----- | ----- | ----- | ----- | :---: | ----- |
| 欄位名稱 | 資料型態 | PK | FK | Nullable | 說明 |
| auditLogId | BIGINT UNSIGNED AUTO\_INCREMENT | V |  | X | 主鍵 |
| actorId | BIGINT UNSIGNED |  | V | O | 執行者 userId（可為 NULL，表示系統動作）。 |
| action | VARCHAR(150) |  |  | X | 動作類別字串（例如 'application.approve', 'user.update'），便於篩選與搜尋。 |
| targetType | VARCHAR(128) |  |  | O | 被操作的資源類型（例如 'application'、'animal'）。 |
| targetId | BIGINT UNSIGNED |  |  | O | 被操作的資源 id。 |
| shelterId | BIGINT UNSIGNED |  |  | O | 若該動作與某 shelter 相關，記錄該 shelterId 以便過濾。 |
| beforeState | JSON |  |  | O | JSON 快照，紀錄變更前後的欄位值，用於鑑識與合規查詢。 |
| afterState | JSON |  |  | O | JSON 快照，紀錄變更前後的欄位值，用於鑑識與合規查詢。 |
| timestamp | DATETIME(6) |  |  | X | 事件發生時間，預設為 CURRENT\_TIMESTAMP(6)。 |

註：資料型態以MySQL 8.0去撰寫。

## ERD (Entity Relationship Diagram)

詳細的實體關係圖請參考：[erd-sql.md](./erd-sql.md)

資料表間的關聯關係：  
User（管理者）對 Shelter 為一對多（User 可管理多個 Shelter）。  
Shelter 對 User 為一對多（多位 User 可指向同一 Shelter，作為主要所屬）。  
Shelter 對 Animal 為一對多（收容所可能有多隻動物）。  
User（owner）對 Animal 為一對多（ownerId）。  
Animal 對 AnimalImages 為一對多，圖片為子資源。  
User（applicant）對 Applications 為一對多。  
Animal 對 Applications 為一對多。  
Animal 對 MedicalRecord 為一對多。
MedicalRecord 對 Attachments 為一對多（attachments 為 polymorphic）。  
User（createdBy）對 Attachments 為一對多。  
User（recipient）對 Notifications 為一對多。  
User（createdBy）對 Jobs 為一對多。  
User（actor）對 AuditLogs 為一對多。
PendingRegistration 獨立表，用於註冊流程中的臨時資料存儲。

