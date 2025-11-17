# 貓狗領養平台 (Pet Adoption Platform)

## 專案簡介

這是一個完整的貓狗領養平台系統，提供動物瀏覽、送養管理、領養申請、醫療紀錄管理等功能。

## 技術架構

### 前端 (Frontend)
- **框架**: Vue 3.4.21 + TypeScript 5.x + Vite 5.1.6
- **狀態管理**: Pinia 2.1.7
- **路由管理**: Vue Router 4.3.0 (含角色型路由守衛)
- **表單驗證**: vee-validate 4.12.5 + zod 3.22.4
- **UI 框架**: Tailwind CSS 3.4.1
- **日期處理**: date-fns 4.1.0
- **HTTP 客戶端**: Axios 1.6.7
- **數據查詢**: TanStack Vue Query 5.28.4
- **測試框架**: Vitest + Playwright
- **代碼品質**: ESLint + Prettier

### 後端 (Backend)
- **框架**: Flask 3.0.0 + flask-smorest 0.42.3 (OpenAPI)
- **ORM**: SQLAlchemy 2.0.23 + Alembic 1.13.0
- **認證**: JWT (flask-jwt-extended 4.5.3)
- **任務隊列**: Celery 5.3.4
- **消息隊列**: Redis 5.0.1
- **安全加密**: bcrypt 4.1.2 + argon2-cffi 23.1.0
- **文件存儲**: MinIO 7.2.0 + boto3 1.34.12
- **限流保護**: Flask-Limiter 3.5.0
- **監控追蹤**: Sentry SDK 1.39.1
- **測試框架**: pytest 7.4.3 + pytest-flask
- **API 文檔**: Swagger UI / ReDoc

### 資料庫與儲存
- **關聯資料庫**: MySQL 8.0+ (InnoDB 引擎)
  - 支援軟刪除機制 (deleted_at)
  - 完整的外鍵約束與索引優化
  - 審計日誌與操作追蹤
- **對象存儲**: MinIO (S3 兼容 API)
  - 圖片與附件文件存儲
  - 分桶管理與權限控制
- **緩存系統**: Redis 7.x
  - 會話管理 (Flask Session)
  - Celery 任務隊列
  - 應用層緩存

## 專案結構

