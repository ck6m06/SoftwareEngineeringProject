# Phase 7 測試指南 - 申請審核管理

## 目標
測試申請審核頁面 (ApplicationReview.vue) 的所有功能，包括篩選、分配、審核、樂觀鎖定和權限控制。

## 前置準備

### 1. 啟動服務
```bash
# Backend (Terminal 1)
cd backend
python app.py

# Frontend (Terminal 2)
cd frontend
npm run dev
```

### 2. 準備測試數據
```sql
-- 創建測試用戶
INSERT INTO users (username, email, password_hash, role, email_verified) VALUES
('admin_user', 'admin@example.com', '$2b$12$...', 'ADMIN', TRUE),
('shelter_staff', 'shelter@example.com', '$2b$12$...', 'SHELTER_MEMBER', TRUE),
('applicant_1', 'applicant1@example.com', '$2b$12$...', 'USER', TRUE),
('applicant_2', 'applicant2@example.com', '$2b$12$...', 'USER', TRUE);

-- 創建測試動物
INSERT INTO animals (name, species, breed, age, sex, shelter_id, status) VALUES
('Bella', 'DOG', '黃金獵犬', 3, 'FEMALE', 1, 'AVAILABLE'),
('Max', 'DOG', '拉布拉多', 2, 'MALE', 1, 'AVAILABLE'),
('Luna', 'CAT', '英國短毛貓', 1, 'FEMALE', 1, 'AVAILABLE'),
('Charlie', 'CAT', '波斯貓', 4, 'MALE', 1, 'AVAILABLE');

-- 創建測試申請（不同狀態）
INSERT INTO applications (applicant_id, animal_id, type, status, submitted_at) VALUES
-- 待審核
(3, 1, 'ADOPTION', 'PENDING', NOW() - INTERVAL '1 day'),
(4, 2, 'ADOPTION', 'PENDING', NOW() - INTERVAL '2 days'),
(3, 3, 'ADOPTION', 'PENDING', NOW() - INTERVAL '3 hours'),
-- 審核中
(4, 4, 'ADOPTION', 'UNDER_REVIEW', NOW() - INTERVAL '12 hours'),
-- 已通過
(3, 1, 'ADOPTION', 'APPROVED', NOW() - INTERVAL '5 days'),
-- 已拒絕
(4, 2, 'ADOPTION', 'REJECTED', NOW() - INTERVAL '7 days');

-- 為審核中的申請指派審核者
UPDATE applications 
SET assignee_id = 2, 
    reviewed_at = NOW() - INTERVAL '6 hours',
    review_notes = '正在審核中'
WHERE status = 'UNDER_REVIEW';
```

### 3. 獲取測試 Token
```bash
# Admin 登入
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Shelter Staff 登入
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"shelter@example.com","password":"shelter123"}'

# 普通用戶登入（測試權限拒絕）
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"applicant1@example.com","password":"user123"}'
```

---

## 測試區塊 A: 頁面訪問與權限控制

### A1: ADMIN 可以訪問
**步驟:**
1. 使用 admin@example.com 登入
2. 訪問 `/admin/applications`

**預期結果:**
- ✅ 成功進入申請審核頁面
- ✅ 顯示完整的統計卡片（4個）
- ✅ 顯示篩選標籤（5個）

### A2: SHELTER_MEMBER 可以訪問
**步驟:**
1. 使用 shelter@example.com 登入
2. 訪問 `/admin/applications`

**預期結果:**
- ✅ 成功進入申請審核頁面
- ✅ 可以看到所有申請數據

### A3: 普通用戶無法訪問
**步驟:**
1. 使用 applicant1@example.com 登入
2. 嘗試訪問 `/admin/applications`

**預期結果:**
- ✅ 被重定向到首頁
- ✅ 或顯示 403 權限錯誤

### A4: 未登入用戶重定向
**步驟:**
1. 登出所有帳號
2. 直接訪問 `/admin/applications`

**預期結果:**
- ✅ 重定向到登入頁面
- ✅ 登入後會回到 `/admin/applications`

---

## 測試區塊 B: 統計卡片顯示

### B1: 統計數據正確
**步驟:**
1. 以 admin 身份登入
2. 檢查四個統計卡片

**預期結果:**
```
待審核: 3 (黃色圖標)
審核中: 1 (藍色圖標)
已通過: 1 (綠色圖標)
已拒絕: 1 (紅色圖標)
```

### B2: 統計卡片樣式正確
**步驟:**
1. 檢查卡片顏色配置

