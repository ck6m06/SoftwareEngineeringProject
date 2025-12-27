# 🐾 貓狗領養平台 (Pet Adoption Platform)

一個完整的貓狗領養平台系統，提供動物瀏覽、送養管理、領養申請、醫療紀錄管理等功能。

[![License](https://img.shields.io/badge/license-Educational-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-supported-2496ED.svg)](https://www.docker.com/)

---

## 📑 目錄

- [快速開始](#-快速開始)
- [技術架構](#️-技術架構)
- [專案結構](#-專案結構)
- [主要功能](#-主要功能模組)
- [API 文檔](#-api-文檔)
- [測試帳號](#-測試帳號)
- [開發指南](#-開發指南)
- [專案文檔](#-專案文檔)
- [版本歷史](#-版本歷史)

---

## 🚀 快速開始

### 環境需求

- Docker & Docker Compose（推薦）
- Node.js 18+ / Python 3.10+（本地開發）
- MySQL 8.0+（本地開發）

### 一鍵啟動（使用 Docker）

```bash
# 0. 進入專案目錄
cd code/project

# 1. 移除先前部屬docker(可選)
docker compose down -v

# 2. 複製環境變數檔案
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. 啟動所有服務
docker compose up -d

# 4. 初始化資料庫（首次啟動）
docker compose exec backend flask db upgrade

# 5. 建立測試帳號
docker compose exec backend python create_test_accounts.py

# 6. 訪問服務
# 前端: http://localhost:5173
# 後端 API: http://localhost:5000
# API 文檔: http://localhost:5000/api/docs
```

**💡 提示**: 
- 前端支援熱模組替換 (HMR)，修改程式碼後自動刷新
- SMTP 已預配置 Gmail，註冊驗證郵件自動發送

### Docker 服務列表

| 服務 | 說明 | 端口 |
|------|------|------|
| frontend | Vue 3 開發伺服器 | 5173 |
| backend | Flask API 伺服器 | 5000 |
| mysql | MySQL 8.0 資料庫 | 3307 |
| redis | Redis 快取與消息隊列 | 6379 |
| minio | MinIO 物件儲存 | 9000, 9001 |
| celery-worker | Celery 背景任務 | - |

---

## 🏗️ 技術架構

### 前端 (Frontend)
- **框架**: Vue 3.4.21 + TypeScript 5.4.2 + Vite 5.1.6
- **狀態管理**: Pinia 2.x
- **路由管理**: Vue Router 4.x (含角色型路由守衛)
- **表單驗證**: vee-validate + zod
- **UI 框架**: Tailwind CSS 3.x
- **日期處理**: date-fns 4.1.0 (含 i18n zh-TW)
- **HTTP 客戶端**: Axios 1.6.7
- **圖片上傳**: 自定義 FileUploader 組件

### 後端 (Backend)
- **框架**: Flask 3.0.0 + flask-smorest 0.42.3 (OpenAPI)
- **ORM**: SQLAlchemy 2.x
- **遷移工具**: Alembic
- **認證**: JWT (flask-jwt-extended 4.5.3)
- **任務佇列**: Celery 5.3.4
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

---

## 📁 專案結構

```
code/
├── project/              # 主要專案代碼
│   ├── backend/          # Flask 後端應用
│   │   ├── app/          # 應用主目錄
│   │   │   ├── blueprints/    # API 路由模組
│   │   │   ├── models/        # SQLAlchemy 模型
│   │   │   ├── services/      # 業務邏輯層
│   │   │   └── utils/         # 工具函數
│   │   ├── migrations/        # Alembic 遷移檔案
│   │   ├── config.py          # 設定檔
│   │   ├── requirements.txt   # Python 依賴
│   │   └── run.py             # 應用入口
│   ├── frontend/         # Vue 3 前端應用
│   │   ├── src/
│   │   │   ├── api/           # API 客戶端模組
│   │   │   ├── components/    # Vue 組件
│   │   │   ├── composables/   # Composition API
│   │   │   ├── pages/         # 頁面組件
│   │   │   ├── router/        # 路由設定
│   │   │   ├── stores/        # Pinia 狀態管理
│   │   │   └── types/         # TypeScript 類型
│   │   └── package.json
│   ├── docker/           # Docker 相關檔案
│   ├── BatchUploadExample/    # 批次上傳範例
│   └── docker-compose.yml     # Docker Compose 設定
└── docs/                 # 完整專案文檔
    ├── api-tests/        # API 測試報告
    ├── fixes/            # 問題修復文檔
    ├── guides/           # 使用指南
    ├── logs/             # 系統日誌
    ├── refactoring/      # 重構文檔
    ├── reports/          # 各類報告
    ├── scripts/          # 測試腳本
    └── test-plans/       # 測試計劃
```

<details>
<summary><b>查看完整目錄結構</b></summary>

詳細的檔案結構請參考 [FOLDER_STRUCTURE.md](code/docs/FOLDER_STRUCTURE.md)

</details>

---

## ✨ 主要功能模組

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

---

## 🔌 API 文檔

API 文檔使用 OpenAPI 3.0 規範，可通過以下方式訪問：

- Swagger UI: http://localhost:5000/api/docs
- ReDoc: http://localhost:5000/api/redoc
- OpenAPI JSON: http://localhost:5000/api/openapi.json

詳細的 API 說明請訪問 Swagger UI: http://localhost:5000/api/docs

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

---

## 👤 測試帳號

#### 快速生成測試帳號

使用以下命令快速建立所有測試帳號：

```bash
# Docker 環境（推薦）
cd code/project
docker compose exec backend python create_test_accounts.py
```

詳細說明請參考: [CREATE_TEST_ACCOUNTS_GUIDE.md](code/docs/guides/CREATE_TEST_ACCOUNTS_GUIDE.md)

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
- 詳細的測試帳號建立流程請參考 [CREATE_TEST_ACCOUNTS_GUIDE.md](code/docs/guides/CREATE_TEST_ACCOUNTS_GUIDE.md)

---

## 👨‍💻 開發指南

### 本地開發環境設置

**後端開發**:
```bash
cd code/project/backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env

# 運行開發服務器
flask run --debug
```

**前端開發**:
```bash
cd code/project/frontend

# 安裝依賴
npm install

# 運行開發服務器
npm run dev
```

### 資料庫遷移

```bash
# 建立遷移
docker compose exec backend flask db migrate -m "描述"

# 執行遷移
docker compose exec backend flask db upgrade

# 回退遷移
docker compose exec backend flask db downgrade
```

### Celery 背景任務

Celery Worker 用於處理異步任務（郵件發送、批次處理等）

```bash
# 啟動 Celery Worker
docker compose up celery-worker

# 查看任務日誌
docker compose logs -f celery-worker
```

### 測試

#### 後端單元測試

**使用 Docker 執行測試**:
```bash
# 在專案根目錄
cd code/project

# 執行所有測試（詳細輸出）
docker compose exec backend bash -c "export PYTHONPATH=/app:\$PYTHONPATH && pytest tests/unit -v"

# 執行所有測試（簡化輸出）
docker compose exec backend bash -c "export PYTHONPATH=/app:\$PYTHONPATH && pytest tests/unit -q"

# 生成覆蓋率報告
docker compose exec backend bash -c "export PYTHONPATH=/app:\$PYTHONPATH && pytest tests/unit --cov=app/services --cov-report=term --cov-report=html"

# 查看特定服務的覆蓋率
docker compose exec backend bash -c "export PYTHONPATH=/app:\$PYTHONPATH && pytest tests/unit --cov=app/services/auth_service --cov=app/services/permission_service --cov-report=term-missing"
```

**測試成果**:
- ✅ **353 個單元測試全部通過**
- ✅ **94% 服務層覆蓋率**（1641 statements, 91 missed）
- ✅ **100% 覆蓋**：attachment_service, audit_service
- ✅ **95%+ 覆蓋**：auth_service (95%), permission_service (97%)

**測試架構說明**：
本專案採用**服務層優先**測試策略，聚焦於 `app/services/` 的業務邏輯層：
- 使用 Mock 技術隔離外部依賴（資料庫、MinIO、Redis、SMTP）
- 透過 Fixture 提供可重複使用的測試資料
- 每個測試獨立運行，確保結果可靠

#### 後端整合測試

**使用 Docker 執行測試**:
```bash
# 在專案根目錄
cd code/project

# 執行所有整合測試
docker compose exec backend bash -c "export PYTHONPATH=/app:\$PYTHONPATH && pytest tests/integration -v"

# 執行特定模組
docker compose exec backend bash -c "export PYTHONPATH=/app:\$PYTHONPATH && pytest tests/integration/test_animal_integration.py -v"
```

**整合測試成果**:
- ✅ **高通過率** (認證系統完全修復)
- ✅ **JWT 認證問題已解決** - 修正 token subject 類型錯誤
- 📊 **核心功能測試**：
  - Auth (認證系統): 7/7 tests ✅ 全部通過
  - Medical (醫療紀錄): 6 tests
  - Notification (通知系統): 8 tests
  - Shelter (收容所管理): 10 tests
  - User (使用者管理): 11 tests
  - Animal (動物管理)、Application (申請管理)

**整合測試說明**：
- 整合測試使用 SQLite 記憶體資料庫（`:memory:`）
- 驗證完整的 Route → Service → ORM → Database 流程
- 測試涵蓋完整的 API 端點與業務流程
- 每個測試獨立運行，確保測試間無互相影響
- **已修復**: JWT token identity 類型問題（從整數改為字串）

**前端測試**:
```bash
cd code/project/frontend
npm run test:e2e       # E2E 測試
```

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

更多問題請參考 [code/docs/fixes/ISSUES_AND_SOLUTIONS.md](code/docs/fixes/ISSUES_AND_SOLUTIONS.md) 的問題解決方案。

詳細的開發指南請參考：
- [開發文檔](code/docs/development.md)
- [Celery Worker 指南](code/docs/guides/CELERY_WORKER_GUIDE.md)
- [任務審批指南](code/docs/guides/JOB_APPROVAL_GUIDE.md)
- [通知觸發指南](code/docs/guides/NOTIFICATION_TRIGGERS_GUIDE.md)

---

## 📚 專案文檔

### 核心文檔
- [專案概述](code/docs/README.md) - 專案整體說明
- [資料夾結構](code/docs/FOLDER_STRUCTURE.md) - 完整目錄結構
- [開發文檔](code/docs/development.md) - 開發環境與流程
- [序列圖說明](code/docs/SEQUENCE_DIAGRAMS_README.md) - 系統互動流程

### 測試與驗證
- [API 測試報告](code/docs/api-tests/API_TEST_REPORT.md)
- [API 驗證報告](code/docs/api-tests/API_VALIDATION_REPORT.md)
- [前端測試報告](code/docs/reports/FRONTEND_TEST_REPORT.md)
- [初始化測試報告](code/docs/reports/INITIALIZATION_TEST_REPORT.md)
- [測試計劃](code/docs/test-plans/) - Phase 1-9 完整測試指南

### 問題修復
- [修復記錄](code/docs/fixes/FIXES.md) - 所有修復的問題
- [問題與解決方案](code/docs/fixes/ISSUES_AND_SOLUTIONS.md)
- [草稿儲存修復](code/docs/fixes/DRAFT_SAVE_FIX.md)
- [通知下拉選單修復](code/docs/fixes/NOTIFICATION_DROPDOWN_FIX.md)
- [時區遷移](code/docs/fixes/TIMEZONE_MIGRATION.md)

### 重構文檔
- [重構指南](code/docs/refactoring/REFACTORING_GUIDE.md)
- [重構進度](code/docs/refactoring/REFACTORING_PROGRESS.md)
- [重構完成報告](code/docs/refactoring/REFACTORING_COMPLETE.md)
- [最終重構報告](code/docs/refactoring/REFACTORING_FINAL_REPORT.md)

### 系統報告
- [架構審查](code/docs/reports/ARCHITECTURE_REVIEW.md)
- [部署成功報告](code/docs/reports/DEPLOYMENT_SUCCESS.md)
- [實作計劃](code/docs/reports/IMPLEMENTATION_PLAN.md)
- [系統修復報告](code/docs/reports/SYSTEM_FIXES_REPORT.md)
- [問題狀態報告](code/docs/reports/ISSUES_STATUS_REPORT.md)

### 使用指南
- [Celery Worker 指南](code/docs/guides/CELERY_WORKER_GUIDE.md)
- [建立測試帳號指南](code/docs/guides/CREATE_TEST_ACCOUNTS_GUIDE.md)
- [任務審批指南](code/docs/guides/JOB_APPROVAL_GUIDE.md)
- [通知觸發指南](code/docs/guides/NOTIFICATION_TRIGGERS_GUIDE.md)

---

## 📋 版本歷史

- **v0.3.0** (2024-12-25) - 時區修正、MinIO 整合、文檔完善
- **v0.2.0** (2024-11-15) - 通知系統、任務審批、用戶管理完整實作
- **v0.1.0** (2024-10-01) - 核心功能實作（動物管理、申請審核）

---

## 📄 授權

本專案僅供教育用途使用。

---

## 🙏 致謝

感謝所有貢獻者對本專案的支持與協助。
- ✅ 草稿只儲存到 localStorage 問題
- ✅ AdminUsers.vue 編譯錯誤
- ✅ 軟刪除帳號登入問題
- ✅ AdminDashboard 載入錯誤

### 技術改進
- 優化事件處理機制 (v-click-outside directive)
- 改進 API 錯誤處理
- 增強表單驗證
- 完善測試帳號管理

---

## 📄 授權

本專案僅供學習使用。

## 開發團隊

軟體工程專案 - 中期作業

---

## 📋 版本歷史

- v0.3.0 (2024-10-26) - 通知系統、任務審批、用戶管理完整實作
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