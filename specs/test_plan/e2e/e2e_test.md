# E2E 測試計畫：寵物領養平台

**版本**: 1.0  
**日期**: 2025-11-30  
**專案**: Pet Adoption Platform  
**測試範圍**: End-to-End Testing Strategy  

## 📋 測試概要

### 目標
驗證寵物領養平台的關鍵使用者流程，確保前後端整合功能正常運作，保障使用者體驗符合業務需求。

### 測試範圍
- **前端**: Vue 3 + Vite (http://localhost:3000)
- **後端**: Flask API (http://localhost:3001) 
- **資料庫**: PostgreSQL (測試環境)
- **檔案儲存**: MinIO/S3 相容儲存

### 測試工具
- **主要框架**: Playwright
- **瀏覽器**: Chrome, Firefox, Safari, Mobile Chrome
- **CI/CD**: GitHub Actions
- **報告**: HTML Report + JUnit XML

## 🎯 測試優先級策略

### P0 - 關鍵路徑 (必須通過，阻擋發布)
1. **使用者瀏覽申請流程**
2. **送養發布流程** 
3. **使用者認證流程**

### P1 - 重要功能 (高優先級)
4. **搜尋與篩選功能**
5. **申請管理功能**
6. **管理員審核流程**

### P2 - 進階功能 (中優先級)
7. **檔案上傳功能**
8. **通知系統**
9. **行動裝置響應式**

## 🏗️ 測試架構設計

### 檔案結構
```
frontend/
├── tests/
│   ├── e2e/
│   │   ├── fixtures/
│   │   │   ├── test-data.ts              # 測試資料
│   │   │   ├── auth-helpers.ts           # 認證輔助
│   │   │   └── mock-files/               # 測試檔案
│   │   │       ├── test-dog.jpg
│   │   │       └── test-cat.jpg
│   │   ├── specs/
│   │   │   ├── critical-paths/           # P0 關鍵流程
│   │   │   │   ├── browse-apply-flow.spec.ts
│   │   │   │   ├── rehome-publish-flow.spec.ts
│   │   │   │   └── user-auth-flow.spec.ts
│   │   │   ├── features/                 # P1 功能測試
│   │   │   │   ├── animal-browsing.spec.ts
│   │   │   │   ├── application-management.spec.ts
│   │   │   │   ├── admin-workflow.spec.ts
│   │   │   │   └── search-filter.spec.ts
│   │   │   └── regression/               # P2 回歸測試
│   │   │       ├── file-upload.spec.ts
│   │   │       ├── notifications.spec.ts
│   │   │       └── mobile-responsive.spec.ts
│   │   ├── page-objects/
│   │   │   ├── BasePage.ts               # 基礎頁面類別
│   │   │   ├── HomePage.ts               # 首頁
│   │   │   ├── AnimalListPage.ts         # 動物列表頁
│   │   │   ├── AnimalDetailPage.ts       # 動物詳情頁
│   │   │   ├── RehomeFormPage.ts         # 送養表單頁
│   │   │   ├── LoginPage.ts              # 登入頁
│   │   │   ├── ApplicationPage.ts        # 申請頁面
│   │   │   └── AdminDashboardPage.ts     # 管理後台
│   │   ├── utils/
│   │   │   ├── api-helpers.ts            # API 輔助函式
│   │   │   ├── db-helpers.ts             # 資料庫操作
│   │   │   ├── file-helpers.ts           # 檔案處理
│   │   │   └── wait-helpers.ts           # 等待輔助
│   │   ├── config/
│   │   │   ├── test-config.ts            # 測試設定
│   │   │   └── environment.ts            # 環境變數
│   │   ├── playwright.config.ts          # Playwright 設定
│   │   ├── global-setup.ts               # 全域設定
│   │   └── global-teardown.ts            # 全域清理
└── package.json
```

## 📝 詳細測試案例

### P0-1: 使用者瀏覽申請流程

**測試目標**: 驗證完整的動物瀏覽到申請流程  
**業務價值**: 核心收益流程，直接影響平台成功率  
**前置條件**: 
- 測試環境已啟動
- 資料庫有測試動物資料
- 電子郵件服務可用

**測試步驟**:
```gherkin
Scenario: 訪客完成動物領養申請流程
  Given 使用者訪問首頁
  When 點擊「瀏覽動物」
  Then 應顯示動物列表頁面
  
  When 點擊第一個動物卡片
  Then 應顯示動物詳情頁面
  And 顯示「我想領養」按鈕
  
  When 點擊「我想領養」按鈕
  Then 應導向登入頁面（因未登入）
  
  When 點擊「註冊新帳號」
  And 填寫有效的註冊資料
  And 提交註冊表單
  Then 應顯示「請檢查電子郵件驗證」訊息
  
  When 進行電子郵件驗證（模擬）
  Then 應自動登入並回到動物詳情頁
  
  When 再次點擊「我想領養」按鈕
  Then 應顯示申請表單
  
  When 填寫完整申請資料
  And 提交申請
  Then 應顯示「申請提交成功」訊息
  And 收到確認電子郵件（模擬）
```

**預期結果**:
- 所有頁面載入時間 < 3 秒
- 表單驗證正確運作
- 成功建立申請記錄
- 使用者收到確認通知

**失敗處理**:
- 截圖儲存失敗畫面
- 記錄 API 錯誤訊息
- 檢查資料庫狀態

### P0-2: 送養發布流程

**測試目標**: 驗證會員可以成功發布動物送養  
**業務價值**: 平台內容產生的核心功能  

**測試步驟**:
```gherkin
Scenario: 會員發布動物送養
  Given 已登入的會員使用者
  When 導航至「發布送養」頁面
  Then 應顯示送養表單
  
  When 填寫動物基本資料
    | 欄位 | 值 |
    | 名稱 | 小白 |
    | 物種 | 狗 |
    | 性別 | 公 |
    | 年齡 | 2歲 |
  And 上傳動物照片
  And 填寫詳細描述
  And 勾選「確認資訊正確」
  And 點擊「提交審核」
  Then 應顯示「送養資訊已提交審核」訊息
  
  When 導航至「我的送養」頁面
  Then 應看到剛發布的動物
  And 狀態顯示為「審核中」
```

**驗證重點**:
- 表單驗證（必填欄位、格式檢查）
- 檔案上傳功能
- 資料持久化
- 狀態流轉正確

### P0-3: 使用者認證流程

**測試目標**: 驗證註冊、登入、登出功能  

**子案例**:
1. **新使用者註冊**
   - 電子郵件驗證流程
   - 密碼安全性檢查
   - 帳號重複檢查

2. **既有使用者登入**
   - 正確憑證登入成功
   - 錯誤憑證顯示錯誤訊息
   - 記住登入狀態

3. **密碼重設**
   - 忘記密碼流程
   - 重設連結有效性
   - 新密碼設定

### P1-4: 搜尋與篩選功能

**測試目標**: 驗證動物搜尋篩選的準確性  

**測試矩陣**:
| 篩選條件 | 測試值 | 預期結果 |
|---------|--------|----------|
| 物種 | 狗 | 只顯示狗類動物 |
| 性別 | 母 | 只顯示母性動物 |
| 年齡範圍 | 1-3歲 | 符合年齡範圍的動物 |
| 關鍵字 | "友善" | 描述包含友善的動物 |
| 複合條件 | 狗+母+友善 | 同時滿足所有條件 |

**測試步驟**:
```typescript
test('複合篩選功能', async ({ page }) => {
  await page.goto('/animals')
  
  // 設定篩選條件
  await page.selectOption('[data-testid="species-filter"]', 'DOG')
  await page.selectOption('[data-testid="gender-filter"]', 'FEMALE')
  await page.fill('[data-testid="keyword-search"]', '友善')
  await page.click('[data-testid="apply-filters"]')
  
  // 驗證結果
  const results = page.getByTestId('animal-card')
  await expect(results).toHaveCountGreaterThan(0)
  
  // 檢查每個結果都符合條件
  const cards = await results.all()
  for (const card of cards) {
    await expect(card.getByText('狗')).toBeVisible()
    await expect(card.getByText('母')).toBeVisible()
  }
})
```

### P1-5: 申請管理功能

**測試目標**: 驗證申請人可以管理自己的申請  

**功能涵蓋**:
- 查看申請列表
- 申請狀態追蹤
- 申請資料修改
- 申請取消功能

### P1-6: 管理員審核流程

**測試目標**: 驗證管理員可以審核送養申請  

**權限測試**:
- 管理員權限驗證
- 審核狀態更新
- 審核備註記錄
- 通知機制觸發

## 🔧 技術實作細節

### Page Object Model 範例

```typescript
// page-objects/AnimalListPage.ts
export class AnimalListPage {
  readonly page: Page
  readonly speciesFilter = '[data-testid="species-filter"]'
  readonly searchInput = '[data-testid="search-input"]'
  readonly animalCards = '[data-testid="animal-card"]'
  readonly applyFiltersBtn = '[data-testid="apply-filters"]'
  
  constructor(page: Page) {
    this.page = page
  }
  
  async goto() {
    await this.page.goto('/animals')
    await this.waitForLoad()
  }
  
  async waitForLoad() {
    await this.page.waitForSelector(this.animalCards)
    await this.page.waitForLoadState('networkidle')
  }
  
  async filterBySpecies(species: string) {
    await this.page.selectOption(this.speciesFilter, species)
    await this.page.click(this.applyFiltersBtn)
    await this.waitForLoad()
  }
  
  async searchByKeyword(keyword: string) {
    await this.page.fill(this.searchInput, keyword)
    await this.page.press(this.searchInput, 'Enter')
    await this.waitForLoad()
  }
  
  async getAnimalCount(): Promise<number> {
    return await this.page.getByTestId('animal-card').count()
  }
  
  async clickAnimalByIndex(index: number) {
    await this.page.click(`${this.animalCards}:nth-child(${index + 1})`)
  }
}
```

### 測試資料管理

```typescript
// fixtures/test-data.ts
export const testUsers = {
  regularMember: {
    email: 'member@test.com',
    password: 'Test123!',
    firstName: '測試',
    lastName: '會員'
  },
  admin: {
    email: 'admin@test.com', 
    password: 'Admin123!',
    role: 'ADMIN'
  }
}

export const testAnimals = {
  publishedDog: {
    name: '小白',
    species: 'DOG',
    gender: 'MALE',
    age: 2,
    description: '友善的小白狗',
    status: 'PUBLISHED'
  },
  draftCat: {
    name: '花花',
    species: 'CAT', 
    gender: 'FEMALE',
    age: 1,
    description: '可愛的小花貓',
    status: 'DRAFT'
  }
}
```

### 環境設定

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  reporter: [
    ['html'],
    ['junit', { outputFile: 'test-results/junit-results.xml' }]
  ],
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  
  projects: [
    // Desktop browsers
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    
    // Mobile devices  
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
    { name: 'mobile-safari', use: { ...devices['iPhone 12'] } }
  ],
  
  webServer: [
    {
      command: 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000
    },
    {
      command: 'cd ../backend && python run.py',
      url: 'http://localhost:3001/health',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000
    }
  ],
  
  globalSetup: require.resolve('./global-setup'),
  globalTeardown: require.resolve('./global-teardown')
})
```

## 📊 測試執行策略

### 本地開發環境
```bash
# 完整測試套件
npm run test:e2e

