# 全端架構設計（Full-Stack, Developer-ready — Vue 3 + Vite frontend, Flask + MySQL backend）

來源：整合 `spec.md`（功能規格）、`erd-generated.md`（資料模型）與現有 OpenAPI（`specs/002-title-description-project/openapi.yaml`）作為 input，提供一份可直接 scaffold 的全端設計，覆蓋前端、後端、背景工作、部署與測試。

首選技術堆疊（已調整為 Vue 3 + Flask + MySQL，採三層式架構）

## 系統架構概述 — 三層式架構 (Three-tier Architecture)

本系統採用三層式架構（Presentation / Application / Data），下列為每一層的技術選擇與主要職責，已依你的要求使用 Vue3 + Flask + MySQL：

1) 表示層（Presentation Layer）
   - 技術：
     - 框架：Vue 3 + Vite + TypeScript（SPA）
     - 狀態管理：Pinia；Server-state: @tanstack/vue-query
     - 表單驗證：vee-validate + zod
     - UI：Tailwind CSS（可替換為設計系統）
   - 主要職責：
     - 呈現使用者介面與互動（頁面導航、元件組合、可及性）。
     - 處理表單驗證、草稿快取與本地輸入暫存（LocalStorage / indexedDB）。
     - 與後端 REST API 交換資料（HTTP/JSON）：發起請求、顯示回應、錯誤處理與 retry 策略。
    - 實作 presign 上傳流程：
      - 向後端請求 presigned URL（傳送 owner_type / owner_id / filename / contentType 做後端授權檢查）。
      - 使用 presigned URL 直接上傳至 MinIO（支援 PUT/POST 與 multipart upload 以處理大型檔案）。
      - 顯示上傳進度（progress bar）、支援上傳取消、中斷後重試與限制並行上傳數量以保護客戶端資源。
      - 在上傳完成後，呼叫 POST /attachments（或對應 endpoint）提交 metadata（storageKey、url、contentType、size、checksum、owner_type、owner_id 等）。
      - 可選：在上傳前在客戶端做影像縮放/壓縮、生成預覽縮圖，或計算 checksum 以便後端驗證完整性。
      - 處理 presign TTL 過期或簽名失敗的情況：自動向後端重取 presign 並續傳或回報錯誤給使用者。
      - 若後端把檔案處理排入 background job（202 + jobId），前端應支援顯示 job 狀態（/jobs/{jobId} 輪詢或透過 websocket 推播）。
     - 顯示長時間任務狀態與通知（/jobs/{jobId} 輪詢或透過 websocket / pubsub）。
     - 客戶端路由守衛與基本存取導向（基於角色或所有權的 UI 控制）。
   - 主要頁面：
     - Landing — 平台首頁、導向登入或主要功能入口。
     - Listings — 動物清單搜尋與篩選（支援分頁 / infinite scroll）。
     - Listing Detail — 動物詳細資訊、圖片 carousel、medical summary、申請入口。 
     - My Applications — 顯示使用者申請紀錄與狀態（一般會員）。
     - My Rehomes — 管理使用者的刊登資料（owner）。
     - Shelter Dashboard — 收容所會員專屬管理介面（刊登、批次上傳、申請審核）。
     - Admin Dashboard — 管理員後台（審核、系統監控、audit 查詢）。
   - 與其他層互動：透過 HTTPS/JSON REST API 與應用層交換資料；上傳流程為 presign→直傳 MinIO→回傳 metadata 給 API。

2) 應用層（Application Layer）
   - 技術：Flask（Blueprints 組織），使用 flask-smorest 以便與 OpenAPI contract 整合。
   - 主要職責：
     - 提供清晰且可版本化的 RESTful API（遵循 OpenAPI contract）。
     - 驗證 (authentication) 與授權 (authorization / RBAC / ownership checks)。
     - 實作業務邏輯並管理資料一致性與交易（transaction / optimistic locking）。
     - 管理附件 metadata、生成 presigned URLs 並驗證上傳擁有權。 
     - 對外排程長時間任務（enqueue job -> 202 + jobId）並監控 job lifecycle。
     - 寫入 AuditLog、處理 idempotency、rate-limiting 與錯誤重試策略。
     - 提供 observability hooks（traces、metrics、structured logs）與健康檢查 endpoints。
   - 背景任務處理（Worker）：Celery + Redis（或 RQ 為替代）負責處理長時間任務（batch import/export、檔案處理、外部系統整合）；API 使用 202 + jobId 模式回應並將工作放入 Redis 佇列。
   - API 規格：建議以 OpenAPI 3.x 為 source-of-truth（contract-first），從 OpenAPI 產生 frontend typed client 與 server validation skeleton。
   - 安全性：短生命 access token + refresh token；高權限操作建議 MFA；所有重要狀態變更寫入 AuditLog。
   - 可觀察性：OpenTelemetry traces、Prometheus metrics、Sentry error 收集。

