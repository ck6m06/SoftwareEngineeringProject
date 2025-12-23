## 前端架構設計（Developer-ready）

來源：`spec.md`（功能規格）與 `erd-generated.md`（資料模型）。

目標：給前端工程師一份可以立即落地的架構設計，包含專案結構、路由、重要元件/頁面 contract、資料流（fetch/cache/error）、驗證、測試建議、以及能被 scaffold 的下一步清單。

本專案採用：Vue 3 + TypeScript + Vite + Tailwind CSS（見 workspace frontend/）。下述建議基於此技術棧，並採用 @tanstack/vue-query、Pinia、Vee-validate + Zod、Storybook 與 Playwright 作為標準工具鏈。

---

## 簡短契約（Inputs / Outputs）
## 前端架構設計（Developer-ready — Vue 3 + Vite）

來源：`specs/002-title-description-project/spec.md`（功能規格）、`specs/002-title-description-project/erd-sql.md`（資料模型）與後端 OpenAPI（如存在）。

目的：提供一份能直接被前端工程師使用與 scaffold 的架構文件，內容包含：技術棧宣告、專案結構、模組分解、路由、上傳 presign contract（前後端共識）、測試策略、以及可執行的 next-steps（含 PowerShell 友好的命令示例）。

## 技術棧（已選定）
- 框架：Vue 3 + Vite（SPA，TypeScript）
- 狀態管理：Pinia
- Server-state：@tanstack/vue-query
- 表單驗證：vee-validate + Zod（zod 作為 schema/source-of-truth for runtime validation）
- UI 樣式：Tailwind CSS
- Component dev & docs：Storybook for Vue
- 測試：Vitest（unit） + @testing-library/vue、Playwright（E2E）
- Mock/Contract：msw + openapi-typescript（或 openapi-generator）

---

## 一句話契約（Inputs / Outputs）
- 輸入：`spec.md`（use-cases）、`erd-sql.md`（資料模型）、`openapi.yaml`（OpenAPI contract）
- 輸出：`frontend/src/api/generated/`（typed client）、components(SFC) 與 composables、Storybook stories、Vitest tests、Playwright flows

成功標準：前端可在 mock 環境下獨立實作 UI 與交互，並以 contract tests 保證與後端 API 對齊。

---

## 高階設計原則（簡要）
- Feature-first：以 domain/feature 為單位拆分模組，模組內包含 UI、composables、types、stories、tests。
- Contract-first：OpenAPI 作為 source-of-truth；前端使用 `openapi-typescript` 產出 types，並用 msw 建立 mock handlers。
- 單向資料流：components (presentational) 與 composables/stores (data & effects) 分離。
- 可測試：每個 composable 有 unit tests；主要流程（發佈、申請、上傳）有 E2E 覆蓋。

---

## 建議專案結構（可直接 scaffold）
frontend/
   - src/
      - api/                    # hand-written wrappers + generated client
         - generated/            # openapi-typescript output
         - client.ts             # thin wrapper (auth, error handling)
         - animals.ts
         - applications.ts
         - uploads.ts
      - components/
         - atoms/
         - molecules/
         - organisms/
      - pages/
         - Home.vue
         - Animals.vue
         - AnimalDetail.vue
         - RehomeForm.vue
         - MyRehomes.vue
         - Applications.vue
      - composables/
         - useAuth.ts
         - useInfiniteAnimals.ts
         - useUploadPresign.ts      # presign orchestration
         - useJobStatus.ts         # job polling
      - stores/
         - useAuth.ts
         - useNotifications.ts
      - router/
         - index.ts                # vue-router routes + guards
      - styles/
         - tailwind.css
      - types/
         - index.d.ts              # additional shared types (zod generated)
      - tests/
         - unit/
         - e2e/
      - main.ts
   - .storybook/
   - vite.config.ts
   - package.json

Notes: 把 generated client 放在 `src/api/generated/`；`src/api/client.ts` 提供 token refresh、拋錯與全域 header 管理。

---

## 路由設計（vue-router）

說明：下列路由設計為 Developer-ready 的建議，可直接實作於 `src/router/index.ts`。包含路由命名慣例、路由清單（name / path / component / meta）、route guard 行為與 prefetch 建議。

- 命名與慣例
   - path 使用小寫與 kebab-case（例如 `/animals`, `/animal-detail/:id`）。
   - route name 使用 PascalCase（例如 `AnimalsList`, `AnimalDetail`），方便在程式中使用 router.push({ name: 'AnimalDetail', params:{ id } }).
   - 所有 page components 放在 `src/pages/`，使用 lazy-loading（動態 import）以減少初始 bundle。