**預期結果:**
- ✅ 待審核: 黃底黃字圖標
- ✅ 審核中: 藍底藍字圖標
- ✅ 已通過: 綠底綠字圖標
- ✅ 已拒絕: 紅底紅字圖標

### B3: 數量更新動態
**步驟:**
1. 通過一個待審核申請
2. 觀察統計卡片變化

**預期結果:**
- ✅ 待審核: 3 → 2
- ✅ 已通過: 1 → 2

---

## 測試區塊 C: 篩選標籤功能

### C1: 顯示所有申請
**步驟:**
1. 點擊「全部」標籤

**預期結果:**
- ✅ 顯示 6 個申請（所有狀態）
- ✅ 標籤計數顯示 "全部 (6)"
- ✅ 標籤為活躍狀態（藍色底線）

### C2: 篩選待審核
**步驟:**
1. 點擊「待審核」標籤

**預期結果:**
- ✅ 只顯示 3 個 PENDING 申請
- ✅ 標籤計數顯示 "待審核 (3)"
- ✅ 所有卡片的狀態徽章為黃色

### C3: 篩選審核中
**步驟:**
1. 點擊「審核中」標籤

**預期結果:**
- ✅ 只顯示 1 個 UNDER_REVIEW 申請
- ✅ 標籤計數顯示 "審核中 (1)"
- ✅ 卡片顯示審核者資訊

### C4: 篩選已通過
**步驟:**
1. 點擊「已通過」標籤

**預期結果:**
- ✅ 只顯示 1 個 APPROVED 申請
- ✅ 標籤計數顯示 "已通過 (1)"
- ✅ 狀態徽章為綠色

### C5: 篩選已拒絕
**步驟:**
1. 點擊「已拒絕」標籤

**預期結果:**
- ✅ 只顯示 1 個 REJECTED 申請
- ✅ 標籤計數顯示 "已拒絕 (1)"
- ✅ 狀態徽章為紅色

### C6: 標籤切換重置分頁
**步驟:**
1. 切換到第 2 頁（如果有）
2. 點擊其他標籤

**預期結果:**
- ✅ 分頁回到第 1 頁
- ✅ 顯示新篩選的結果

---

## 測試區塊 D: 申請卡片顯示

### D1: 卡片基本資訊
**步驟:**
1. 查看申請列表中的卡片

**預期結果 (每個卡片應包含):**
- ✅ 申請人頭像圖標
- ✅ 申請人姓名/Email
- ✅ 申請時間（相對時間，如 "1 天前"）
- ✅ 狀態徽章
- ✅ 動物照片（或占位圖）
- ✅ 動物名稱
- ✅ 動物品種、年齡資訊

### D2: 顯示審核者資訊
**步驟:**
1. 查看 UNDER_REVIEW 狀態的申請

**預期結果:**
- ✅ 顯示「審核者: shelter_staff」
- ✅ 有審核者圖標

### D3: 顯示審核備註
**步驟:**
1. 查看已審核的申請

**預期結果:**
- ✅ 顯示「審核備註: 正在審核中」
- ✅ 淺灰色背景區塊

### D4: 動物圖片顯示
**測試 A: 有圖片**
```sql
UPDATE animals SET images = '[{"url":"https://example.com/dog.jpg"}]'::jsonb
WHERE animal_id = 1;
```
**預期結果:**
- ✅ 顯示動物照片
- ✅ 圓角樣式

**測試 B: 無圖片**
**預期結果:**
- ✅ 顯示占位圖標（灰色相機圖標）

---

## 測試區塊 E: 操作按鈕功能

### E1: 查看詳情按鈕
**步驟:**
1. 點擊任意申請的「查看詳情」按鈕

**預期結果:**
- ✅ 跳轉到 `/applications/{id}` 頁面
- ✅ 如果該頁面不存在，顯示 404（正常）

### E2: 分配審核者按鈕
**可見性測試:**
**步驟:**
1. 查看 PENDING 申請

**預期結果:**
- ✅ 顯示「分配審核者」按鈕（藍色）

**步驟:**
2. 查看 APPROVED/REJECTED 申請

**預期結果:**
- ✅ 不顯示「分配審核者」按鈕

### E3: 通過/拒絕按鈕
**可見性測試:**
**步驟:**
1. 查看 PENDING 或 UNDER_REVIEW 申請

**預期結果:**
- ✅ 顯示「通過」按鈕（綠色）
- ✅ 顯示「拒絕」按鈕（紅色）

