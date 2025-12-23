# PHASE 9 測試指南 - Jobs 任務狀態

**測試日期**: 2025-10-26  
**測試範圍**: Jobs (背景任務) 模組  
**預計時間**: 30 分鐘

---

## 📋 測試概述

本階段測試 Jobs (背景任務狀態管理) 功能,包含:
- ✅ 任務列表查詢與篩選
- ✅ 任務狀態監控
- ✅ 任務操作 (Retry/Cancel)
- ✅ 自動刷新機制
- ✅ 角色權限控制

---

## 🔧 前置準備

### 1. 確認服務運行
\\\powershell
# 檢查後端
curl http://localhost:5000/health

# 檢查前端
# 瀏覽器訪問 http://localhost:5173
\\\

### 2. 準備測試帳號
| 角色 | Email | 密碼 | 權限 |
|------|-------|------|------|
| ADMIN | admin@test.com | Admin123 | 查看所有任務 |
| SHELTER_MEMBER | shelter@test.com | Shelter123 | 查看自己的任務 |
| GENERAL_MEMBER | (任意一般用戶) | - | ❌ 無權限 |

### 3. 建立測試任務數據
\\\powershell
# 登入取得 token
$loginResp = Invoke-RestMethod -Uri 'http://localhost:5000/api/auth/login' -Method POST -Body '{\"email\":\"admin@test.com\",\"password\":\"Admin123\"}' -ContentType 'application/json'
$token = $loginResp.access_token