```
proj_new/
├── backend/              # Flask 後端應用
│   ├── app/             # 應用主目錄
│   │   ├── blueprints/  # API 路由模組
│   │   │   ├── auth.py          # 身份驗證與授權
│   │   │   ├── animals.py       # 動物管理
│   │   │   ├── applications.py  # 領養申請管理
│   │   │   ├── admin.py         # 管理員功能
│   │   │   ├── jobs.py          # 背景任務管理
│   │   │   ├── medical_records.py # 醫療紀錄
│   │   │   ├── notifications.py # 通知系統
│   │   │   ├── shelters.py      # 收容所管理
│   │   │   ├── uploads.py       # 檔案上傳
│   │   │   └── users.py         # 用戶管理
│   │   ├── models/      # SQLAlchemy 數據模型
│   │   │   ├── user.py          # 用戶模型
│   │   │   ├── animal.py        # 動物模型
│   │   │   ├── application.py   # 申請模型
│   │   │   ├── medical_record.py # 醫療紀錄模型
│   │   │   ├── shelter.py       # 收容所模型
│   │   │   ├── pending_registration.py # 待註冊模型
│   │   │   └── others.py        # 其他輔助模型
│   │   ├── services/    # 業務邏輯服務層
│   │   │   ├── email_service.py    # 郵件服務
│   │   │   ├── notification_service.py # 通知服務
│   │   │   └── audit_service.py    # 審計服務
│   │   ├── tasks/       # Celery 背景任務
│   │   ├── templates/   # Jinja2 郵件模板
│   │   ├── utils/       # 工具函數庫
│   │   └── __init__.py  # Flask 應用工廠
│   ├── migrations/      # Alembic 數據庫遷移檔案
│   ├── scripts/         # 部署與維護腳本
│   ├── tests/           # 後端單元測試
│   ├── config.py        # 應用配置檔
│   ├── requirements.txt # Python 依賴清單
│   └── run.py           # 應用啟動入口
├── frontend/            # Vue 3 前端應用
│   ├── src/
│   │   ├── api/         # API 客戶端模組
│   │   │   ├── client.ts        # Axios HTTP 客戶端
│   │   │   ├── animals.ts       # 動物相關 API
│   │   │   ├── applications.ts  # 申請相關 API
│   │   │   ├── jobs.ts          # 任務相關 API
│   │   │   ├── medicalRecords.ts # 醫療紀錄 API
│   │   │   ├── shelters.ts      # 收容所 API
│   │   │   ├── uploads.ts       # 檔案上傳 API
│   │   │   ├── users.ts         # 用戶管理 API
│   │   │   └── auditLogs.ts     # 審計日誌 API
│   │   ├── components/  # Vue 可重用組件
│   │   │   ├── layout/          # 佈局組件
│   │   │   ├── uploads/         # 檔案上傳組件
│   │   │   └── common/          # 通用 UI 組件
│   │   ├── composables/ # Composition API 邏輯
│   │   │   ├── useNotifications.ts # 通知邏輯
│   │   │   ├── useUpload.ts    # 檔案上傳邏輯
│   │   │   └── useAuth.ts      # 認證邏輯
│   │   ├── pages/       # 頁面路由組件
│   │   │   ├── Animals.vue          # 動物列表頁面
│   │   │   ├── AnimalDetail.vue     # 動物詳情頁面
│   │   │   ├── RehomeForm.vue       # 送養表單頁面
│   │   │   ├── MyRehomes.vue        # 我的送養管理
│   │   │   ├── ApplicationReview.vue # 申請審核頁面
│   │   │   ├── MedicalRecords.vue   # 醫療紀錄頁面
│   │   │   ├── AdminDashboard.vue   # 管理員控制台
│   │   │   ├── AdminUsers.vue       # 用戶管理頁面
│   │   │   ├── ShelterDashboard.vue # 收容所控制台
│   │   │   ├── Jobs.vue             # 任務列表頁面
│   │   │   ├── AuditLogs.vue        # 審計日誌頁面
│   │   │   └── NotificationCenter.vue # 通知中心
│   │   ├── router/      # 路由配置
│   │   │   └── index.ts         # 路由定義 (含角色守衛)
│   │   ├── stores/      # Pinia 狀態管理
│   │   │   └── auth.ts          # 認證狀態管理
│   │   ├── types/       # TypeScript 類型定義
│   │   └── App.vue      # 根組件
│   ├── package.json     # Node.js 依賴配置
│   ├── vite.config.ts   # Vite 建構配置
│   ├── tailwind.config.js # Tailwind CSS 配置
│   └── tsconfig.json    # TypeScript 配置
├── docker/              # Docker 容器化檔案
│   ├── backend.Dockerfile    # 後端容器定義
│   ├── frontend.Dockerfile  # 前端容器定義
│   └── nginx.conf           # Nginx 反向代理配置
├── docker-compose.yml   # Docker Compose 多服務編排
├── docs/                # 專案技術文檔
│   ├── api/             # API 文檔
│   └── development.md   # 開發指南
├── TEST_ACCOUNTS.md     # 測試帳號說明文檔
├── CREATE_TEST_ACCOUNTS_GUIDE.md # 測試帳號建立指南
└── README.md            # 專案說明文檔
```
│   ├── api/
│   │   └── README.md    # API 使用指南
│   └── development.md   # 開發指南
├── TEST_ACCOUNTS.md     # 測試帳號文檔
├── DRAFT_SAVE_FIX.md    # 草稿儲存修復說明
├── NOTIFICATION_DROPDOWN_FIX.md  # 通知下拉選單修復說明
└── README.md            # 專案說明
```

## 快速開始

### 環境需求

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- MySQL 8.0+

### 使用 Docker Compose 啟動（推薦）

```bash
# 移除所有服務(刪除所有SQL和minio圖片資料，重啟)(可選)
docker-compose down -v

# 複製環境變數檔案（包含預配置的Gmail SMTP設定）
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 啟動所有服務
docker-compose up -d

# 等待服務完全啟動（約15秒）
timeout 15  # Windows: timeout /t 15

# 初始化資料庫（首次啟動時）
docker-compose exec backend flask db upgrade
# 如遇到遷移問題，執行：
# docker-compose exec backend flask db stamp f024b1dbf16b

# 建立測試帳號（推薦）
docker-compose exec backend python create_test_accounts.py

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

服務將在以下端口運行：
- 前端: http://localhost:5173 (Vite dev server with HMR 🔥)
- 後端 API: http://localhost:5000
- API 文檔: http://localhost:5000/api/docs
- MinIO 控制台: http://localhost:9001
- MySQL: localhost:3307
- Redis: localhost:6379

**郵件功能**：
- ✅ **SMTP 已預配置** - 使用 Gmail SMTP (usershelter702@gmail.com)
- 📧 **註冊驗證郵件** - 新用戶註冊時自動發送
- 🔐 **密碼重設郵件** - 忘記密碼時發送重設連結
- 📋 **領養申請通知** - 申請審核結果自動通知
- 測試 SMTP: `docker-compose exec backend python -c "from app import create_app; from app.services.email_service import email_service; app = create_app(); app.app_context().__enter__(); print('SMTP 測試:', email_service.send_verification_email('test@example.com', 'test', 'token123'))"`

**開發注意事項:**
- 前端支援熱模組替換 (HMR)，修改程式碼後瀏覽器會自動刷新
- 後端修改需要重啟容器: `docker-compose restart backend`
- 完整 Docker 使用指南請參考: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

