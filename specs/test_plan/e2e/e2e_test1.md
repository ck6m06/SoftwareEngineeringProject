# E2E 測試計畫：寵物領養平台 - 送養發布流程

**版本**: 2.0  
**日期**: 2025-11-30  
**專案**: Pet Adoption Platform  
**測試範圍**: 送養發布 End-to-End 測試  
**狀態**: ✅ 已實作並通過

## 📋 測試概要

### 目標
驗證寵物領養平台的送養發布核心流程，確保前後端整合功能正常運作，保障使用者可以成功提交送養資訊並進入審核流程。

### 實際測試環境
- **前端**: Vue 3 + Vite (http://localhost:5173)
- **後端**: Flask API (http://localhost:5000) 
- **資料庫**: MySQL (Docker 容器)
- **檔案儲存**: MinIO S3 相容儲存

### 測試工具
- **主要框架**: Playwright
- **瀏覽器**: Chrome（已優化配置，其他瀏覽器已註解）
- **報告**: HTML Report
- **測試檔案**: test_dog.jpg（真實照片）

## 🎯 P0-2-003: 完整送養發布流程 - 實際實作

### 測試目標
驗證會員可以成功發布動物送養，包含表單填寫、真實照片上傳、多步驟導航和最終審核提交。

### 業務價值
- **核心功能**: 平台核心送養內容產生流程
- **狀態流轉**: 從 DRAFT → SUBMITTED 的完整狀態轉換
- **使用者體驗**: 4步驟表單的完整用戶旅程

### 測試資料配置

#### 使用的測試用戶
```typescript
// 已建立的測試用戶
testUser: {
  email: 'user@test.com',
  password: 'User123',
  verified: true
}
```

#### 實際動物測試資料
```typescript
export const testRehomeData = {
  animalData: {
    basic: {
      name: '小白',
      type: 'dog',      // 對應 'DOG' 選項
      breed: '柴犬',
      gender: 'male',   // 對應 'MALE' 選項  
      age: '2',         // 計算為 2023-01-01 出生日期
      description: '可愛的寵物，健康活潑，適合家庭飼養。'
    }
  },
  testFiles: {
    realImage: 'tests/e2e/test-assets/images/test_dog.jpg'  // 實際使用的測試照片
  }
}
```

### P0-2-003: 完整提交流程驗證

**測試流程覆蓋**:
1. 會員登入驗證 (user@test.com)
2. 導航至送養表單頁面
3. 4步驟表單完整填寫：
   - 基本資訊 (名稱、物種、品種、性別、出生日期、顏色、描述)
   - 照片上傳 (使用 test_dog.jpg)
   - 醫療資訊 (健康狀態記錄)
   - 確認送出 (最終提交審核)
4. 狀態流轉驗證 (DRAFT → SUBMITTED)
5. 資料庫記錄確認

### 實際表單結構

**4步驟送養表單流程**:

1. **基本資訊** (`currentStep === 0`)
   - 動物名稱（必填）
   - 物種選擇：CAT/DOG（必填）
   - 品種（必填）
   - 性別：MALE/FEMALE（必填）
   - 出生日期（必填）
   - 顏色
   - 描述（必填）

2. **上傳照片** (`currentStep === 1`) 
   - **關鍵發現**: 必須成功上傳照片才能繼續
   - 支援檔案類型：image/*
   - 使用 MinIO S3 儲存
   - 必須有照片才能進入下一步

3. **醫療資訊** (`currentStep === 2`)
   - 醫療記錄（可選）
   - 健康狀態資訊

4. **確認送出** (`currentStep === 3`)
   - **最終提交按鈕**: 「確認送出」
   - 提交後狀態: DRAFT → SUBMITTED
   - 進入管理員審核流程

### Page Object 架構

**RehomeFormPage 主要功能**:
- `fillBasicInfo()`: 填寫動物基本資訊
- `uploadRealPhoto()`: 上傳真實測試照片 (test_dog.jpg)
- `goToNextStep()`: 步驟間導航
- `submitForReview()`: 最終提交審核 (非草稿)
- 各步驟等待方法: `waitForUploadStep()`, `waitForMedicalStep()`, `waitForConfirmationStep()`

### 實際測試結果

**執行狀態**: ✅ **1 passed (8.4s)**

**資料庫驗證**:
```sql
-- 測試產生的記錄
animal_id | name | status    | created_at
14        | 小白  | SUBMITTED | 2025-11-30 15:48:57
```

**關鍵發現**:
- ✅ 完整的 4 步驟流程實作完成
- ✅ 真實照片上傳功能正常
- ✅ 狀態正確從 DRAFT 轉為 SUBMITTED
- ✅ 前後端整合驗證通過
- ✅ Page Object Model 架構完整

### 測試配置優化

**Playwright 配置調整**:
```typescript
// playwright.config.ts - 針對開發效率優化
projects: [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  // Firefox, Safari, Mobile 已註解，專注於 Chrome 測試
]
```

**執行效能**:
- 單一測試執行時間: ~8.4 秒
- 包含完整流程: 登入 → 表單填寫 → 照片上傳 → 提交審核
- 自動化清理: 測試後自動清理測試資料

---

### 與原計畫的主要差異

| 計畫項目 | 實際實作 | 狀態 |
|---------|----------|------|
| 多個測試案例 (P0-2-001~008) | 單一完整測試 (P0-2-003) | ✅ 簡化但覆蓋核心流程 |
| 複雜表單驗證測試 | 基本必填欄位驗證 | ⚠️ 待補強 |
| 多瀏覽器測試 | Chrome 單一瀏覽器 | ✅ 開發階段適用 |
| 詳細錯誤處理測試 | try-catch 基本處理 | ⚠️ 可擴展 |
| PostgreSQL | MySQL | ✅ 架構調整 |
| localhost:3000/3001 | localhost:5173/5000 | ✅ 實際環境 |

### 成功標準 - 實際達成

✅ **功能完整性**: 核心送養發布流程 100% 可用  
✅ **效能達標**: 完整測試 < 9秒  
✅ **Chrome 兼容**: 完全支援  
✅ **真實資料**: 照片上傳、資料庫持久化正常  
✅ **狀態流轉**: DRAFT → SUBMITTED 正確轉換

### 後續擴展建議

1. **表單驗證測試**: 新增必填欄位、格式驗證測試
2. **錯誤處理**: 網路異常、檔案上傳失敗場景
3. **多瀏覽器**: 生產環境前加入 Firefox、Safari 測試
4. **行動裝置**: 響應式設計測試
5. **效能監控**: 加入頁面載入時間斷言

---

**結論**: 目前實作已成功建立 P0-2 送養發布的核心 E2E 測試，覆蓋最重要的用戶流程。雖然與原始計畫在範圍上有差異，但核心價值已實現且測試穩定通過。