**步驟:**
2. 查看 APPROVED/REJECTED 申請

**預期結果:**
- ✅ 不顯示「通過」和「拒絕」按鈕

---

## 測試區塊 F: 分配審核者 Modal

### F1: 打開 Modal
**步驟:**
1. 點擊「分配審核者」按鈕

**預期結果:**
- ✅ Modal 彈出
- ✅ 顯示標題「分配審核者」
- ✅ 顯示下拉選單

### F2: 選擇審核者
**步驟:**
1. 打開下拉選單
2. 選擇 shelter_staff

**預期結果:**
- ✅ 下拉選單顯示可用審核者列表
- ✅ 顯示格式: "username (ROLE)"
- ✅ 選擇後「確認分配」按鈕啟用

### F3: 執行分配
**步驟:**
1. 選擇審核者
2. 點擊「確認分配」

**預期結果:**
- ✅ 按鈕變為「處理中...」
- ✅ 顯示成功提示「分配成功！」
- ✅ Modal 關閉
- ✅ 列表自動重新載入
- ✅ 該申請顯示審核者資訊

**API 驗證:**
```bash
curl -X PATCH http://localhost:5000/api/applications/1/assign \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assignee_id": 2}'
```
**預期結果:**
- ✅ 200 OK
- ✅ 返回更新後的申請資料

### F4: 取消分配
**步驟:**
1. 打開 Modal
2. 點擊「取消」或點擊 Modal 外部

**預期結果:**
- ✅ Modal 關閉
- ✅ 沒有發送 API 請求
- ✅ 列表狀態不變

### F5: 分配錯誤處理
**步驟:**
1. 關閉 backend
2. 嘗試分配審核者

**預期結果:**
- ✅ 顯示錯誤提示「分配失敗: Network Error」
- ✅ Modal 保持打開
- ✅ 可以重試

---

## 測試區塊 G: 審核申請 Modal

### G1: 打開通過 Modal
**步驟:**
1. 點擊「通過」按鈕

**預期結果:**
- ✅ Modal 彈出
- ✅ 標題顯示「通過申請」
- ✅ 顯示申請人和動物摘要
- ✅ 文字輸入框（審核備註）
- ✅ 確認按鈕為綠色

### G2: 打開拒絕 Modal
**步驟:**
1. 點擊「拒絕」按鈕

**預期結果:**
- ✅ Modal 彈出
- ✅ 標題顯示「拒絕申請」
- ✅ 確認按鈕為紅色

### G3: 通過申請（無備註）
**步驟:**
1. 點擊「通過」
2. 不填寫備註
3. 點擊「確認通過」

**預期結果:**
- ✅ 按鈕變為「處理中...」
- ✅ 提示「申請通過成功！」
- ✅ Modal 關閉
- ✅ 列表重新載入
- ✅ 該申請移到「已通過」

**API 驗證:**
```bash
curl -X POST http://localhost:5000/api/applications/1/review \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "review_notes": "",
    "version": 1
  }'
```
**預期結果:**
- ✅ 200 OK
- ✅ status: "APPROVED"
- ✅ reviewed_at: 當前時間
- ✅ version: 2

### G4: 拒絕申請（附備註）
**步驟:**
1. 點擊「拒絕」
2. 填寫拒絕原因: "申請人條件不符"
3. 點擊「確認拒絕」

**預期結果:**
- ✅ 提示「申請拒絕成功！」
- ✅ 該申請移到「已拒絕」
- ✅ 顯示審核備註

**API 驗證:**
```bash
curl -X POST http://localhost:5000/api/applications/1/review \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reject",
    "review_notes": "申請人條件不符",
    "version": 1
  }'
```
**預期結果:**
- ✅ 200 OK
- ✅ status: "REJECTED"
- ✅ review_notes: "申請人條件不符"

### G5: 取消審核
**步驟:**
1. 打開審核 Modal
2. 填寫備註
3. 點擊「取消」

**預期結果:**
- ✅ Modal 關閉
- ✅ 沒有發送 API 請求
- ✅ 列表狀態不變

---

## 測試區塊 H: 樂觀鎖定（版本衝突）

### H1: 模擬版本衝突
**準備:**
```sql
-- 查看當前版本
SELECT application_id, version FROM applications WHERE application_id = 1;
-- version = 1
```

**步驟:**
1. Admin A 打開申請 1 的審核 Modal
2. 在另一個瀏覽器，Admin B 先通過申請 1（version 1 → 2）
3. Admin A 點擊「確認通過」（version 仍為 1）