### Docker 服務說明

專案使用 Docker Compose 管理以下服務：

| 服務 | 說明 | 端口 |
|------|------|------|
| backend | Flask API 伺服器 | 5000 |
| frontend | Vue 3 開發伺服器 | 5173 |
| mysql | MySQL 8.0 資料庫 | 3307 |
| redis | Redis 快取與消息隊列 | 6379 |
| minio | MinIO 物件儲存 | 9000, 9001 |
| celery_worker | Celery 背景任務執行器 | - |
| celery_beat | Celery 定時任務排程器 | - |

**查看服務日誌**:
```bash
docker-compose logs -f backend    # 查看後端日誌
docker-compose logs -f frontend   # 查看前端日誌
docker-compose logs -f celery_worker  # 查看 Celery 日誌
```

### 本地開發

#### 後端設置

```bash
cd backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env

# 初始化資料庫
flask db upgrade

# 啟動開發伺服器
python run.py
```

#### 前端設置

```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev

# 建立生產版本
npm run build
```

## 主要功能模組

### 1. 動物瀏覽與搜尋
- 動物列表瀏覽 (分頁、篩選)
- 進階搜尋與篩選 (物種、性別、收容所)
- 動物詳情檢視 (含圖片、醫療記錄)
- 領養申請提交

### 2. 送養管理
- 個人送養發佈與管理 (草稿儲存、提交審核)
- 收容所送養發佈與批次匯入
- 送養狀態管理 (草稿/審核中/已發布/已下架)
- 圖片上傳與管理
- 我的送養列表

### 3. 申請審核
- 申請列表瀏覽
- 申請狀態管理與指派
- 申請審核作業 (核准/拒絕)
- 自動通知機制

### 4. 醫療紀錄
- 醫療紀錄新增與檢視
- 醫療紀錄驗證 (僅收容所會員和管理員)
- 醫療記錄附件管理

### 5. 系統管理
- 使用者管理 (搜尋、篩選、封禁)
- 權限管理 (角色型權限控制 - RBAC)
- 資料審核
- 審計日誌
- 任務管理與審批

### 6. 通知中心
- 即時通知 (定期輪詢機制)
- 7 種通知類型支援
- 通知已讀/未讀管理
- 通知刪除功能
- 下拉選單快速檢視

### 7. 收容所管理
- 收容所資訊管理
- 收容所動物批次匯入
- 收容所會員專屬功能

### 8. 背景任務系統
- 用戶資料刪除任務
- 資料匯出任務
- 批次更新任務
- 任務狀態追蹤
- 管理員審批流程

### 9. 郵件通知系統
- **註冊驗證郵件** - 新用戶註冊後自動發送 24 小時有效驗證連結
- **密碼重設郵件** - 忘記密碼時發送 1 小時有效重設連結  
- **領養申請通知** - 申請核准/拒絕時自動通知申請人
- **申請狀態更新** - 包含審核意見和收容所聯絡資訊
- **異步發送機制** - 使用 Celery 任務隊列，支援重試和錯誤處理
- **Gmail SMTP 集成** - 預配置 Gmail SMTP 服務，開箱即用

## API 文檔

API 文檔使用 OpenAPI 3.0 規範，可通過以下方式訪問：

- Swagger UI: http://localhost:5000/api/docs
- ReDoc: http://localhost:5000/api/redoc
- OpenAPI JSON: http://localhost:5000/api/openapi.json

詳細的 API 使用指南請參考 [docs/api/README.md](docs/api/README.md)

### 主要 API 端點

#### 身份驗證
- `POST /api/auth/register` - 用戶註冊
- `POST /api/auth/login` - 用戶登入
- `POST /api/auth/refresh` - 刷新 Token
- `GET /api/auth/me` - 取得當前用戶資訊

#### 動物管理
- `GET /api/animals` - 取得動物列表
- `GET /api/animals/{id}` - 取得動物詳情
- `POST /api/animals` - 建立動物 (支援草稿)
- `PATCH /api/animals/{id}` - 更新動物
- `POST /api/animals/{id}/submit` - 提交審核
- `DELETE /api/animals/{id}` - 刪除動物

#### 申請管理
- `GET /api/applications` - 取得申請列表
- `POST /api/applications` - 建立申請
- `POST /api/applications/{id}/review` - 審核申請

#### 通知系統
- `GET /api/notifications` - 取得通知列表
- `POST /api/notifications/{id}/read` - 標記已讀
- `POST /api/notifications/read-all` - 全部標記已讀
- `DELETE /api/notifications/{id}` - 刪除通知

#### 任務管理
- `GET /api/jobs` - 取得任務列表
- `POST /api/jobs/{id}/approve` - 審批任務 (管理員)
- `POST /api/jobs/{id}/reject` - 拒絕任務 (管理員)