- 建議路由清單（name / path / component / meta）
   - Home
      - path: `/`, name: `Home`, component: `Home.vue`, meta: { public: true }
   - Animals list
      - path: `/animals`, name: `AnimalsList`, component: `Animals.vue`, meta: { public: true }
   - Animal detail
      - path: `/animals/:id`, name: `AnimalDetail`, component: `AnimalDetail.vue`, meta: { public: true }
   - Rehome publish
      - path: `/rehomes/new`, name: `RehomeNew`, component: `RehomeForm.vue`, meta: { requiresAuth: true, roles: ['GENERAL_MEMBER','SHELTER_MEMBER'] }
   - My rehomes
      - path: `/my/rehomes`, name: `MyRehomes`, component: `MyRehomes.vue`, meta: { requiresAuth: true }
   - Applications (my applications)
      - path: `/applications`, name: `Applications`, component: `Applications.vue`, meta: { requiresAuth: true }
   - Job status
      - path: `/jobs/:jobId`, name: `JobStatus`, component: `JobStatus.vue`, meta: { requiresAuth: true }
   - Admin root (nested)
      - path: `/admin`, name: `AdminRoot`, component: `AdminLayout.vue`, meta: { requiresAuth: true, roles: ['ADMIN'] }
      - children: `/admin/animals`, `/admin/applications`, `/admin/users` 等
   - Error & fallback
      - path: `/403`, name: `Forbidden`, component: `Forbidden.vue`
      - path: `/:pathMatch(.*)*`, name: `NotFound`, component: `NotFound.vue`

  
   ## 頁面與路由對照（Page ↔ Route 對應表）

   下表為 Developer-ready 的頁面與路由對照，可直接用來 scaffold `src/pages/*` 檔案、router route 陣列、以及對應的 API 呼叫與授權設定。每一列包含：路由名稱、path、建議元件位置、主要使用之 API endpoint、以及 meta（是否公開 / 需登入 / 角色限制）與實作注意事項。

   - Home
      - path: `/`
      - name: `Home`
      - component: `src/pages/Home.vue`
      - APIs: `GET /animals?featured=true` (首頁精選)、`GET /notifications` (若登入)
      - meta: { public: true }
      - notes: 輕量 prefetch 精選動物；若 user 已登入則可在 client 快取中合併通知 badge 資料

   - Animals list
      - path: `/animals`
      - name: `AnimalsList`
      - component: `src/pages/Animals.vue`
      - APIs: `GET /animals` (filters, pagination)
      - meta: { public: true }
      - notes: useInfiniteQuery，支援 URL query sync (page, filters)

   - Animal detail
      - path: `/animals/:id`
      - name: `AnimalDetail`
      - component: `src/pages/AnimalDetail.vue`
      - APIs: `GET /animals/{id}`, `GET /applications?animalId={id}`
      - meta: { public: true }
      - notes: prefetch in beforeResolve；show skeleton while loading；owner-related actions (edit/rehome) require ownership check via API or server-side permission

   - Rehome publish (create rehome/listing)
      - path: `/rehomes/new`
      - name: `RehomeNew`
      - component: `src/pages/RehomeForm.vue`
      - APIs: `POST /rehomes` (form submit), `POST /uploads/presign` (upload flow), `POST /attachments` (metadata create)
      - meta: { requiresAuth: true, roles: ['GENERAL_MEMBER','SHELTER_MEMBER'] }
      - notes: form uses vee-validate + zod; useUploadPresign.ts 管理 presign + upload + metadata create；使用 optimistic UI 或 upload-progress indicator

   - My rehomes
      - path: `/my/rehomes`
      - name: `MyRehomes`
      - component: `src/pages/MyRehomes.vue`
      - APIs: `GET /rehomes?ownerId={me}`, `DELETE /rehomes/{id}`
      - meta: { requiresAuth: true }
      - notes: requireAuth guard；在頁面載入時 prefetch user-owned listings

   - Applications (my applications)
      - path: `/applications`
      - name: `Applications`
      - component: `src/pages/Applications.vue`
      - APIs: `GET /applications?userId={me}`, `POST /applications`
      - meta: { requiresAuth: true }
      - notes: handle 409 conflict UX (idempotency) gracefully; show application status and ability to cancel

   - Job status
      - path: `/jobs/:jobId`
      - name: `JobStatus`
      - component: `src/pages/JobStatus.vue`
      - APIs: `GET /jobs/{jobId}`
      - meta: { requiresAuth: true }
      - notes: useJobStatus.ts composable for polling with backoff; show progress and link to results when ready

   - Admin root & children
      - path: `/admin`
      - name: `AdminRoot`
      - component: `src/layouts/AdminLayout.vue`
      - children: `/admin/animals` (`src/pages/admin/AnimalsAdmin.vue`), `/admin/applications` (`src/pages/admin/ApplicationsAdmin.vue`), `/admin/users` (`src/pages/admin/UsersAdmin.vue`)
      - APIs: admin-scoped endpoints (e.g., `GET /admin/animals`, `PUT /admin/animals/{id}`)
      - meta: { requiresAuth: true, roles: ['ADMIN'] }
      - notes: nested routes + lazy-loaded admin chunk; route-level RBAC enforced in beforeEach + server checks for sensitive actions

   - Login / Auth
      - path: `/login`
      - name: `Login`
      - component: `src/pages/Login.vue`
      - APIs: `POST /auth/login`, `POST /auth/refresh`
      - meta: { public: true }
      - notes: on successful login redirect to `redirect` query param; store tokens in secure storage (httpOnly cookie preferred; otherwise secure storage + refresh flow)

   - Forbidden
      - path: `/403`
      - name: `Forbidden`
      - component: `src/pages/Forbidden.vue`
      - meta: { public: true }
      - notes: used for RBAC denials

   - Not Found
      - path: `/:pathMatch(.*)*`
      - name: `NotFound`
      - component: `src/pages/NotFound.vue`
      - meta: { public: true }
      - notes: fallback route; optionally show helpful links and search box

      - Route guards 與行為（router.beforeEach）
   - 權限驗證：在 `beforeEach` 檢查 `to.meta.requiresAuth`；若需要登入但使用者未登入，redirect 到 `/login?redirect=...`。
   - 角色檢查：若 `to.meta.roles` 存在，讀取 `stores/useAuth` 的 user.role 判斷是否包含，若不包含則 redirect `/403`。
   - Owner 檢查（例如編輯某筆 rehome）：建議在頁面內以 API 驗證或在 `beforeEnter` 做一次 server-side ownership 檢查（避免 UI 假定所有權）。

