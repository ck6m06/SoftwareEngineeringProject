# Phase 5 Test Guide - Notification Center UI

**測試目的**: 驗證通知中心功能的完整性，包括通知鈴鐺、下拉選單、完整頁面以及輪詢機制。

**測試環境**:
- Frontend: http://localhost:5173
- Backend: http://localhost:5000
- PostgreSQL: localhost:5432

**前置條件**:
- 前端和後端服務都已啟動
- date-fns 套件已安裝 (`npm install date-fns`)
- 至少有一個已註冊的用戶帳號
- 資料庫中有測試數據

---

## 測試區塊 A: 通知鈴鐺基礎功能

### A1. 鈴鐺圖示顯示 (未登入狀態)
**目的**: 確認未登入時不顯示通知鈴鐺

**步驟**:
1. 未登入狀態下訪問首頁
2. 檢查導航欄右側

**預期結果**:
- 不顯示通知鈴鐺圖示
- 只顯示 "登入" 和 "註冊" 按鈕

**實際結果**: ___________

---

### A2. 鈴鐺圖示顯示 (已登入狀態)
**目的**: 確認已登入時顯示通知鈴鐺

**步驟**:
1. 以一般會員身份登入
2. 檢查導航欄右側 (在 "我的申請" 和用戶選單之間)

**預期結果**:
- ✅ 顯示鈴鐺圖示 (SVG bell icon)
- ✅ 鈴鐺位置在 "我的申請" 和用戶選單之間
- ✅ 滑鼠懸停時鈴鐺變深色

**實際結果**: ___________

---

### A3. 未讀數量 Badge
**目的**: 確認未讀通知數量正確顯示

**步驟**:
1. 以有未讀通知的用戶身份登入
2. 觀察鈴鐺右上角的紅色 badge

**創建測試通知** (使用管理員或直接插入資料庫):
```sql
-- 為測試用戶創建3個未讀通知
INSERT INTO notifications (recipient_id, actor_id, type, payload, read, created_at)
VALUES
  (1, NULL, 'application_approved', '{"animal_name": "小黑", "application_id": 1}', false, NOW()),
  (1, NULL, 'animal_status_changed', '{"animal_name": "小花", "status": "已領養"}', false, NOW()),
  (1, NULL, 'system_notification', '{"message": "系統維護通知"}', false, NOW());

-- 替換 recipient_id=1 為實際測試用戶 ID
```

**預期結果**:
- ✅ 顯示紅色圓形 badge "3"
- ✅ Badge 定位在鈴鐺右上角
- ✅ 字體白色，背景紅色 (bg-red-600)
- ✅ 如果超過 99 則顯示 "99+"

**實際結果**: ___________

---

## 測試區塊 B: 通知下拉選單

### B1. 打開下拉選單
**目的**: 確認點擊鈴鐺打開下拉選單

**步驟**:
1. 點擊通知鈴鐺圖示
2. 觀察下拉選單出現

**預期結果**:
- ✅ 下拉選單從鈴鐺下方彈出
- ✅ 選單寬度 320px (w-80)
- ✅ 包含標題列 "通知"
- ✅ 如有未讀通知，顯示 "全部已讀" 按鈕
- ✅ 選單有陰影和圓角

**實際結果**: ___________

---

### B2. 下拉選單內容顯示
**目的**: 確認下拉選單正確顯示通知列表

**前置**: 已有 3 個未讀通知 (參考 A3 的 SQL)

**步驟**:
1. 打開通知下拉選單
2. 檢查顯示的通知項目

**預期結果**:
- ✅ 顯示所有未讀通知 (最多顯示最近的通知)
- ✅ 每個通知顯示:
  * 未讀藍色圓點 (h-2 w-2)
  * 通知訊息文字
  * 相對時間 (例如: "3 分鐘前")
  * 刪除按鈕 (X 圖示)
- ✅ 未讀通知背景淺藍色 (bg-blue-50)
- ✅ 底部顯示 "查看所有通知" 連結

**實際結果**: ___________

---

### B3. 標記單個通知為已讀
**目的**: 確認點擊通知可標記為已讀

**步驟**:
1. 打開下拉選單
2. 點擊第一個未讀通知
3. 觀察 badge 數字變化

