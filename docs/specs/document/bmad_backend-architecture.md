## 後端架構設計（Developer-ready — Flask + MySQL）

檔案來源：`spec.md`（功能規格）與 `erd-generated.md`（實體與欄位說明）。

目的：提供一份針對 Flask + MySQL 的後端設計，developer-ready、可直接 scaffold 與實作，包含模組分解、資料映射、API surface、長時間 job 模式、部署/運維建議與短期交付清單。

設計前提：本文件假定後端採用 Flask（Blueprints 組織）、SQLAlchemy（ORM）+ Alembic（migrations）、Celery + Redis（背景工作），檔案儲存使用 S3-compatible（MinIO for dev、AWS S3 for prod），資料庫選用 MySQL (InnoDB)。API contract 建議以 OpenAPI 為 source-of-truth。

## 簡短契約（Inputs / Outputs）
- 輸入：`spec.md`（業務需求、用例、API 範例）與 `erd-generated.md`（資料結構、enum、關聯）。
- 輸出：後端程式碼 scaffold（模組、controller、service、prisma schema 快速修補）、OpenAPI skeleton、部署清單與運維 runbook。
- 成功標準：前端可使用 OpenAPI mock server 開發，後端開發者可依檔案建立 CRUD 與 job 處理流程，並且 CI 能通過基本 lint/typecheck/test。

## 高階決策與理由
### 主要技術選擇
- 框架：Flask（Blueprints）搭配 flask-smorest 或 flask-pydantic 做 schema 驗證與 OpenAPI 綁定（或採 contract-first 的 apispec/connexion workflow）。
- ORM：SQLAlchemy（Declarative models）+ Alembic for migrations。
- DB：MySQL (InnoDB)。開發使用 Docker Compose 的 MySQL，生產可選 RDS/Aurora MySQL 或自管 MySQL 集群。
- Background jobs：Celery + Redis（推薦）或 RQ。
- File storage：S3-compatible (MinIO for dev)；用 boto3/minio-py 產生 presigned URLs。
- API contract：OpenAPI 3.0（contract-first 建議），前端由此產生 typed client。

## 模組分解（高內聚、低耦合）
每個模組包含 Blueprint (routes)、service 層 (業務邏輯)、repository/ORM layer（SQLAlchemy models & queries）、schemas (pydantic 或 marshmallow)、單元測試。

1. Auth 模組
   - 功能：使用者註冊、登入、JWT access/refresh token 發放與刷新、登出、電子郵件驗證（email verification）、密碼重置流程支援。
   - 路由：
     - POST /auth/register
     - POST /auth/login
     - POST /auth/refresh
     - POST /auth/logout
     - GET /auth/verify?token=
   - 說明：
     - 負責身份驗證（authentication）與基礎授權（authorization）工具。建議使用短生命 access token (JWT) + refresh token (httpOnly cookie 或安全儲存) 並實作 token rotation / revoke 機制。
     - 實作細節建議：使用安全的雜湊演算法（bcrypt/argon2）儲存密碼、加入登入失敗次數鎖定與 rate limiting、防止暴力破解；使用 `flask-smorest` 或類似工具做 schema 驗證與 OpenAPI 綁定。
     - 安全建議：refresh token 儘量放 httpOnly, Secure cookie；若採用 SPA 並使用 localStorage，需妥善設計 refresh 與 CSRF 保護；管理員高風險操作考慮 MFA。
     - 其他：提供 endpoints 支援 email verification 與 password reset（含 expire token），並在所有重要狀態變更寫入 AuditLog。

2. Users 模組
  - 功能：使用者 CRUD、個人檔案管理、角色管理、primaryShelterId、個資匯出/刪除請求（job pattern）。
  - 路由：
    - GET /users/{id}
    - PATCH /users/{id}
    - POST /data/export
  - 說明：實作應包含欄位級別的隱私控制（PII masking）、匯出/刪除走 job pattern（需審核），並在敏感操作寫入 AuditLog。

3. Shelters 模組
  - 功能：收容所資料管理、收容所驗證流程、收容所批次匯入（batch upload）入口。
  - 路由：
    - GET /shelters/{id}
    - POST /shelters/{id}/animals/batch  (enqueue job -> 202)
  - 說明：batch import 使用 multipart upload + job pattern；需記錄 jobId，worker 由 Celery 處理並回填結果至 Job 表與 Notification。

4. Animals / Rehomes 模組
  - 功能：動物資料與送養刊登管理（CRUD）、狀態流（DRAFT, SUBMITTED, PUBLISHED, RETIRED）、圖片/附件關聯管理。
  - 路由：
    - GET /animals
    - GET /animals/{id}
    - POST /rehomes
    - PATCH /rehomes/{id}
    - DELETE /rehomes/{id}
  - 說明：支援 filters (species, city, q, featured)、pagination/infinite scroll；圖片與 attachments 為 polymorphic metadata，實際檔案存 S3/MinIO。