- Prefetch 與 data fetching
   - 在 route enter 或 `beforeResolve` 呼叫 vue-query 的 prefetch（useQueryClient().prefetchQuery）以提前載入需要的資料，並在 component 中使用同樣的 query key 拿取快取資料。
   - 重要 detail 頁面（AnimalDetail）可搭配 Suspense / skeleton UI 提供更好的使用者體驗。

- Lazy-loading 與 chunk 命名
   - 使用動態 import 並給予 chunk 名稱以利 debug：
      - `const AnimalDetail = () => import(/* webpackChunkName: "animal-detail" */ '@/pages/AnimalDetail.vue')`

- 檔案/位置建議
   - `src/router/index.ts`：routes 陣列 + createRouter + guards（beforeEach）
   - `src/layouts/`：MainLayout.vue, AdminLayout.vue（供 nested routes 使用）
   - `src/pages/*`：route-level components

範例（文件用示意，不是完整程式碼）：
   - routes = [ { name: 'AnimalsList', path: '/animals', component: () => import('@/pages/Animals.vue'), meta: { public: true } }, ... ]

---

## 前端模組分解（feature-first）
1) Auth
    - 責任：登入/登出、token 管理、route-guards
    - 檔案：`stores/useAuth.ts`、`composables/useAuth.ts`、`components/auth/LoginForm.vue`
    - Endpoint：POST /auth/login, POST /auth/refresh

2) Browsing (Animals / Listings)
    - 責任：列表、篩選、分頁/無限滾動、快取策略
    - 檔案：`pages/Animals.vue`, `composables/useInfiniteAnimals.ts`, `components/AnimalCard.vue`
    - Endpoint：GET /animals?...

3) Animal Detail & Rehome
    - 責任：詳情頁、Rehome 表單（含 upload presign）、申請按鈕
    - 檔案：`pages/AnimalDetail.vue`, `pages/RehomeForm.vue`, `composables/useUploadPresign.ts`
    - Endpoint：GET /animals/{id}, POST /rehomes

4) Uploads / Attachments
    - 責任：取得 presign URL、執行直接上傳、POST metadata、提供上傳 progress 與 retry
    - 檔案：`composables/useUploadPresign.ts`, `components/FileUploader.vue`, `api/uploads.ts`
    - Endpoint：POST /uploads/presign, POST /attachments

5) Applications
    - 責任：提交與查詢申請、idempotency header 管理、顯示 409 錯誤 UX
    - 檔案：`pages/Applications.vue`, `composables/useApplication.ts`
    - Endpoint：POST /applications