**預期結果**:
- ✅ 點擊的通知背景變為白色 (bg-blue-50 → bg-white)
- ✅ 藍色圓點變灰色 (bg-blue-600 → bg-gray-300)
- ✅ 鈴鐺 badge 數字減 1 (3 → 2)
- ✅ 下拉選單自動關閉

**驗證 API**:
```bash
# 檢查通知是否標記為已讀
curl -X GET http://localhost:5000/api/notifications \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**實際結果**: ___________

---

### B4. 全部標為已讀
**目的**: 確認 "全部已讀" 按鈕功能

**前置**: 至少 2 個未讀通知

**步驟**:
1. 打開下拉選單
2. 點擊右上角 "全部已讀" 按鈕
3. 觀察變化

**預期結果**:
- ✅ 所有通知圓點變灰色
- ✅ 所有通知背景變白色
- ✅ 鈴鐺 badge 消失 (unreadCount = 0)
- ✅ "全部已讀" 按鈕消失
- ✅ 顯示 "目前沒有通知" 或空列表

**驗證 API**:
```bash
# 檢查所有通知的 read 狀態
curl -X GET http://localhost:5000/api/notifications \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" | jq '.[] | {id: .notification_id, read: .read}'
```

**實際結果**: ___________

---

### B5. 刪除通知
**目的**: 確認刪除按鈕功能

**步驟**:
1. 打開下拉選單
2. 點擊某個通知的刪除按鈕 (X 圖示)
3. 觀察變化

**預期結果**:
- ✅ 該通知從列表中消失
- ✅ 如果刪除未讀通知，badge 數字減 1
- ✅ 列表即時更新
- ✅ 沒有頁面重新載入

**驗證 API**:
```bash
# 確認通知已刪除
curl -X GET http://localhost:5000/api/notifications \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" | jq 'length'
```

**實際結果**: ___________

---

### B6. 點擊外部關閉選單
**目的**: 確認 click-outside 指令功能

**步驟**:
1. 打開通知下拉選單
2. 點擊頁面其他區域 (例如導航欄 logo)

**預期結果**:
- ✅ 下拉選單自動關閉
- ✅ 過渡動畫流暢 (ease-in duration-75)

**實際結果**: ___________

---

### B7. 空狀態顯示
**目的**: 確認沒有通知時的空狀態

**前置**: 刪除所有通知或使用沒有通知的新用戶

**步驟**:
1. 打開下拉選單
2. 觀察空狀態顯示

**預期結果**:
- ✅ 顯示鈴鐺圖示 (SVG 灰色)
- ✅ 顯示文字 "目前沒有通知"
- ✅ 仍然顯示 "查看所有通知" 連結
- ✅ 不顯示 "全部已讀" 按鈕

**實際結果**: ___________

---

## 測試區塊 C: 通知中心完整頁面

### C1. 導航到通知中心
**目的**: 確認可以訪問通知中心頁面

**步驟**:
1. 方式 1: 點擊下拉選單底部的 "查看所有通知"
2. 方式 2: 直接訪問 http://localhost:5173/notifications

**預期結果**:
- ✅ 成功導航到 `/notifications` 路由
- ✅ 未登入用戶自動重定向到登入頁 (requiresAuth: true)
- ✅ 頁面標題顯示 "通知中心"
- ✅ 頁面包含 3 個統計卡片

**實際結果**: ___________

---

### C2. 統計卡片顯示
**目的**: 確認頂部統計卡片正確

**前置**: 有 5 個通知 (3 個未讀, 2 個已讀)

**創建測試數據**:
```sql
INSERT INTO notifications (recipient_id, actor_id, type, payload, read, created_at)
VALUES
  (1, NULL, 'application_submitted', '{"animal_name": "Test1"}', false, NOW()),
  (1, NULL, 'application_approved', '{"animal_name": "Test2"}', false, NOW()),
  (1, NULL, 'application_rejected', '{"animal_name": "Test3"}', false, NOW()),
  (1, NULL, 'rehome_application_received', '{"animal_name": "Test4"}', true, NOW()),
  (1, NULL, 'animal_status_changed', '{"animal_name": "Test5"}', true, NOW());