# 建立測試任務 (批次匯入動物)
$headers = @{Authorization=\"Bearer $token\"}
Invoke-RestMethod -Uri 'http://localhost:5000/api/shelters/1/animals/batch' -Method POST -Headers $headers -Body '{\"file_url\":\"test.csv\"}' -ContentType 'application/json'
\\\

---

## ✅ 測試案例

### Test 1: 訪問任務狀態頁面

#### 步驟:
1. 使用 **admin@test.com** 登入
2. 點擊導航欄「管理後台」
3. 在 AdminDashboard 點擊「📊 任務狀態」按鈕
4. 或直接訪問: http://localhost:5173/jobs

#### 預期結果:
- ✅ 成功進入任務狀態頁面
- ✅ 顯示標題「任務狀態」
- ✅ 顯示 5 個狀態 Tab (全部、待處理、執行中、成功、失敗)
- ✅ 顯示任務列表或「暫無任務」提示

---

### Test 2: 任務列表查詢 (ADMIN)

#### 步驟:
1. 以 ADMIN 身份登入並進入 /jobs
2. 觀察任務列表內容
3. 點擊不同狀態 Tab 切換

#### 預期結果:
- ✅ 顯示所有用戶的任務 (ADMIN 可見全部)
- ✅ 任務卡片包含:
  - 任務類型 (animal_batch_import 等)
  - 狀態標記 (顏色對應: 待處理-灰/執行中-藍/成功-綠/失敗-紅)
  - 建立時間、開始時間、完成時間
  - 建立者 (user_id)
  - 結果摘要 (如有)
- ✅ Tab 切換正確篩選任務狀態

#### API 驗證:
\\\powershell
# 查詢所有任務
Invoke-RestMethod -Uri 'http://localhost:5000/api/jobs' -Headers $headers

# 查詢特定狀態
Invoke-RestMethod -Uri 'http://localhost:5000/api/jobs?status=SUCCEEDED' -Headers $headers
\\\

---

### Test 3: 任務列表查詢 (SHELTER_MEMBER)

#### 步驟:
1. 登出 ADMIN
2. 使用 **shelter@test.com** 登入
3. 進入 /jobs 頁面
4. 觀察任務列表

#### 預期結果:
- ✅ 只顯示自己建立的任務
- ✅ 看不到其他用戶的任務
- ✅ 任務數量可能較少或為空

#### API 驗證:
\\\powershell
# SHELTER_MEMBER 登入
$shelterResp = Invoke-RestMethod -Uri 'http://localhost:5000/api/auth/login' -Method POST -Body '{\"email\":\"shelter@test.com\",\"password\":\"Shelter123\"}' -ContentType 'application/json'
$shelterToken = $shelterResp.access_token
$shelterHeaders = @{Authorization=\"Bearer $shelterToken\"}

# 查詢任務 (應只回傳自己的)
Invoke-RestMethod -Uri 'http://localhost:5000/api/jobs' -Headers $shelterHeaders
\\\

---

### Test 4: 任務狀態自動刷新

#### 步驟:
1. 進入 /jobs 頁面
2. 觀察右上角「最後更新」時間
3. 等待 5 秒
4. 觀察時間是否更新

#### 預期結果:
- ✅ 頁面每 5 秒自動刷新任務列表
- ✅ 「最後更新」時間戳持續更新
- ✅ 執行中任務的進度條可能更新
- ✅ 無需手動重新整理

#### 程式碼檢查:
\\\	ypescript
// frontend/src/pages/Jobs.vue
// 應包含 setInterval 每 5000ms 呼叫 fetchJobs()
\\\

---

### Test 5: 任務詳情展開

#### 步驟:
1. 在任務列表中找到任一任務卡片
2. 檢查卡片顯示的資訊完整性
3. 若有 result_summary,檢查是否正確顯示

#### 預期結果:
- ✅ 任務類型正確顯示中文名稱:
  - \nimal_batch_import\  動物批次匯入
  - \data_export\  資料匯出
  - \ccount_deletion_request\  帳號刪除申請
- ✅ 時間戳格式正確 (YYYY-MM-DD HH:mm:ss)
- ✅ 狀態顏色正確:
  - PENDING (待處理) - 灰色
  - RUNNING (執行中) - 藍色
  - SUCCEEDED (成功) - 綠色
  - FAILED (失敗) - 紅色
  - CANCELLED (已取消) - 黃色

---

### Test 6: 重試失敗任務 (Retry)

#### 步驟:
1. 在任務列表中找到狀態為「失敗」的任務
2. 點擊「重試」按鈕
3. 觀察狀態變化

#### 預期結果:
- ✅ 只有失敗任務顯示「重試」按鈕
- ✅ 點擊後顯示「重試中...」
- ✅ 任務狀態更新為 PENDING
- ✅ 顯示成功訊息
- ✅ 任務會被 worker 重新執行 (若 worker 運行中)

#### API 驗證:
\\\powershell
# 重試任務 (替換 JOB_ID)
Invoke-RestMethod -Uri 'http://localhost:5000/api/jobs/1/retry' -Method POST -Headers $headers
\\\

#### 預期回應:
\\\json
{
  \"message\": \"任務已重新排入隊列\",
  \"job\": {
    \"job_id\": 1,
    \"status\": \"PENDING\",
    \"retry_count\": 1
  }
}
\\\

---

### Test 7: 取消任務 (Cancel)

#### 步驟:
1. 建立新任務 (如批次匯入)
2. 在任務為 PENDING 或 RUNNING 時
3. 點擊「取消」按鈕
4. 確認取消操作

#### 預期結果:
- ✅ 只有 PENDING/RUNNING 任務顯示「取消」按鈕
- ✅ 點擊後顯示確認對話框
- ✅ 確認後任務狀態更新為 CANCELLED
- ✅ 顯示成功訊息

#### API 驗證:
\\\powershell
# 取消任務
Invoke-RestMethod -Uri 'http://localhost:5000/api/jobs/2/cancel' -Method POST -Headers $headers
\\\

---

### Test 8: 權限控制測試

#### 步驟:
1. 使用一般會員帳號登入 (GENERAL_MEMBER)
2. 嘗試訪問 http://localhost:5173/jobs
3. 或在導航欄檢查是否有「任務狀態」連結

#### 預期結果:
- ✅ 一般會員無法訪問 /jobs
- ✅ 強制訪問會被重定向到首頁
- ✅ AdminDashboard 不顯示「任務狀態」按鈕

#### 路由配置檢查:
\\\	ypescript
// frontend/src/router/index.ts
{
  path: '/jobs',
  meta: { requiresRole: ['ADMIN', 'SHELTER_MEMBER'] }
}
\\\

---

### Test 9: 分頁測試 (若任務數 > 20)

#### 步驟:
1. 建立超過 20 個任務
2. 觀察頁面底部是否顯示分頁控制
3. 點擊下一頁

#### 預期結果:
- ✅ 每頁顯示最多 20 個任務
- ✅ 顯示分頁控制 (若總數 > 20)
- ✅ 切換頁碼正確載入新數據
- ✅ 顯示「第 X 頁,共 Y 頁」

---

### Test 10: 錯誤處理測試

#### 測試場景:
1. **後端服務停止**:
   - 停止 Flask 後端
   - 刷新 /jobs 頁面
   - 預期: 顯示錯誤訊息「無法載入任務列表」

2. **無效 Token**:
   - 清除 localStorage token
   - 刷新頁面
   - 預期: 重定向到登入頁

3. **無效任務 ID**:
   \\\powershell
   # 查詢不存在的任務
   Invoke-RestMethod -Uri 'http://localhost:5000/api/jobs/99999' -Headers $headers
   \\\
   - 預期: 404 錯誤

---

## 📊 測試結果記錄

| 測試案例 | 狀態 | 備註 |
|---------|------|------|
| Test 1: 訪問頁面 | ⬜ |  |
| Test 2: 查詢 (ADMIN) | ⬜ |  |
| Test 3: 查詢 (SHELTER) | ⬜ |  |
| Test 4: 自動刷新 | ⬜ |  |
| Test 5: 任務詳情 | ⬜ |  |
| Test 6: 重試任務 | ⬜ |  |
| Test 7: 取消任務 | ⬜ |  |
| Test 8: 權限控制 | ⬜ |  |
| Test 9: 分頁 | ⬜ |  |
| Test 10: 錯誤處理 | ⬜ |  |

**測試狀態**: ✅ 通過 | ❌ 失敗 | ⚠️ 部分通過 | ⬜ 未測試

---

## 🐛 已知問題

1. **Celery Worker 未實作**:
   - 任務會卡在 PENDING 狀態
   - Retry 後不會實際執行
   - 需實作 backend/app/tasks/ 目錄下的 worker

2. **進度追蹤**:
   - 目前執行中任務顯示固定 50% 進度
   - 實際進度需 worker 回報

---

## 🔄 與其他模組整合測試

### 與 Medical Records 整合:
- 醫療記錄批次匯入應建立 Job
- 在 Jobs 頁面可查看匯入狀態

### 與 Shelters 整合:
- 收容所動物批次匯入應建立 Job
- SHELTER_MEMBER 可查看自己收容所的匯入任務

### 與 Notifications 整合:
- 任務完成/失敗應發送通知 (待實作)

---

## 📝 測試完成檢查清單

- [ ] 所有 10 個測試案例已執行
- [ ] ADMIN 和 SHELTER_MEMBER 權限測試通過
- [ ] 自動刷新機制正常運作
- [ ] 任務狀態顯示正確
- [ ] Retry/Cancel 功能正常
- [ ] 錯誤處理機制完善
- [ ] UI 響應式設計在不同螢幕正常顯示

---

## 🚀 下一步

1. **實作 Celery Worker** (PHASE9b):
   - 實作動物批次匯入 worker
   - 實作資料匯出 worker
   - 測試任務實際執行

2. **增強功能**:
   - 任務詳情展開/摺疊
   - 匯出任務列表為 CSV
   - 任務執行日誌查看

3. **整合測試**:
   - 測試完整的批次匯入流程
   - 測試任務失敗重試機制
   - 測試高並發任務排程

---

**測試完成時間**: ___________  
**測試人員**: ___________  
**測試環境**: Windows / macOS / Linux  
**瀏覽器**: Chrome / Firefox / Safari  
**測試結論**: ✅ 通過 / ❌ 失敗 / ⚠️ 需改進