**預期結果:**
- ✅ API 返回 409 Conflict
- ✅ 前端顯示提示:「申請已被其他人修改，請重新載入頁面」
- ✅ Modal 保持打開
- ✅ 列表自動重新載入
- ✅ 顯示最新狀態（已通過）

**API 測試:**
```bash
# 第一次審核（成功）
curl -X POST http://localhost:5000/api/applications/1/review \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "approve", "version": 1}'
# 返回: 200 OK, version: 2

# 第二次審核（衝突）
curl -X POST http://localhost:5000/api/applications/1/review \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "reject", "version": 1}'
# 返回: 409 Conflict
```

**預期響應:**
```json
{
  "error": "Conflict",
  "message": "Application has been modified by another user",
  "current_version": 2
}
```

### H2: 重新載入後再審核
**步驟:**
1. 遇到版本衝突後
2. 點擊確認重新載入
3. 重新打開該申請
4. 執行審核

**預期結果:**
- ✅ 使用最新 version
- ✅ 審核成功

---

## 測試區塊 I: 分頁功能

### I1: 顯示分頁控制
**準備:**
```sql
-- 新增超過 10 筆申請
INSERT INTO applications (applicant_id, animal_id, type, status, submitted_at)
SELECT 
  3 + (n % 2), 
  1 + (n % 4),
  'ADOPTION',
  'PENDING',
  NOW() - (n || ' hours')::INTERVAL
FROM generate_series(1, 15) AS n;
```

**步驟:**
1. 切換到「待審核」標籤

**預期結果:**
- ✅ 顯示 10 個申請
- ✅ 顯示分頁控制（上一頁、下一頁）
- ✅ 顯示「第 1 頁，共 2 頁」

### I2: 切換頁面
**步驟:**
1. 點擊「下一頁」

**預期結果:**
- ✅ 顯示第 2 頁的申請（剩餘 5 個）
- ✅ 「上一頁」按鈕啟用
- ✅ 「下一頁」按鈕禁用

### I3: 回到第一頁
**步驟:**
1. 在第 2 頁點擊「上一頁」

**預期結果:**
- ✅ 回到第 1 頁
- ✅ 「上一頁」按鈕禁用

---

## 測試區塊 J: Loading 狀態

### J1: 初始載入
**步驟:**
1. 刷新頁面

**預期結果:**
- ✅ 顯示 Loading 動畫（旋轉圖標）
- ✅ 顯示「載入中...」文字
- ✅ 載入完成後顯示申請列表

### J2: 篩選時載入
**步驟:**
1. 切換標籤

**預期結果:**
- ✅ 短暫顯示 Loading 狀態
- ✅ 顯示新篩選結果

### J3: 審核時載入
**步驟:**
1. 點擊「確認通過」

**預期結果:**
- ✅ 按鈕文字變為「處理中...」
- ✅ 按鈕禁用
- ✅ 完成後恢復

---

## 測試區塊 K: 空狀態顯示

### K1: 無待審核申請
**準備:**
```sql
UPDATE applications SET status = 'APPROVED' WHERE status = 'PENDING';
```

**步驟:**
1. 切換到「待審核」標籤

**預期結果:**
- ✅ 顯示空狀態圖標（文件圖標）
- ✅ 顯示文字:「目前沒有待審核的申請」
- ✅ 顯示說明:「當有新的申請時，將會顯示在這裡」

### K2: 無任何申請
**準備:**
```sql
DELETE FROM applications;
```

**步驟:**
1. 切換到「全部」標籤

**預期結果:**
- ✅ 顯示空狀態
- ✅ 統計卡片全為 0

---

## 測試區塊 L: 響應式設計

### L1: 桌面版佈局
**步驟:**
1. 在桌面瀏覽器（>1024px）查看

**預期結果:**
- ✅ 統計卡片為 4 列網格
- ✅ 操作按鈕水平排列
- ✅ Modal 寬度適中（500px）

### L2: 平板版佈局
**步驟:**
1. 調整瀏覽器寬度為 768px

**預期結果:**
- ✅ 統計卡片為 2 列網格
- ✅ 操作按鈕仍水平排列

### L3: 手機版佈局
**步驟:**
1. 調整瀏覽器寬度為 375px

**預期結果:**
- ✅ 統計卡片為 1 列
- ✅ 操作按鈕垂直堆疊（全寬）
- ✅ 動物圖片全寬顯示
- ✅ 篩選標籤可橫向滾動