```

**預期結果**:
- ✅ **全部通知**: 5 (藍色圖示)
- ✅ **未讀通知**: 3 (紅色圖示)
- ✅ **已讀通知**: 2 (綠色圖示)
- ✅ 數字字體大 (text-2xl font-semibold)

**實際結果**: ___________

---

### C3. 篩選標籤切換
**目的**: 確認全部/未讀/已讀標籤功能

**步驟**:
1. 預設顯示 "全部" 標籤 (border-indigo-500)
2. 點擊 "未讀" 標籤
3. 點擊 "已讀" 標籤
4. 點擊 "全部" 標籤

**預期結果**:
- ✅ 每次點擊，對應標籤下方出現藍色底線
- ✅ **全部**: 顯示 5 個通知
- ✅ **未讀**: 只顯示 3 個未讀通知 (左側藍色邊框)
- ✅ **已讀**: 只顯示 2 個已讀通知 (無左側藍色邊框)
- ✅ 標籤文字顯示數量: "全部 (5)", "未讀 (3)", "已讀 (2)"

**實際結果**: ___________

---

### C4. 通知卡片完整顯示
**目的**: 確認通知卡片所有元素正確顯示

**步驟**:
1. 在 "全部" 標籤下觀察第一個未讀通知卡片

**預期結果**:
通知卡片包含:
- ✅ **左側藍色邊框** (border-l-4 border-indigo-600) - 僅未讀
- ✅ **圓形彩色圖示** (h-12 w-12)
  * application_approved: 綠色 (bg-green-500) + 勾選圖示
  * application_rejected: 紅色 (bg-red-500) + X 圖示
  * application_submitted: 藍色 (bg-blue-500) + 文件圖示
- ✅ **通知標題** + "未讀" badge (bg-indigo-100 text-indigo-800)
- ✅ **通知訊息** (詳細內容)
- ✅ **相對時間** (例如: "5 分鐘前")
- ✅ **右側操作按鈕**:
  * 勾選按鈕 (僅未讀通知) - 藍色
  * 刪除按鈕 - 紅色

**實際結果**: ___________

---

### C5. 頁面內標記為已讀
**目的**: 確認頁面內的標記已讀功能

**步驟**:
1. 在 "未讀" 標籤下
2. 點擊某個通知的勾選按鈕 (右上角)

**預期結果**:
- ✅ 該通知的 "未讀" badge 消失
- ✅ 左側藍色邊框消失
- ✅ 統計卡片的 "未讀通知" 數字減 1
- ✅ 統計卡片的 "已讀通知" 數字加 1
- ✅ 通知從 "未讀" 列表移除 (如果在未讀標籤下)
- ✅ 勾選按鈕消失

**實際結果**: ___________

---

### C6. 頁面內全部標為已讀
**目的**: 確認頁面頂部的全部已讀按鈕

**前置**: 至少 2 個未讀通知

**步驟**:
1. 點擊頁面右上角 "全部標為已讀" 按鈕
2. 觀察變化

**預期結果**:
- ✅ 所有通知的 "未讀" badge 消失
- ✅ 所有左側藍色邊框消失
- ✅ "未讀通知" 統計變為 0
- ✅ "已讀通知" 統計增加相應數量
- ✅ "全部標為已讀" 按鈕消失 (unreadCount = 0)
- ✅ 鈴鐺 badge 消失 (如果導航欄可見)

**實際結果**: ___________

---

### C7. 頁面內刪除通知
**目的**: 確認頁面內的刪除功能

**步驟**:
1. 點擊某個通知的刪除按鈕 (垃圾桶圖示)
2. 觀察變化

**預期結果**:
- ✅ 該通知從列表中移除
- ✅ "全部通知" 統計減 1
- ✅ 如果刪除未讀通知, "未讀通知" 統計減 1
- ✅ 如果刪除已讀通知, "已讀通知" 統計減 1
- ✅ 即時更新，無需重新載入

**實際結果**: ___________

---

### C8. 點擊通知卡片
**目的**: 確認點擊通知卡片的交互

**步驟**:
1. 點擊任意未讀通知的卡片主體 (非按鈕區域)

**預期結果**:
- ✅ 通知自動標記為已讀
- ✅ 左側藍色邊框消失
- ✅ "未讀" badge 消失
- ✅ TODO: 根據通知類型導航 (當前未實作)

**實際結果**: ___________

---

### C9. 空狀態 (全部標籤)
**目的**: 確認沒有任何通知時的顯示

**前置**: 刪除所有通知

**步驟**:
1. 在 "全部" 標籤下觀察

**預期結果**:
- ✅ 顯示大型鈴鐺圖示 (h-16 w-16 灰色)
- ✅ 標題: "目前沒有通知"
- ✅ 說明文字: "您目前沒有任何通知"
- ✅ 統計卡片全部顯示 0

**實際結果**: ___________

---

### C10. 空狀態 (未讀標籤)
**目的**: 確認沒有未讀通知時的顯示

**前置**: 全部通知已讀

**步驟**:
1. 點擊 "未讀" 標籤

**預期結果**:
- ✅ 顯示鈴鐺圖示
- ✅ 標題: "目前沒有通知"
- ✅ 說明文字: "所有通知都已讀取"

**實際結果**: ___________

---

## 測試區塊 D: 輪詢機制

### D1. 自動輪詢更新 (下拉選單)
**目的**: 確認未讀數量自動更新

**步驟**:
1. 登入用戶 A 並保持頁面開啟
2. 使用管理員或 SQL 為用戶 A 創建新通知:
```sql
INSERT INTO notifications (recipient_id, type, payload, read, created_at)
VALUES (1, 'system_notification', '{"message": "測試輪詢"}', false, NOW());
```
3. 等待最多 30 秒 (輪詢間隔)
4. 觀察鈴鐺 badge 變化

**預期結果**:
- ✅ 30 秒內 badge 數字自動增加
- ✅ 打開下拉選單可看到新通知
- ✅ 沒有手動刷新頁面

**驗證輪詢**:
打開瀏覽器 DevTools → Network → Filter XHR
應每 30 秒看到請求:
```
GET /api/notifications/unread-count
```

**實際結果**: ___________

---

### D2. 自動輪詢更新 (通知中心頁面)
**目的**: 確認通知中心頁面也啟用輪詢

**步驟**:
1. 在通知中心頁面停留
2. 使用 SQL 創建新通知
3. 等待 30 秒

**預期結果**:
- ✅ 統計卡片自動更新 (未讀數字增加)
- ✅ 如果在 "未讀" 標籤，新通知出現在列表頂部
- ✅ Network 面板顯示定期請求

**實際結果**: ___________

---

### D3. 輪詢停止 (組件卸載)
**目的**: 確認離開頁面時停止輪詢

**步驟**:
1. 打開通知中心頁面
2. 確認 Network 面板有定期請求
3. 導航到其他頁面 (例如首頁)
4. 觀察 Network 面板 2-3 分鐘

**預期結果**:
- ✅ 離開頁面後停止輪詢請求
- ✅ 不再看到 `/api/notifications/unread-count` 請求
- ✅ 避免記憶體洩漏

**實際結果**: ___________

---

## 測試區塊 E: 通知訊息格式化

### E1. 不同通知類型顯示
**目的**: 確認各種通知類型的訊息格式正確

**創建測試數據**:
```sql
INSERT INTO notifications (recipient_id, type, payload, read, created_at)
VALUES
  (1, 'application_submitted', '{"animal_name": "小白", "application_id": 101}', false, NOW()),
  (1, 'application_approved', '{"animal_name": "小黃", "application_id": 102}', false, NOW()),
  (1, 'application_rejected', '{"animal_name": "小灰", "application_id": 103, "reason": "不符合條件"}', false, NOW()),
  (1, 'application_under_review', '{"animal_name": "小橘", "application_id": 104}', false, NOW()),
  (1, 'rehome_application_received', '{"animal_name": "小花", "applicant_name": "張三"}', false, NOW()),
  (1, 'animal_status_changed', '{"animal_name": "小黑", "status": "已領養"}', false, NOW()),
  (1, 'system_notification', '{"message": "系統將於今晚維護"}', false, NOW());
