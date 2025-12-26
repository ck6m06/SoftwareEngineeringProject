# Sequence Diagrams v7

本目錄包含寵物領養平台所有使用案例的PlantUML循序圖。

## 檔案列表

### 1. 動物瀏覽與搜尋 (BP-ANIMAL-001)
- \sequence-animal-list.puml\ - 1.1 動物列表瀏覽
- \sequence-animal-search.puml\ - 1.2 動物搜尋篩選
- \sequence-animal-detail.puml\ - 1.3 動物詳情檢視
- \sequence-application-submit.puml\ - 1.4 領養申請提交

### 2. 送養管理 (BP-REHOME-001)
- \sequence-personal-rehome.puml\ - 2.1 個人送養發佈 (參考v6版本)
- \sequence-my-rehomes.puml\ - 2.2 個人送養管理
- \sequence-shelter-batch-upload.puml\ - 2.3.1 批次匯入
- \sequence-shelter-animals-management.puml\ - 2.4 收容所送養管理

### 3. 申請審核 (BP-APPLICATION-001)
- \sequence-my-applications.puml\ - 申請列表瀏覽 (申請者視角)
- \sequence-application-review.puml\ - 3.1/3.3 申請列表瀏覽與審核作業

### 4. 醫療紀錄 (BP-MEDICAL-001)
- \sequence-medical-record-create.puml\ - 4.1 醫療紀錄新增
- \sequence-medical-record-view.puml\ - 4.2 醫療紀錄檢視

### 5. 系統管理 (BP-SYSTEM-001)
- \sequence-user-management.puml\ - 5.1 使用者管理
- \sequence-data-audit.puml\ - 5.3 資料審核

### 6. 通知中心 (BP-NOTIFICATION-001)
- \sequence-notification-view.puml\ - 6.1 通知瀏覽
- \sequence-notification-management.puml\ - 6.2 通知管理

### 其他
- \sequence-audit-logs.puml\ - 稽核日誌檢視

## 命名規範

循序圖中的參與者命名遵循以下規範:
- **Actor**: 使用中文角色名稱 (如: 一般會員、收容所會員、管理員)
- **Frontend**: Vue檔案名稱 (如: Animals.vue, AnimalDetail.vue)
- **API Client**: TypeScript API檔案 (如: animals.ts, applications.ts)
- **Backend Blueprint**: Python blueprint檔案 (如: animals.py, applications.py)
- **Service Layer**: Python service檔案 (如: animal_service.py, application_service.py)
- **Database**: MySQL
- **Storage**: MinIO

## 技術架構

**前端:**
- Vue 3 + TypeScript
- Vite
- Vue Router
- Pinia (狀態管理)

**後端:**
- Python Flask
- SQLAlchemy (ORM)
- Flask-JWT-Extended (認證)
- Celery (背景任務)

**儲存:**
- MySQL (資料庫)
- MinIO (物件儲存 / S3相容)

## 如何使用

1. 安裝PlantUML或使用線上編輯器
2. 開啟.puml檔案
3. 生成PNG或SVG圖片

**線上工具:**
- http://www.plantuml.com/plantuml/uml/
- https://plantuml-editor.kkeisuke.com/

**VS Code擴充套件:**
- PlantUML extension by jebbs

## 測試說明

### 單元測試
單元測試位於 `code/project/backend/tests/unit/`，主要測試 Service 層的業務邏輯。

```bash
cd code/project/backend

# 執行所有單元測試
pytest tests/unit -v

# 查看單元測試覆蓋率
pytest tests/unit --cov=app.services --cov-report=term
pytest tests/unit --cov=app.services --cov-report=html
```

### 整合測試
整合測試位於 `code/project/backend/tests/integration/`，測試完整的 API 流程（Route → Service → ORM → Database）。

```bash
cd code/project/backend

# 執行所有整合測試
pytest tests/integration -v

# 查看整合測試覆蓋率
pytest tests/integration --cov=app --cov-report=term
pytest tests/integration --cov=app --cov-report=html
```

### 查看合併覆蓋率
```bash
# 執行所有測試並查看總體覆蓋率
pytest tests/ --cov=app --cov-report=term

# 生成 HTML 詳細報告
pytest tests/ --cov=app --cov-report=html

# 查看詳細的未覆蓋行號
pytest tests/ --cov=app --cov-report=term-missing
```

詳細測試文檔：
- 單元測試: `code/project/backend/tests/unit/README.md`
- 整合測試: `code/project/backend/tests/integration/README.md`

## 更新日期

2025-12-24

