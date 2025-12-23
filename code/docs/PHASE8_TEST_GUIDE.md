# Phase 8 測試指南 - Medical Records (醫療記錄)

**測試日期**: 2025-10-26  
**測試目的**: 驗證醫療記錄管理功能的完整性，包括 CRUD 操作、驗證流程、角色權限控制。  
**前置條件**: Phase 1-7 測試通過

---

## 📋 測試環境確認

**前端**: http://localhost:5173/ (Vite dev server)  
**後端**: http://localhost:5000/ (Flask API)  
**資料庫**: MySQL 8.0 (Docker on port 3307)

**測試帳號**:
- **管理員**: admin@test.com / Admin123 (可驗證醫療記錄)
- **收容所會員**: 需自行建立或使用現有帳號
- **一般會員**: 無權限訪問醫療記錄頁面

**測試資料**:
- **動物**: 小白 (ID: 10, DOG, 柴犬)
- **醫療記錄**: 4 筆已建立 (VACCINE, CHECKUP, TREATMENT, SURGERY)

---

## 測試區塊 A: API 端點測試

### A1. 建立醫療記錄

**目的**: 確認後端 API 可正確建立醫療記錄

**步驟**:
```powershell
# 1. 登入取得 token
$loginBody = @{email="admin@test.com"; password="Admin123"} | ConvertTo-Json
$loginResponse = Invoke-WebRequest -Uri "http://localhost:5000/api/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
$token = ($loginResponse.Content | ConvertFrom-Json).access_token

# 2. 建立醫療記錄
$recordBody = @{
    record_type="CHECKUP"
    date="2024-10-26"
    provider="測試動物醫院"
    details="年度健康檢查"
} | ConvertTo-Json
$headers = @{Authorization="Bearer $token"}
Invoke-WebRequest -Uri "http://localhost:5000/api/medical-records/animals/10/medical-records" -Method POST -Body $recordBody -ContentType "application/json; charset=utf-8" -Headers $headers
```

**預期結果**:
- ✅ HTTP 201 Created
- ✅ 回應包含 `record` 物件
- ✅ `verified` = false (預設未驗證)

**實際結果**: ___________

---

### A2. 取得醫療記錄列表

**步驟**:
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/medical-records/animals/10/medical-records" -Method GET -Headers $headers
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

**預期結果**:
- ✅ HTTP 200 OK
- ✅ 記錄按日期降序排列
- ✅ 包含所有欄位

**實際結果**: ___________

---

## 測試區塊 B: 前端 UI 測試

### B1. 頁面訪問與權限

**步驟**:
1. 未登入訪問 `/medical-records`
2. 一般會員登入後訪問
3. 管理員登入後訪問

**預期結果**:
- ✅ 未登入: 重定向到登入頁
- ✅ 一般會員: 無權限
- ✅ 管理員/收容所會員: 成功訪問

**實際結果**: ___________

---

### B2. 動物選擇器

**預期結果**:
- ✅ 下拉選單顯示所有動物
- ✅ 物種標籤正確 (🐕 狗, 🐱 貓)
- ✅ 空狀態提示

**實際結果**: ___________

---

### B3. 醫療記錄時間軸

**預期結果**:
記錄卡片顯示:
- ✅ 日期 (YYYY-MM-DD)
- ✅ 類型 Badge (顏色正確)
  * VACCINE - 綠色
  * CHECKUP - 藍色  
  * TREATMENT - 紅色
  * SURGERY - 橙色
  * OTHER - 灰色
- ✅ 提供者
- ✅ 詳細說明
- ✅ 驗證狀態
- ✅ 操作按鈕

**實際結果**: ___________

---

### B4. 新增醫療記錄

**步驟**:
1. 點擊 "新增醫療記錄"
2. 填寫表單
3. 提交

**預期結果**:
- ✅ Modal 正確顯示
- ✅ 表單驗證正常
- ✅ 提交成功後記錄出現

**實際結果**: ___________

---

### B5. 編輯醫療記錄

**預期結果**:
- ✅ Modal 預填現有資料
- ✅ 可修改所有欄位
- ✅ 更新即時反映

**實際結果**: ___________

---

### B6. 驗證醫療記錄 (ADMIN)

**步驟**:
1. 以 ADMIN 登入
2. 點擊驗證按鈕
3. 確認對話框

**預期結果**:
- ✅ 對話框正確
- ✅ 驗證後顯示 "已驗證" 標籤
- ✅ SHELTER_MEMBER 看不到驗證按鈕

**實際結果**: ___________

---

## 測試區塊 C: 記錄類型測試

### C1. 5 種記錄類型顯示

**預期結果**:
| 類型 | 顏色 | 標籤 |
|------|------|------|
| VACCINE | 綠 | 疫苗接種 |
| CHECKUP | 藍 | 健康檢查 |
| TREATMENT | 紅 | 治療 |
| SURGERY | 橙 | 手術 |
| OTHER | 灰 | 其他 |

**實際結果**: ___________

---

## 測試區塊 D: 空狀態與錯誤

### D1. 未選擇動物

**預期結果**:
- ✅ 提示: "請選擇一個動物"
- ✅ 新增按鈕禁用

**實際結果**: ___________

---

### D2. 動物無記錄

**預期結果**:
- ✅ 空狀態圖示
- ✅ 提示: "此動物尚無醫療記錄"

**實際結果**: ___________

---

## 測試區塊 E: 響應式設計

### E1-E3. 桌面/平板/手機

**預期結果**:
- ✅ 桌面: 佈局良好
- ✅ 平板: 自適應
- ✅ 手機: 垂直排列，觸控友善

**實際結果**: ___________

---

## 測試區塊 F: 整合測試

### F1. 完整 CRUD 流程

**步驟**:
1. 建立新動物
2. 新增 3 筆醫療記錄
3. 編輯第 1 筆
4. ADMIN 驗證第 1 筆
5. 確認所有操作正確

**實際結果**: ___________

---

## 測試總結

### 通過的測試 (✅)
- [ ] A1-A2: API 測試
- [ ] B1-B6: UI 測試
- [ ] C1: 記錄類型
- [ ] D1-D2: 空狀態
- [ ] E1-E3: 響應式
- [ ] F1: 整合測試

### 失敗的測試 (❌)
列出問題:

---

### 需要改進

**優先級 HIGH**:
1. ✅ API 路徑已修正
2. 錯誤提示 Toast

**優先級 MEDIUM**:
3. 附件上傳整合
4. 匯出 PDF 功能
5. 搜尋/篩選

**優先級 LOW**:
6. 分頁 (30+ 筆)
7. 從動物詳情頁快速訪問
8. 統計圖表

---

## 附錄: API 參考

```bash
# 建立
POST /api/medical-records/animals/{animal_id}/medical-records

# 列表
GET /api/medical-records/animals/{animal_id}/medical-records

# 更新
PATCH /api/medical-records/{record_id}

# 驗證
POST /api/medical-records/{record_id}/verify
```

---

**測試完成日期**: ___________  
**測試人員**: ___________