```

**預期訊息格式**:

| 通知類型 | 預期訊息 | 圖示顏色 | 標題 |
|---------|---------|---------|------|
| application_submitted | 您的申請已提交：小白 | 藍色 | 領養申請已提交 |
| application_approved | 您的申請已通過：小黃 | 綠色 | 領養申請已通過 |
| application_rejected | 您的申請未通過：小灰... | 紅色 | 領養申請未通過 |
| application_under_review | 您的申請審核中：小橘 | 黃色 | 領養申請審核中 |
| rehome_application_received | 您的送養動物小花收到申請... | 紫色 | 收到新的領養申請 |
| animal_status_changed | 動物小黑狀態已更新為已領養 | 靛藍色 | 動物狀態更新 |
| system_notification | 系統將於今晚維護 | 灰色 | 系統通知 |

**步驟**:
1. 打開通知中心頁面
2. 逐一檢查每個通知

**實際結果**: ___________

---

### E2. 時間格式化
**目的**: 確認相對時間顯示正確

**步驟**:
1. 創建不同時間的通知:
```sql
-- 剛剛
INSERT INTO notifications (recipient_id, type, payload, read, created_at)
VALUES (1, 'system_notification', '{"message": "剛剛"}', false, NOW());

-- 5 分鐘前
INSERT INTO notifications (recipient_id, type, payload, read, created_at)
VALUES (1, 'system_notification', '{"message": "5分鐘前"}', false, NOW() - INTERVAL '5 minutes');

