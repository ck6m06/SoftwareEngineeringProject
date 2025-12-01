# E2E 測試框架

這是寵物送養平台的 End-to-End (E2E) 測試框架，使用 Playwright 實現。

## 目錄結構

```
tests/e2e/
├── specs/                      # 測試規格
│   └── critical-paths/          # 關鍵路徑測試
│       └── rehome-publishing.spec.ts
├── page-objects/               # 頁面物件模型
│   ├── RehomeFormPage.ts
│   ├── LoginPage.ts
│   └── NavigationPage.ts
├── fixtures/                   # 測試固件
│   ├── rehome-test-data.ts     # 送養測試資料
│   └── auth-helpers.ts         # 認證助手
├── utils/                      # 工具函數
│   └── test-helpers.ts
├── config/                     # 配置檔案
│   ├── global-setup.ts         # 全域設置
│   └── global-teardown.ts      # 全域清理
├── test-assets/                # 測試檔案
│   ├── images/                 # 測試圖片
│   └── documents/              # 測試文件
└── README.md                   # 說明文件
```

## 測試策略

### P0-2 送養發布流程測試覆蓋

1. **P0-2-001**: 完整送養發布流程 - 快樂路徑
2. **P0-2-002**: 表單驗證測試
3. **P0-2-003**: 大檔案上傳測試
4. **P0-2-004**: 網路錯誤處理
5. **P0-2-005**: 草稿儲存功能
6. **P0-2-006**: 行動裝置響應式測試

## 執行測試

### 環境配置

#### 本地開發環境
```bash
# 設定環境變數 (可選，使用預設值)
export FRONTEND_URL=http://localhost:5173
export BACKEND_URL=http://localhost:5000

# 或建立 .env 檔案
cp .env.example .env
```

#### GCP 部署環境測試
```bash
# 設定 GCP 環境變數
export FRONTEND_URL=https://your-frontend-app.appspot.com
export BACKEND_URL=https://your-backend-api.appspot.com

# 或編輯 .env 檔案
FRONTEND_URL=https://your-frontend-app.appspot.com
BACKEND_URL=https://your-backend-api.appspot.com
```

#### 混合環境 (前端在 GCP，後端在本地)
```bash
export FRONTEND_URL=https://your-frontend-app.appspot.com
export BACKEND_URL=http://localhost:5000
```

### 前置要求

1. 確保前端服務可在配置的 URL 存取
2. 確保後端 API 服務可在配置的 URL 存取  
3. 確保測試資料庫已配置 (如果使用完整後端)

### 執行指令

```bash
# 執行所有 E2E 測試
npm run test:e2e

# 執行特定測試檔案
npx playwright test rehome-publishing.spec.ts

# 執行特定瀏覽器的測試
npx playwright test --project=chromium

# 開啟 UI 模式執行測試
npx playwright test --ui

# 執行測試並產生報告
npx playwright test --reporter=html
```

### 除錯模式

```bash
# 使用 headed 模式執行測試
npx playwright test --headed

# 逐步執行測試
npx playwright test --debug

# 執行測試記錄器
npx playwright codegen http://localhost:5173
```

## 測試設計模式

### Page Object Model (POM)

我們使用 Page Object Model 模式來組織測試程式碼：

- `RehomeFormPage`: 送養表單頁面的互動方法
- `LoginPage`: 登入頁面的互動方法
- `NavigationPage`: 導航元素的互動方法

### 測試固件 (Fixtures)

- `rehome-test-data.ts`: 包含所有送養相關的測試資料
- `auth-helpers.ts`: 提供認證相關的輔助函數

### 工具函數

- `test-helpers.ts`: 通用的測試輔助功能，如 API 等待、截圖等

## 測試環境管理

### 全域設置 (Global Setup)

在測試執行前自動執行：
- 檢查服務狀態
- 初始化測試資料庫
- 創建測試用戶
- 準備測試檔案

### 全域清理 (Global Teardown)

在測試執行後自動執行：
- 清理測試資料
- 清理上傳的檔案
- 重置資料庫（可選）
- 生成測試報告

## 測試資料管理

### 測試用戶

- **一般會員**: `test.user@example.com` / `TestPassword123!`
- **管理員**: `admin@test.com` / `Admin123!`

### 測試檔案

- `test-assets/images/`: 包含測試用圖片檔案
- `test-assets/documents/`: 包含測試用文件檔案

## 測試報告

### HTML 報告

執行測試後，HTML 報告會生成在 `test-results/html/index.html`

### JUnit 報告

JUnit XML 報告會生成在 `test-results/junit-results.xml`，用於 CI/CD 整合

## 最佳實踐

### 1. 測試隔離

- 每個測試開始前確保乾淨的狀態
- 使用 `beforeEach` 進行測試前設置
- 避免測試間的相依性

### 2. 等待策略

- 使用 Playwright 的內建等待機制
- 等待 API 響應完成
- 等待元素狀態變化

### 3. 錯誤處理

- 截圖失敗的測試
- 記錄網路活動
- 提供有意義的錯誤訊息

### 4. 維護性

- 使用 Page Object Model
- 將測試資料外部化
- 重用通用的測試邏輯

## 故障排除

### 常見問題

1. **服務未運行**: 確保前後端服務都在運行
2. **元素找不到**: 檢查 `data-testid` 是否正確設定
3. **超時問題**: 增加適當的等待時間
4. **檔案上傳失敗**: 檢查測試檔案是否存在

### 除錯技巧

- 使用 `page.pause()` 暫停執行
- 啟用 `--headed` 模式觀察測試執行
- 檢查瀏覽器開發者工具
- 查看 Playwright trace 檔案

## CI/CD 整合

### GitHub Actions 範例

```yaml
- name: Run E2E tests
  run: |
    npm ci
    npm run test:e2e
  env:
    CI: true
```

### 環境變數

- `CI=true`: 啟用 CI 模式設定
- `RESET_TEST_DB=true`: 測試後重置資料庫
- `NODE_ENV=test`: 設定測試環境