---

## 測試區塊 M: 整合測試

### M1: 完整審核流程
**步驟:**
1. 用戶提交領養申請
2. Admin 進入審核頁面
3. 看到新申請（待審核）
4. 分配給 shelter_staff 審核
5. Shelter staff 登入
6. 查看已分配的申請
7. 審核通過並填寫備註
8. 用戶收到通知

**預期結果:**
- ✅ 每一步都成功執行
- ✅ 狀態正確更新
- ✅ 通知正確發送

### M2: 拒絕後重新申請
**步驟:**
1. Admin 拒絕申請
2. 用戶重新提交申請（同一動物）
3. Admin 再次審核

**預期結果:**
- ✅ 可以創建新申請
- ✅ 每個申請獨立 version
- ✅ 不會互相干擾

### M3: 多人同時審核
**步驟:**
1. 開啟 3 個瀏覽器
2. 同時登入 3 個 admin
3. 分別審核不同申請

**預期結果:**
- ✅ 互不影響
- ✅ 統計數據實時更新
- ✅ 沒有衝突

---

## 測試區塊 N: 錯誤處理

### N1: 網路錯誤
**步驟:**
1. 關閉 backend
2. 嘗試載入申請列表

**預期結果:**
- ✅ 顯示錯誤提示
- ✅ 不會白屏或崩潰

### N2: 權限錯誤
**步驟:**
1. Token 過期
2. 嘗試審核申請

**預期結果:**
- ✅ 返回 401 Unauthorized
- ✅ 重定向到登入頁面

### N3: 無效申請 ID
**步驟:**
1. 手動修改 URL 訪問不存在的申請

**預期結果:**
- ✅ 顯示 404 錯誤
- ✅ 或自動返回列表

---

## 測試區塊 O: 性能測試

### O1: 大量申請載入
**準備:**
```sql
-- 生成 100 筆申請
INSERT INTO applications (applicant_id, animal_id, type, status, submitted_at)
SELECT 
  3 + (n % 10), 
  1 + (n % 20),
  'ADOPTION',
  CASE (n % 4)
    WHEN 0 THEN 'PENDING'
    WHEN 1 THEN 'UNDER_REVIEW'
    WHEN 2 THEN 'APPROVED'
    ELSE 'REJECTED'
  END,
  NOW() - (n || ' hours')::INTERVAL
FROM generate_series(1, 100) AS n;
```

**步驟:**
1. 載入申請列表
2. 切換標籤

**預期結果:**
- ✅ 載入時間 < 2 秒
- ✅ 切換標籤流暢
- ✅ 分頁正常工作

### O2: 動畫性能
**步驟:**
1. 打開 Chrome DevTools Performance
2. 錄製切換標籤的操作

**預期結果:**
- ✅ FPS > 30
- ✅ 無明顯卡頓

---

## 測試區塊 P: 瀏覽器兼容性

### P1: Chrome
**預期結果:** ✅ 所有功能正常

### P2: Firefox
**預期結果:** ✅ 所有功能正常

### P3: Safari
**預期結果:** ✅ 所有功能正常

### P4: Edge
**預期結果:** ✅ 所有功能正常

---

## 測試總結

### 測試覆蓋率目標
- [x] 功能測試: 100%
- [x] 權限控制: 100%
- [x] 樂觀鎖定: 100%
- [x] 錯誤處理: 100%
- [x] 響應式設計: 100%

### 已知問題
- [ ] 審核者列表目前為硬編碼，需要從 API 獲取
- [ ] 申請詳情頁面 (`/applications/:id`) 尚未實現

### 後續改進
1. 新增批次審核功能（一次審核多個）
2. 新增審核歷史記錄
3. 新增審核統計圖表
4. 新增郵件通知開關
5. 新增導出申請報表功能

---

## 快速驗證清單

**基本功能 (5分鐘)**
- [ ] 頁面可訪問
- [ ] 統計數據正確
- [ ] 篩選功能正常
- [ ] 申請卡片顯示完整

**審核流程 (10分鐘)**
- [ ] 可以分配審核者
- [ ] 可以通過申請
- [ ] 可以拒絕申請
- [ ] 狀態正確更新

**進階功能 (10分鐘)**
- [ ] 版本衝突處理正常
- [ ] 權限控制有效
- [ ] 分頁功能正常
- [ ] 響應式佈局適配

**總測試時間: ~25 分鐘**

---

**測試完成後，Application Review UI 功能應該 100% 可用！** 🎉