-- 2 小時前
INSERT INTO notifications (recipient_id, type, payload, read, created_at)
VALUES (1, 'system_notification', '{"message": "2小時前"}', false, NOW() - INTERVAL '2 hours');

-- 1 天前
INSERT INTO notifications (recipient_id, type, payload, read, created_at)
VALUES (1, 'system_notification', '{"message": "1天前"}', false, NOW() - INTERVAL '1 day');
```

2. 查看通知列表

**預期結果**:
- ✅ "不到 1 分鐘前" 或 "幾秒前"
- ✅ "5 分鐘前"
- ✅ "2 小時前"
- ✅ "1 天前"
- ✅ 使用繁體中文 (date-fns zhTW locale)

**實際結果**: ___________

---

## 測試區塊 F: 響應式設計

### F1. 桌面版 (1920x1080)
**目的**: 確認桌面版佈局正常

**步驟**:
1. 瀏覽器視窗設為全螢幕
2. 訪問通知中心頁面

**預期結果**:
- ✅ 最大寬度 1024px (max-w-4xl) 居中
- ✅ 統計卡片 3 欄並排 (grid-cols-3)
- ✅ 通知卡片寬度足夠顯示所有元素
- ✅ 下拉選單不超出視窗

**實際結果**: ___________

---

### F2. 平板版 (768x1024)
**目的**: 確認平板版佈局調整

**步驟**:
1. DevTools → Responsive mode → iPad
2. 訪問通知中心頁面

**預期結果**:
- ✅ 統計卡片仍為 3 欄 (md:grid-cols-3)
- ✅ 卡片內容不擠壓
- ✅ 按鈕觸控區域足夠大

**實際結果**: ___________

---

### F3. 手機版 (375x667)
**目的**: 確認手機版佈局調整

**步驟**:
1. DevTools → Responsive mode → iPhone SE
2. 訪問通知中心頁面

**預期結果**:
- ✅ 統計卡片變為 1 欄 (grid-cols-1)
- ✅ 通知卡片圖示和文字自動換行
- ✅ 操作按鈕保持可點擊
- ✅ 下拉選單寬度自適應 (可能需要調整)

**實際結果**: ___________

---

## 測試區塊 G: 效能與邊界情況

### G1. 大量通知載入 (100+)
**目的**: 測試大量通知的效能

**創建測試數據**:
```sql
-- 批量插入 100 個通知
INSERT INTO notifications (recipient_id, type, payload, read, created_at)
SELECT 
  1,
  (ARRAY['application_submitted', 'application_approved', 'system_notification'])[floor(random() * 3 + 1)],
  '{"animal_name": "Test"}',
  random() > 0.5,
  NOW() - (random() * INTERVAL '30 days')