6) Jobs / Admin / Notifications
    - 責任：job polling、admin pages、通知中心
    - 檔案：`composables/useJobStatus.ts`, `components/JobProgress.vue`, `stores/useNotifications.ts`
    - Endpoint：GET /jobs/{jobId}, GET /notifications

---

## Upload presign — 前後端契約範例（務必同步到後端文件）
建議把以下範例同時放在 `bmad_frontend-architecture.md` 與 `bmad_backend-architecture.md`，並在 OpenAPI `openapi.yaml` 內落實。

- POST /uploads/presign (Request)
   {
      "filename": "photo.jpg",
      "contentType": "image/jpeg",
      "ownerType": "rehomes",      // enum: rehomes|animal|medicalRecord|... 
      "ownerId": 123,
      "contentLength": 345678
   }

- 200 OK (Response)
   {
      "storageKey": "attachments/rehomes/123/20251017/uuid.jpg",
      "url": "https://minio.dev.example.com/attachments/....", // presigned URL
      "method": "PUT",
      "headers": { "Content-Type": "image/jpeg" },
      "expiresAt": "2025-10-17T15:23:00Z"
   }

Client 用該 `url` 與 `headers` 做 PUT，上傳成功後呼叫：

- POST /attachments (Request)
   {
      "storageKey": "attachments/rehomes/123/20251017/uuid.jpg",
      "ownerType": "rehomes",
      "ownerId": 123,
      "filename": "photo.jpg",
      "contentType": "image/jpeg",
      "size": 345678
   }

- 201 Created (Response)
   { "attachmentId": 456, "url": "...", "createdAt": "..." }

注意事項：
- presign TTL 建議 5–15 分鐘；不要回傳長期憑證。 
- 大檔案 (>50MB) 使用 multipart presign（在 OpenAPI 內標註或另提供 endpoint /uploads/multipart/initiate）。
- 前端應保留 retry 與 abort 機制；metadata create 應避免重複（server 可對 `storageKey` 加 unique constraint 或接受 Idempotency-Key）。

---

## Data fetching 與 cache 策略
- Lists: useInfiniteQuery(['animals', filters])，page size 與 cacheTime 根據流量調整。
- Detail: useQuery(['animal', id])，cacheTime 適中以平衡 fresh data 與 UX。
- Mutations: useMutation，搭配 optimistic updates 或 invalidation。
- 全域錯誤處理於 `src/api/client.ts`（axios/ky），401 自動嘗試 refresh token，失敗則 redirect to login。

---

## Type & Contract workflow
- 開發前：後端先產出 `specs/002-title-description-project/openapi.yaml`（contract-first）。
- 前端 CI job：使用 `openapi-typescript` 產生 types 並提交到 `frontend/src/api/generated/`。
- 前端在開發中使用 msw handlers（由 generated types 驅動）做 mock。

範例命令（PowerShell）:
```powershell
npx openapi-typescript specs/002-title-description-project/openapi.yaml --output frontend/src/api/generated/openapi-types.ts
```

若要產生 client（例如 axios wrapper），可使用 `openapi-generator-cli` 或手寫薄封裝。

---

## Testing strategy
- Unit：Vitest + @testing-library/vue，cover composables、stores 與小型 components。
- Storybook：components 與 interaction stories；整合 msw handlers 作為 stories 的 mock source。
- Contract tests：CI step 啟動 openapi mock server（或使用 generated msw handlers），執行前端 contract tests。
- E2E：Playwright（staging），重要流程：browse→detail→apply、rehome publish（含上傳）、shelter batch import（job pattern）。

---

## CI / DX 建議（最小可行）
- pre-commit：lint-staged (ESLint, Prettier, vitest run affected tests)
- CI pipeline：
   1. install deps
   2. generate openapi types (if openapi.yaml changed)
   3. build + vitest
   4. storybook build
   5. optional: playwright smoke tests against staging

---

## 可交付的下一步（我可以幫你做，選項）
1) 產生 typed client 與 msw handlers，路徑：`frontend/src/api/generated/`（我會把命令與 CI snippet 一併寫入）。
2) scaffold base Vue components 與 `useUploadPresign.ts` 範例實作（含 Storybook stories 與 msw handler 範例）。
3) 新增 Playwright E2E 範例（browse→detail→apply）與 CI 設定。
4) 同時做 1+2（最推薦，能最快得到可跑的 demo）。

請回覆你想執行的項目編號（1/2/3/4）或要求我先產生 patch 預覽。

---
完成者：automated architect action
