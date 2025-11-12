# 貓狗領養平台 (Pet Adoption Platform)

## 專案簡介

這是一個完整的貓狗領養平台系統，提供動物瀏覽、送養管理、領養申請、醫療紀錄管理等功能。

## 技術架構

### 前端 (Frontend)
- **框架**: Vue 3.4.21 + TypeScript 5.x + Vite 5.4.21
- **狀態管理**: Pinia 2.x
- **路由管理**: Vue Router 4.x (含角色型路由守衛)
- **表單驗證**: vee-validate + zod
- **UI 框架**: Tailwind CSS 3.x
- **日期處理**: date-fns (含 i18n zh-TW)
- **HTTP 客戶端**: Axios
- **圖片上傳**: 自定義 FileUploader 組件

### 後端 (Backend)
- **框架**: Flask 3.0.0 + flask-smorest (OpenAPI)
- **ORM**: SQLAlchemy 2.x
- **遷移工具**: Alembic
- **認證**: JWT (flask-jwt-extended)
- **任務隊列**: Celery 5.x
- **消息隊列**: Redis 7.x
- **API 文檔**: Swagger UI / ReDoc

### 資料庫與儲存
- **資料庫**: MySQL 8.0+ (InnoDB)
  - 支援軟刪除機制 (deleted_at)
  - 完整的外鍵約束
  - 審計日誌記錄
- **物件儲存**: MinIO (S3 相容)
- **快取**: Redis 7.x
- **會話管理**: Redis (Flask Session)

## 專案結構

```
proj_new/
├── backend/              # Flask 後端應用
│   ├── app/             # 應用主目錄
│   │   ├── blueprints/  # API 路由模組
│   │   │   ├── auth.py          # 身份驗證
│   │   │   ├── animals.py       # 動物管理
│   │   │   ├── applications.py  # 申請管理
│   │   │   ├── notifications.py # 通知系統
│   │   │   ├── jobs.py          # 任務管理
│   │   │   ├── shelters.py      # 收容所管理
│   │   │   └── admin.py         # 管理員功能
│   │   ├── models/      # SQLAlchemy 模型
│   │   │   ├── user.py          # 用戶模型
│   │   │   ├── animal.py        # 動物模型
│   │   │   ├── application.py   # 申請模型
│   │   │   └── others.py        # 其他模型
│   │   ├── services/    # 業務邏輯層
│   │   │   └── notification_service.py  # 通知服務
│   │   ├── utils/       # 工具函數
│   │   └── __init__.py  # Flask 應用工廠
│   ├── migrations/      # Alembic 遷移檔案
│   ├── config.py        # 設定檔
│   ├── requirements.txt # Python 依賴
│   └── run.py           # 應用入口
├── frontend/            # Vue 3 前端應用
│   ├── src/
│   │   ├── api/         # API 客戶端模組
│   │   │   ├── client.ts        # Axios 客戶端
│   │   │   ├── animals.ts       # 動物 API
│   │   │   ├── applications.ts  # 申請 API
│   │   │   ├── notifications.ts # 通知 API
│   │   │   └── jobs.ts          # 任務 API
│   │   ├── assets/      # 靜態資源
│   │   ├── components/  # Vue 組件
│   │   │   ├── layout/          # 佈局組件
│   │   │   ├── uploads/         # 上傳組件
│   │   │   └── NotificationBell.vue  # 通知鈴鐺
│   │   ├── composables/ # Composition API 邏輯
│   │   │   ├── useNotifications.ts  # 通知邏輯
│   │   │   └── useUpload.ts     # 上傳邏輯
│   │   ├── pages/       # 頁面組件
│   │   │   ├── Animals.vue          # 動物列表
│   │   │   ├── AnimalDetail.vue     # 動物詳情
│   │   │   ├── RehomeForm.vue       # 送養表單
│   │   │   ├── MyRehomes.vue        # 我的送養
│   │   │   ├── AdminUsers.vue       # 用戶管理
│   │   │   ├── Jobs.vue             # 任務列表
│   │   │   └── NotificationCenter.vue  # 通知中心
│   │   ├── router/      # 路由設定
│   │   │   └── index.ts         # 路由配置 (含角色守衛)
│   │   ├── stores/      # Pinia 狀態管理
│   │   │   └── auth.ts          # 認證狀態
│   │   ├── types/       # TypeScript 類型定義
│   │   └── App.vue      # 根組件
│   ├── package.json
│   └── vite.config.ts
├── docker/              # Docker 相關檔案
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
├── docker-compose.yml   # Docker Compose 設定
├── docs/                # 專案文檔
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

# 複製環境變數檔案
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 啟動所有服務
docker-compose up -d

# 初始化資料庫 (首次啟動時)
docker-compose exec backend flask db upgrade

# 建立測試帳號 (可選)
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