5. Applications 模組
  - 功能：申請 (Application) 建立、查詢、審核流程（含 assignment）、狀態管理與並發控制（optimistic locking）。
  - 路由：
    - POST /applications
    - GET /applications
    - POST /applications/{id}/review
  - 說明：支援 Idempotency-Key header 去重、application.version 作為 optimistic locking 欄位；service 層需驗證申請人資格（不得為刊登者本人）。

6. MedicalRecords 模組
  - 功能：動物醫療紀錄建立、附件關聯、驗證流程（verify）。
  - 路由：
    - POST /animals/{id}/medical-records
    - POST /medical-records/{id}/verify
  - 說明：初始紀錄為 unverified，管理員可標示為 verified；醫療附件應能鏈結至 attachments 並記錄來源與上傳者。

7. Attachments / Uploads 模組
  - 功能：產生 presigned URL、處理 multipart presign（大檔案）、管理 attachment metadata（storageKey, url, ownerType, ownerId）。
  - 路由：
    - POST /uploads/presign
    - POST /attachments
    - GET /attachments/{id}
  - 說明：presign TTL 建議 5–15 分鐘；上傳成功後前端呼叫 POST /attachments 建立 metadata；後端在 metadata 接收時驗證檔案存在、大小/checksum（若提供）與擁有權。

8. Notifications 模組
  - 功能：建立與查詢通知紀錄（DB）、enqueue delivery job、標記已讀。
  - 路由：
    - GET /notifications
    - POST /notifications/{id}/mark-read
  - 說明：通知產生可由 worker 處理外部投遞（email/push）；前端可透過 GET /notifications?recipientId= 查詢未讀/已讀狀態。

9. Jobs 模組
  - 功能：統一 Job table、查詢 job 狀態、重試與 metrics、管理與觀察長時間任務生命周期。
  - 路由：
    - GET /jobs/{jobId}
  - 說明：所有長時間任務採 202 + jobId 模式；worker（Celery）更新 job table（attempts, progress, resultSummary），並在完成/失敗時發 Notification。

10. Audit 模組
   - 功能：寫入並查詢 AuditLog（actorId, action, before, after, notes, timestamp）。
   - 路由：
    - GET /admin/audit
   - 說明：在所有重要狀態變更中調用 auditService.log；對於寫入失敗應具備重試/enqueue 機制，且一般使用者不可刪除 audit 紀錄。