# 只執行 P0 測試
npm run test:e2e:critical

# 特定瀏覽器測試
npm run test:e2e -- --project=chromium

# 除錯模式
npm run test:e2e:debug

# 產生測試報告
npm run test:e2e:report
```

### CI/CD 整合
```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests
on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  test:
    timeout-minutes: 30
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: pet_adoption_test
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: 18
    
    - name: Install dependencies
      run: npm ci
      
    - name: Install Playwright browsers
      run: npx playwright install --with-deps
      
    - name: Setup test database
      run: |
        cd backend
        python -m pytest --setup-only
        
    - name: Run E2E tests
      run: npm run test:e2e:ci
      
    - uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: playwright-report/
```

### 測試資料管理策略

```typescript
// global-setup.ts
async function globalSetup() {
  // 建立測試資料庫
  await setupTestDatabase()
  
  // 種子測試資料
  await seedTestData()
  
  // 設定測試服務
  await startTestServices()
}

// global-teardown.ts  
async function globalTeardown() {
  // 清理測試資料
  await cleanupTestData()
  
  // 關閉測試服務
  await stopTestServices()
}
```

## 📈 品質指標與監控

### 成功指標
- **測試通過率**: ≥ 98% (P0), ≥ 95% (P1), ≥ 90% (P2)
- **執行時間**: P0 < 5分鐘, 完整套件 < 15分鐘
- **穩定性**: 假陽性率 < 2%

### 監控項目
- 測試執行時間趨勢
- 失敗率統計
- 環境健康度檢查
- 效能基準線監控

### 報告機制
- **即時通知**: P0 失敗立即通知團隊
- **每日報告**: 測試健康度摘要
- **週報**: 趨勢分析和改善建議

## 🚀 部署與維護

### 測試環境需求
- **硬體**: 4 CPU, 8GB RAM, 50GB 儲存空間
- **軟體**: Docker, Node.js 18+, Python 3.9+
- **瀏覽器**: Chrome, Firefox 最新穩定版

### 維護計畫
- **每週**: 檢視失敗測試，更新不穩定案例
- **每月**: 測試案例 Review，清理過時測試
- **每季**: 效能基準線更新，工具版本升級

### 故障排除指南
1. **環境問題**: 檢查服務健康度
2. **資料問題**: 驗證測試資料完整性  
3. **網路問題**: 確認服務間連線
4. **瀏覽器問題**: 更新瀏覽器驅動

## 📋 檢核清單

### 測試實作檢核
- [ ] Page Object Model 實作完成
- [ ] 測試資料 Fixtures 建立
- [ ] 環境設定檔配置
- [ ] CI/CD 管道設定
- [ ] 錯誤處理機制
- [ ] 報告產出機制

### 品質檢核  
- [ ] 所有 P0 測試案例涵蓋
- [ ] 測試資料隔離確保
- [ ] 並行執行無衝突
- [ ] 失敗重試機制
- [ ] 效能基準設定
- [ ] 安全性測試納入

### 文件檢核
- [ ] 測試計畫完整
- [ ] 執行手冊建立  
- [ ] 故障排除指南
- [ ] 維護程序文件
- [ ] 團隊培訓資料

---

**文件版本**: 1.0  
**最後更新**: 2025-11-30  
**負責人**: QA Team  
**審核者**: Tech Lead, Product Manager  
**下次檢視**: 2025-12-15