3) 資料層（Data Layer）
   - 資料庫：MySQL (InnoDB)，使用 SQLAlchemy (Declarative) 與 Alembic 管理 schema 與 migrations（開發使用 docker-compose 的 MySQL，生產可選 RDS/Aurora MySQL 或自管集群）。
   - 物件儲存：MinIO（開發與生產）
       - 採用 MinIO：開發可在 docker-compose 使用單節點 MinIO 快速啟動，生產則採用 MinIO 分散式模式或透過 MinIO Operator / Helm 在 Kubernetes 部署以確保可用性與擴充性。


   ## 使用 MinIO 的實務建議（開發與生產）

   - 部署選項：
     - 開發：在 docker-compose 中啟動單節點 MinIO（快速、簡單）。
     - 生產：採用 MinIO 分散式模式（多節點）或在 Kubernetes 上使用 MinIO Operator / Helm chart，確保可用性與水平擴充。

   - 網路與安全：
     - 強制 TLS（NGINX/ALB 終端或 MinIO TLS）以保護簽名 URL 與物件傳輸安全。
     - 使用短期且權限受限的存取金鑰（access/secret）或從 Vault 取得 credentials，避免在程式碼中硬編碼。
     - 對不同用途（API server, presign service, admin）使用不同的 service account / policy，以最小權限原則授權。

   - CORS 與 Bucket Policy：
     - 為前端直傳設定適當 CORS 與 bucket policy，使瀏覽器能從前端直接上傳（PUT/POST）而不暴露過多權限。
     - presigned URL 流程仍需在後端做 ownership 驗證（確保上傳人有權對該 owner_id 建立 attachment metadata）。

   - Presign workflow 與驗證：
     - 後端產生 presigned URL（PUT 或 POST）給前端；前端使用該 URL 直接上傳至 MinIO，成功後呼叫 POST /attachments 建立 metadata（storageKey、url、owner_type、owner_id、checksum 等）。
     - 後端在收到 metadata 時應驗證：object 是否存在、大小與 checksum（可選）、且上傳者是否有權限建立該 metadata。

   - 上傳穩健性：
     - 對大型檔案採用 multipart upload；確保前端/後端能重試已中斷的 multipart 上傳。
     - 設定合理的 presign TTL（例如 5–15 分鐘），避免長時間暴露簽名 URL。

   - 運維、監控與備份：
     - 啟用 MinIO 的 Prometheus metrics 並將其接入現有的監控（Prometheus/Grafana）。
     - 使用 `mc`（MinIO Client）或 MinIO 的備份/鏡像機制（mc mirror / bucket replication）做跨區備援與長期備份。
     - 設定 object lifecycle（過期、轉儲）以管理儲存成本與法遵要求。

   - 相容性與限制：
     - MinIO 大部分情況下與 S3 API 相容，但某些 AWS 專屬功能（例如 KMS 與 IAM 深度整合、特定 server-side KMS 行為）可能不同；若依賴 AWS 特性請先驗證。
     - 在高併發或大型檔案場景下，請測試並調整分散式 MinIO 節點數、磁碟 I/O 與網路帶寬。

   - 實作提示（Flask 生態）：
     - 可使用 `minio` 或 `boto3` 兩種套件產生 presigned URLs；`minio` 官方套件於自管 MinIO 上較輕量，`boto3` 在與 AWS 測試時更方便。
     - 建議：後端僅發放 presign 並驗證 metadata；不要讓前端持有長期 credentials。

   - 範例資源：
     - Docker Compose 範例（dev）：minio service + console；
     - Kubernetes：MinIO Operator / Helm chart；
     - CLI：`mc` 用於 admin、mirror、policy 和 life-cycle 操作。

   - 安全備註：
     - 對於敏感檔案（例如身份文件、醫療紀錄），考慮在物件層加密（SSE）或在上傳前由後端進行應用層加密。
     - 定期輪轉 MinIO access keys 並監控未授權存取事件。
   - 快取與佇列（Optional）：Redis（task queue、cache、pub/sub for realtime）。
   - 主要職責：
     - 持久化域資料（users、shelters、animals、applications、attachments、audit_logs 等）。
     - 提供資料完整性（foreign keys、unique constraints）與效能（indexes、query patterns）。
     - 儲存 attachments metadata 並與 Object Storage 協調實際檔案位置。
     - 支援備份/還原策略、migration workflow（Alembic）與線上變更注意事項。
     - 提供 read replica 與分片策略以支援報表與大量讀取負載（視需要）。
     - 確保 transaction 與鎖定策略以支援審核流程與並發控制（optimistic locking）。
   - 設計注意事項：
     - 為高頻查詢欄位建立索引（animal.status, animal.city, application.status, attachment.owner_type/owner_id）。
     - Application.version 採 optimistic locking；create endpoints 支援 Idempotency-Key。 
     - Attachment 採 polymorphic owner (owner_type, owner_id)；metadata 存 DB，實際檔案存在 Object Storage。 