FROM generate_series(1, 100);
```

**步驟**:
1. 訪問通知中心頁面
2. 測量載入時間
3. 滾動列表

**預期結果**:
- ✅ 頁面載入時間 < 2 秒
- ✅ 滾動流暢 (60 FPS)
- ✅ 統計數字正確 (全部/未讀/已讀)
- ✅ 瀏覽器不凍結

**TODO**: 實作分頁或虛擬滾動 (若列表超過 50 項)

**實際結果**: ___________

---

### G2. 極長通知訊息
**目的**: 測試長文字處理

**創建測試數據**:
```sql
INSERT INTO notifications (recipient_id, type, payload, read, created_at)
VALUES (1, 'system_notification', '{
  "message": "這是一個非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常長的通知訊息用來測試文字是否正確換行以及是否有 CSS overflow 的問題"
}', false, NOW());
```

**預期結果**:
- ✅ 文字自動換行 (不會超出卡片)
- ✅ 卡片高度自動調整
- ✅ 不影響其他通知顯示

**實際結果**: ___________

---

### G3. 網路錯誤處理
**目的**: 測試 API 錯誤處理

**步驟**:
1. 打開通知中心頁面
2. DevTools → Network → Offline
3. 嘗試標記通知為已讀或刪除

**預期結果**:
- ✅ 顯示錯誤訊息 (console.error)
- ✅ 不會白屏或崩潰
- ✅ 重新連線後可恢復功能

**TODO**: 實作用戶友善的錯誤提示 (Toast notification)

**實際結果**: ___________

---

## 測試區塊 H: 整合測試

### H1. 完整用戶流程
**情境**: 用戶提交領養申請並收到通知

**步驟**:
1. 用戶 A 登入並提交領養申請
2. 管理員審核並通過申請
3. 用戶 A 檢查通知

**預期流程**:
1. ✅ 提交申請後，收容所收到 `rehome_application_received` 通知
2. ✅ 審核後，用戶 A 收到 `application_approved` 通知
3. ✅ 鈴鐺 badge 顯示 "1"
4. ✅ 打開下拉選單看到綠色勾選圖示
5. ✅ 點擊通知可跳轉到申請詳情頁 (TODO)
6. ✅ 通知自動標記為已讀

**實際結果**: ___________

---

### H2. 多裝置同步
**情境**: 同一用戶在多個瀏覽器登入

**步驟**:
1. Chrome: 用戶 A 登入
2. Firefox: 用戶 A 登入
3. Chrome: 標記一個通知為已讀
4. Firefox: 等待 30 秒觀察

**預期結果**:
- ✅ Firefox 的 badge 數字自動減少 (輪詢同步)
- ✅ Firefox 列表中該通知變為已讀狀態

**限制**: 不是即時同步 (最多延遲 30 秒)

**實際結果**: ___________

---

## 測試總結

### 通過的測試 (✅)
- [ ] A1-A3: 鈴鐺顯示與 badge
- [ ] B1-B7: 下拉選單功能
- [ ] C1-C10: 通知中心頁面
- [ ] D1-D3: 輪詢機制
- [ ] E1-E2: 訊息格式化
- [ ] F1-F3: 響應式設計
- [ ] G1-G3: 效能與邊界
- [ ] H1-H2: 整合測試

### 失敗的測試 (❌)
列出失敗的測試編號和原因：

---

### 發現的問題
1. 
2. 
3. 

---

### 需要改進的功能
1. **點擊通知跳轉**: 根據 notification.type 跳轉到相應頁面
   - application_approved → /my/applications/:id
   - rehome_application_received → /my-rehomes
   
2. **分頁功能**: 當通知超過 50 個時實作分頁

3. **錯誤提示**: 使用 Toast 顯示 API 錯誤

4. **Loading 骨架屏**: 初次載入時顯示骨架屏動畫

5. **通知音效**: 收到新通知時播放提示音 (可選)

---

## 附錄: API 端點參考

```bash
# 獲取所有通知
GET /api/notifications
Headers: Authorization: Bearer <token>
Query: ?read=false (僅未讀)

# 獲取未讀數量
GET /api/notifications/unread-count
Headers: Authorization: Bearer <token>

# 標記單個通知為已讀
PUT /api/notifications/{notification_id}/read
Headers: Authorization: Bearer <token>

# 標記全部為已讀
PUT /api/notifications/mark-all-read
Headers: Authorization: Bearer <token>

# 刪除通知
DELETE /api/notifications/{notification_id}
Headers: Authorization: Bearer <token>
```

---

**測試完成日期**: ___________  
**測試人員**: ___________  
**測試環境版本**: 
- Node.js: ___________
- PostgreSQL: ___________
- Browser: ___________