#### 管理員功能
- `GET /api/admin/users` - 取得用戶列表
- `POST /api/admin/users/{id}/ban` - 封禁用戶

### 測試帳號

#### 快速生成測試帳號

使用以下命令快速建立所有測試帳號：

```bash
# Docker 環境（推薦）
docker-compose exec backend python create_test_accounts.py
```

詳細說明請參考: [CREATE_TEST_ACCOUNTS_GUIDE.md](CREATE_TEST_ACCOUNTS_GUIDE.md)

#### 可用測試帳號

開發環境提供以下測試帳號：

| 角色 | Email | 密碼 | 權限 |
|------|-------|------|------|
| 管理員 | admin@test.com | Admin123 | 完整管理權限 |
| 收容所會員 | shelter@test.com | Shelter123 | 收容所管理功能 |
| 一般會員 | user@test.com | User123 | 基本用戶功能 |
| 一般會員2 | user2@test.com | User123 | 額外測試帳號 |

**真實郵件測試**：
- 您可以用真實的 Gmail 地址註冊新帳號來測試郵件功能
- 系統會發送真實的驗證郵件到您的信箱（請檢查垃圾郵件夾）
- 郵件包含驗證連結和 24 小時有效的 token
- 發送者：usershelter702@gmail.com

**注意**: 
- 測試帳號僅供開發環境使用，生產環境請使用強密碼
- 完整的測試帳號清單和問題排查請參考 [TEST_ACCOUNTS.md](TEST_ACCOUNTS.md)

## 測試

### 後端測試

```bash
cd backend
pytest tests/
```

### 前端測試

```bash
cd frontend
npm run test:unit      # 單元測試
npm run test:e2e       # E2E 測試
```

## 部署

詳細的部署指南請參考 [docs/deployment.md](docs/deployment.md)

## 開發指南

詳細的開發指南請參考 [docs/development.md](docs/development.md)

### 常見問題

#### Q: 通知下拉選單點擊後立即關閉？
使用 `@click.stop` 修飾符阻止事件冒泡。參考 `frontend/src/components/NotificationBell.vue`

#### Q: 儲存草稿沒有呼叫 API？
確保 `saveDraft()` 函數正確呼叫 `createAnimal()` 或 `updateAnimal()`。參考 `frontend/src/pages/RehomeForm.vue`

#### Q: 測試帳號無法登入？
可能是帳號被軟刪除，使用以下 SQL 恢復：
```sql
UPDATE users SET deleted_at = NULL WHERE email = 'admin@test.com';
```

更多問題請參考 [docs/development.md](docs/development.md) 的常見問題區塊。

## 最近更新 (2025-10-26)

### 新增功能
- ✅ **通知系統完整實作** - 7 種通知類型，自動觸發機制
- ✅ **任務審批系統** - 管理員可審批/拒絕背景任務
- ✅ **用戶管理介面** - 搜尋、篩選、封禁功能
- ✅ **草稿持久化** - 草稿儲存到資料庫，避免資料遺失
- ✅ **通知下拉選單** - 快速檢視未讀通知

### 修復問題
- ✅ 通知下拉選單開啟後立即關閉
- ✅ 草稿只儲存到 localStorage 問題
- ✅ AdminUsers.vue 編譯錯誤
- ✅ 軟刪除帳號登入問題
- ✅ AdminDashboard 載入錯誤

### 技術改進
- 優化事件處理機制 (v-click-outside directive)
- 改進 API 錯誤處理
- 增強表單驗證
- 完善測試帳號管理

## 專案文檔

- [API 文檔](docs/api/README.md) - 完整的 API 使用指南
- [開發指南](docs/development.md) - 開發流程和常見問題
- [測試帳號](TEST_ACCOUNTS.md) - 測試帳號清單和問題排查
- [快速生成測試帳號](CREATE_TEST_ACCOUNTS_GUIDE.md) - 測試帳號生成腳本使用指南
- [Docker 使用指南](DOCKER_GUIDE.md) - Docker 部署和開發指南

## 授權

本專案僅供學習使用。

## 開發團隊

軟體工程專案 - 中期作業

## 版本歷史

- v0.3.0 (2025-10-26) - 通知系統、任務審批、用戶管理完整實作
  - 新增通知系統 (7 種通知類型)
  - 新增任務審批流程
  - 新增用戶管理介面
  - 修復草稿儲存問題
  - 修復通知下拉選單問題
  - 完善測試帳號管理
- v0.2.0 (2025-10-24) - 核心功能實作
  - 動物管理功能
  - 申請審核系統
  - 收容所管理
  - 醫療記錄管理
- v0.1.0 (2025-10-22) - 初始專案架構建立
  - 前後端分離架構
  - Docker Compose 環境
  - 基礎認證系統