## 資料流說明（流程對應你提供的描述）
- 前端（Vue3）透過 HTTPS 向後端 Flask API 發送請求（JSON body / Bearer token）。
- API 層負責：驗證請求身份與權限；執行業務邏輯；存取 MySQL；處理 presigned upload 與 attachments metadata；若為長時間任務，將工作排入 Celery/Redis 佇列，並立即回傳 HTTP 202（Accepted）與 jobId。
- 背景工作處理器（Celery workers）從佇列中取出任務，進行非同步處理（如 CSV 匯入、圖片處理、外部 API 呼叫），並於完成後更新資料庫與 job/notification 狀態。

## 小結與實務建議
- 開發執行：先 scaffold minimal Flask app（create_app factory、extensions：db、migrate、redis、celery），搭配 docker-compose (mysql, redis, minio, api, worker) 做 local dev。 
- Migrations：使用 Alembic，採 expand-then-contract 策略並在部署中先跑後端 migrations。生產大型表格變更請採線上 schema change 工具（gh-ost / pt-online-schema-change）視情況而定。
- Jobs：所有長時間操作走 202 + jobId；worker 更新 job 表並發 Notification，前端可輪詢 /jobs/{jobId} 或透過 websocket/pubsub 得到進度。
- Security：對於敏感個資（phone, id）採加密 / tokenization；AuditLog 盡量 append-only 並限制刪除權限。

如需我把這段取代原來的三層說明（或把原文刪除/重構更大範圍），我可以接著執行（例如：同步更新文件中的模組映射、API surface 或產生相應的 scaffold）。

核心設計原則
- Contract-first：OpenAPI 作為前後端契約（自動生成 typed client、msw handler、server validation stub）。
- Job-first：長時間任務走 job pattern（POST -> 202 + jobId，worker 處理並更新 job status）。
- Idempotency & Concurrency：POST create 操作支持 Idempotency-Key；審核/assignment 使用 optimistic locking（version）與 DB-level transaction。
- Security & Audit：RBAC、AuditLog（actor、action、before、after），secrets in vault。

系統分層概覽
- CDN / Edge (TLS)
- Load Balancer / API Gateway
- API (Flask app, stateless) — horizontally scalable
- Background workers (Celery + Redis)
- Persistent stores: MySQL primary (+ replicas for read), S3 for attachments
- Observability: metrics, traces, logs
- CI/CD pipeline & artifact registry

模組映射（對應 `spec.md` 與 OpenAPI）
- Auth (register/login/refresh/verify)
- Users
- Shelters
- Animals / Rehomes
- Applications (submission, review, assignment)
- MedicalRecords
- Attachments / Uploads (presign + metadata)
- Notifications (DB-backed + worker delivery)
- Jobs (job table + worker supervisor)
- Audit (immutable-ish audit logs)
- Admin / Reporting

資料一致性與並發控制
- Use optimistic locking for review flows: Application.version + expected_version checks in update endpoints.
- Persist idempotency keys (table: idempotency_keys) with TTL to deduplicate POSTs.
- Presign upload flow: frontend requests presign -> direct upload to S3 -> POST /attachments to record metadata; validate storageKey and ownership on metadata write.