11. Admin 模組
   - 功能：管理端專用操作（資源恢復、審核、報表、系統查詢）。
   - 路由：
    - /admin/* （例如 /admin/animals, /admin/users, /admin/applications）
   - 說明：需嚴格 RBAC 控制（角色與 scope），並記錄所有管理動作至 AuditLog；管理面板功能可搭配限速與多因素驗證。

12. Health & Observability 模組
   - 功能：健康檢查、metrics、tracing、錯誤收集整合。
   - 路由：
    - GET /healthz
    - GET /readyz
    - GET /metrics
   - 說明：支援 OpenTelemetry traces、Prometheus metrics endpoint 與 Sentry 錯誤監控；在容器化環境提供 readiness/liveness endpoints 以利 k8s probe。

## Feature → Module 映射（User-facing features 對應後端模組）

建議：文件中同時保留「使用者視角的功能清單（feature list）」與「後端的 domain/module 清單」。前者幫助產品與 QA 理解使用流程，後者指導工程師 scaffold 與實作。下面示範如何把你列的 feature（1.0 ~ 2.4）映射到後端模組與代表性 endpoint：

- 1.0 動物瀏覽與搜尋
  - 負責模組：`animals`、`attachments`（圖片）、`notifications`（optional）
  - 代表 endpoint：GET /animals, GET /animals/{id}, GET /animals?featured=true

- 1.1 動物列表瀏覽
  - 負責模組：`animals`
  - 代表 endpoint：GET /animals (supports pagination, filters)

- 1.2 動物搜尋篩選
  - 負責模組：`animals`
  - 代表 endpoint：GET /animals?species=&city=&q=&featured=true

- 1.3 動物詳情檢視
  - 負責模組：`animals`, `attachments`, `medicalrecords`
  - 代表 endpoint：GET /animals/{id}, GET /attachments?ownerType=animal&ownerId={id}

- 1.4 領養申請提交
  - 負責模組：`applications`, `jobs`（若需 background checks）、`notifications`
  - 代表 endpoint：POST /applications (Idempotency-Key), GET /applications?applicantId=

- 2.0 送養管理
  - 負責模組：`rehomes`（或放在 `animals` domain）、`attachments`, `jobs`（batch）

- 2.1 個人送養發佈
  - 負責模組：`animals`/`rehomes`, `attachments`
  - 代表 endpoint：POST /rehomes (status=DRAFT or SUBMITTED)

- 2.2 個人送養管理
  - 負責模組：`animals`/`rehomes`
  - 代表 endpoint：GET /users/{id}/rehomes, PATCH /rehomes/{id}, DELETE /rehomes/{id}

- 2.3 收容所送養發佈
  - 負責模組：`shelters`, `animals`, `attachments`, `jobs`（如果 batch 上傳）
  - 代表 endpoint：POST /shelters/{id}/animals/batch -> 202 { jobId }

- 2.4 收容所送養管理
  - 負責模組：`shelters`, `animals`, `applications`, `admin`（如需高權限操作）
  - 代表 endpoint：GET /shelters/{id}/animals, POST /shelters/{id}/animals/{animalId}/publish

實務建議：
- 在規格文件（specs）用 feature-centric 的章節來描述使用流程、UX 與驗收條件（1.0~2.4）。
- 在後端架構文件與程式碼中使用 domain/module-based 組織（上方的 modules list），確保每個 module 明確擁有其 routes/service/schemas/tests。
- 在 repo 中新增一張『Feature → Module → Endpoint』的對照表（可放在 `specs/` 下或 README），讓前端、QA、PM 能迅速查到某個 feature 會觸發哪些後端 API 與哪些模組負責。


## 資料模型對應（來源：erd-generated.md -> SQLAlchemy）
- 使用 `erd-generated.md` 作為 models 的來源，將實體映射為 SQLAlchemy models（User, Shelter, Animal, AnimalImage, Application, MedicalRecord, Attachment, Notification, Job, AuditLog）。
- Enums（Role, Species, Sex, AnimalStatus, ApplicationStatus...）以 SQLAlchemy Enum 或自訂映射實作。
- Attachment 採 polymorphic owner (owner_type, owner_id)。實作時於 application 層提供解譯與索引策略以維持效能。

建議的資料庫注意事項：
- 為常查詢欄位建立索引（例如 Application(applicant_id, status)、Notification(recipient_id)、Animal(status, city)、Attachment(owner_type, owner_id)）。
- Application.version 欄位用於 optimistic locking（更新時以 WHERE version=expectedVersion）。
- Job table 包含 attempts、started_at、finished_at、result_summary 等欄位以支援可查詢的背景工作狀態。

## 核心 API Surface（摘要）
以下為依 `spec.md` 總結的最重要 endpoints（作為 OpenAPI skeleton 的起點）：

- Auth
  - POST /auth/register
  - POST /auth/login
  - POST /auth/logout
  - GET /auth/verify?token=

- Animals / Rehomes
  - GET /animals
  - GET /animals/{id}
  - POST /rehomes (建立送養; status=SUBMITTED)
  - PATCH /rehomes/{id}
  - GET /animals?featured=true

- Applications
  - POST /applications (Idempotency-Key 支援)
  - GET /applications?applicantId=&status=
  - POST /applications/{id}/review { action: UNDER_REVIEW|ACCEPT|REJECT, expectedVersion? }
  - POST /shelters/{id}/applications/{appId}/assign { assigneeId }

- Shelters
  - GET /shelters/{id}
  - POST /shelters/{id}/animals/batch -> 202 { jobId }

- Medical Records
  - POST /animals/{id}/medical-records
  - POST /medical-records/{id}/verify

- Uploads / Attachments
  - POST /uploads/presign { filename, contentType, ownerType, ownerId }
  - POST /attachments (metadata)

- Notifications
  - GET /notifications?recipientId={me}
  - POST /notifications/{id}/mark-read

- Jobs & Admin
  - GET /jobs/{jobId}
  - GET /admin/audit?targetType=&targetId=&from=&to=&actorId=

HTTP 標準錯誤與合約遵循：401/403/404/409/422，錯誤 body 採 { code, message, details }。

## 實作要點（工程細節）
- Idempotency：對 create endpoints（POST /applications, /rehomes, batch import）支援 Idempotency-Key header。實作方式可為獨立的 idempotency_keys 表或在 business table（例如 application）上加上 idempotency_key 與 unique constraint（applicant_id + idempotency_key）。重複請求應回傳已存在資源或 409。
- Concurrency：審核流程與 assignment 以 optimistic locking（version int）為主；API 接收 expectedVersion，若衝突回 409 並返回 currentVersion。
- Jobs：批次匯入、匯出、長時間檔案處理皆採 202 + jobId，worker 使用 Celery（Redis broker）處理，進度寫入 Job 表並發 Notification。提供 GET /jobs/{jobId} 查詢進度。
- Attachments：前端先呼叫 /uploads/presign 取得 presigned URL，上傳至 S3 (或 MinIO)，然後呼叫 POST /attachments 建立 metadata（storage_key, url, owner_type, owner_id）。Flask 可用 boto3 或 minio-py 生成 presigned URL。
- Audit：在 Service 層提供 auditService.log(actor, action, before, after, notes)。對於失敗的寫入可 fallback enqueue retry job，再回 202。

## 安全性與合規
- Auth：JWT（access short-lived, refresh longer），對 admin high-risk 操作建議 MFA。
- RBAC：在 route guard 層實作 role 檢查與 resource ownership 檢查（ownerId / shelterId）。
- 個資：個資匯出/刪除以 job pattern 並需審核後執行；敏感欄位加密 at-rest（例如 phone 加密或 tokenization）。
- Audit & Immutable Log：AuditLog 不允許一般使用者刪除；可選擇將 audit log 存入 append-only store（例如 write-once S3 + secure index）。

## 可觀察性、監控與提示
- Tracing：OpenTelemetry，追踪跨 service/worker 的請求。
- Metrics：Prometheus 指標（http_request_duration_seconds, job_queue_length, job_success_total, job_failure_total, audit_write_failures），Grafana 儀表板。
- Errors：Sentry 捕獲 exception 與手動記錄的 business error。

## 部署建議（Dev -> Staging -> Prod）
- Docker Compose 開發樣板：MySQL, Redis, MinIO, api (Flask), celery worker, migrations job。用於本地開發。
- K8s / Cloud 建議：
  - Deploy API as stateless Deployment + HPA。連接 RDS/Aurora MySQL + ElastiCache (Redis)。
  - Attachments 使用 S3（或 MinIO for on-prem）。
  - Workers (Celery) 為獨立 Deployment，視 job queue 長度垂直/水平擴充。
  - 使用 managed services（RDS/Aurora, S3, ElastiCache）以降低運維負擔。

## 運維與 runbooks（最小集）
- Health check：/healthz (liveness), /readyz (readiness)。
- 緊急回退：在 k8s 上保留前一個可用 image tag，使用 Deployment rollback；DB migration 應支援 rollback 計劃。
- Backup：每日 snapshot（Postgres），且至少保留 7 天版本，主要備份測試自動校驗。
- Incident playbook：API error rate 高於閾值 -> 暫停非關鍵 worker -> 增加 API replicas -> 調查 Sentry / logs。

## 安全測試與 QA 建議
- SAST、依賴檢查、自動化同階段測試（Jest）、整合測試（supertest）與 E2E（Playwright/Cypress）。
- 添加 contract tests（利用 generated OpenAPI mock 與 API tests）以保證前後端合約。

## 可交付的下一步（短期優先）
1. 產出 OpenAPI 3.0 skeleton（`specs/002-title-description-project/openapi.yaml`）— high priority，對齊前後端。
2. Scaffold minimal Flask backend：create_app factory、extensions (db, migrate, redis, celery)、blueprints (auth, animals, applications, uploads)、SQLAlchemy models 與 Alembic migration skeleton。
3. Scaffold Vue 3 frontend skeleton（Vite + Pinia + @tanstack/vue-query）並以 OpenAPI generated client 作為 data layer。
4. 建立 Docker Compose dev stack（MySQL, Redis, MinIO, api, worker）並在 CI 中加入 migration job。

## Checklist for Implementation (MVP)
- [ ] Initialize Flask project + Python tooling (poetry/venv)
- [ ] Add SQLAlchemy models & Alembic migrations (from ERD)
- [ ] Implement Auth + Users blueprints (register/login, role enforcement)
- [ ] Implement Animals/Rehomes blueprint (GET list, GET detail, POST rehome)
- [ ] Implement Applications blueprint with optimistic locking + idempotency
- [ ] Implement Uploads (presign) + Attachment metadata
- [ ] Implement Jobs worker (Celery) for batch imports
- [ ] Implement Notifications table + Notification Center APIs
- [ ] Implement Audit logging service / middleware
- [ ] Add health/metrics endpoints + OpenTelemetry + Sentry
- [ ] Create OpenAPI YAML & run contract tests

## 風險與注意事項
- 若現有 schema.prisma 與本文件期望不一致，應以 Prisma schema 為主並在本文件記錄差異。
- 批次匯入（CSV/JSON）請務必採用 job pattern 以避免同步阻塞與超時。
- Attachment storage 權限與 presigned URL 需正確設定 CORS 與短時效簽名以免誤用。

---
完成者：automated architect action