API 與合約（Contract-first）
- Produce OpenAPI 3.x skeleton and keep it authoritative (`specs/002-title-description-project/openapi.yaml`).
- From OpenAPI generate:
  - Frontend typed client (openapi-typescript -> placed in `frontend/src/api/generated/`)
  - MSW handlers / msw-rest for frontend testing & Storybook
  - Server validation helpers (pydantic models or auto-generated validators)

部署策略（分階段）
- Local / Dev: Docker Compose with MySQL, Redis, MinIO, api, worker
- Staging: Managed MySQL, Redis (ElastiCache), object storage; deploy via GitHub Actions -> image registry -> Kubernetes / Cloud Run / ECS; run smoke tests
- Production: Multi-AZ MySQL, Redis cluster, S3; HPA for API & workers; CDN for static assets; feature flags for rollout

CI/CD（建議 GitHub Actions）
Pipeline stages:
  1. PR: lint, typecheck (TS on frontend, mypy/ruff for backend), unit tests
  2. Integration: start ephemeral devstack (docker-compose) -> run integration tests (backend + migrations)
  3. Build images & push on merge
  4. Deploy to staging, run E2E (Playwright)
  5. Manual approval -> deploy to production + post-deploy health checks

資料庫遷移與發布策略
- Use Alembic for migrations; run migrations as separate CI/CD job before rolling deployment.
- Follow expand-then-contract pattern for schema changes and backfill steps in CI when needed.

備份與災難復原
- Nightly logical backups + binlog/WAL shipping; test restores regularly; store backups across regions.

觀測性與告警
- Metrics: P50/P95 latency, error rate, job queue length, failed job rate.
- Traces: propagate trace id from frontend to backend & workers via headers; instrument critical flows with OpenTelemetry.
- Alerts: latency or error spikes, job backlog growth, DB replication lag, audit write failures.

安全與合規
- Store secrets in a vault; limit CI secret exposure; rotate keys regularly.
- Enforce RBAC at middleware/guard level and validate ownership at service level.
- Audit: write audit log for state-changing actions; consider append-only storage and retention policy.

測試策略
- Unit: Vitest + @testing-library/vue for frontend; pytest for backend.
- Integration: run backend tests against ephemeral MySQL (docker-compose or testcontainers).
- Contract tests: generate mocks from OpenAPI and run consumer-driven contract tests between frontend and API.
- E2E: Playwright (critical flows: browse -> detail -> apply; batch import job; admin review flow).

運維與執行手冊（精簡）
- Incident: scale replicas, inspect Sentry & job queue, escalate DB issues.
- Job backlog: add workers, enable rate-limiting for large imports.
- Storage full: pause uploads, alert, and extend capacity or clean per retention policy.

短期可交付項目（優先順序）
1. 產出 OpenAPI 3.0 skeleton並 commit（`specs/002-title-description-project/openapi.yaml`）。
2. Scaffold minimal Flask backend + SQLAlchemy models + Alembic + Docker Compose dev stack（MySQL, Redis, MinIO, api, worker）。
3. Generate frontend typed client & msw handlers from OpenAPI，並建立 Storybook stories（Vue SFCs）。
4. Add GitHub Actions workflows for PR checks and staging deploy.

交付清單（初始）
- [ ] openapi.yaml created and reviewed
- [ ] backend scaffold generated (auth, animals, applications, uploads)
- [ ] sqlalchemy models & alembic migrations initialized
- [ ] docker-compose.dev.yml created (mysql, redis, minio, api, worker)
- [ ] frontend generated client in `frontend/src/api/generated/`
- [ ] storybook + msw handlers
- [ ] playwright E2E smoke test for main flow

風險與注意事項
- Mocks for third-party services (email, storage) are required in dev to avoid surprises.
- Data migrations must be planned and staged to avoid production data loss.
- Ensure audit log writes are reliable; enqueue writes if primary store is unreachable.

我可以立刻替你做的事（選一）：
1) 產出或更新 OpenAPI skeleton (`specs/002-title-description-project/openapi.yaml`) 並 commit（如果你需要我調整 schema 我也可以）。
2) scaffold minimal Flask backend + Docker Compose dev stack（會產生多個檔案）。
3) 產出 GitHub Actions workflow skeleton（lint/test/build/deploy-to-staging）。

請回覆你要我執行的項目（輸入 1/2/3 或描述其他任務），我會開始執行並把結果寫入倉庫。
