# 草稿儲存功能修復說明

## 問題描述
在「我的送養」頁面點擊「儲存草稿」按鈕時,草稿只儲存到瀏覽器的 localStorage,並沒有呼叫後端 API 將草稿儲存到資料庫。

## 修復內容

### 修改的文件
\rontend/src/pages/RehomeForm.vue\

### 修改的函數

#### 1. saveDraft() 函數 (第 393-452 行)

**修改前:**
- 只將表單資料儲存到 localStorage
- 不呼叫任何 API

**修改後:**
- 新增基本驗證 (檢查名稱和物種必填)
- 呼叫 \createAnimal()\ API 創建新草稿到資料庫
- 如果是編輯模式,呼叫 \updateAnimal()\ 更新現有草稿
- 儲存返回的 animal_id,以便後續更新而不是重複創建
- 同時儲存到 localStorage 作為備份
- 顯示適當的成功訊息

#### 2. loadDraft() 函數 (第 454-471 行)

**修改前:**
- 只從 localStorage 載入表單資料

**修改後:**
- 檢查草稿中是否有 animalId
- 如果有 animalId,設定為編輯模式
- 載入所有表單資料和狀態

## 測試方法

### 手動測試步驟

1. **登入系統**
   - 使用測試帳號登入: test@example.com / Test123

2. **開啟送養表單**
   - 訪問: http://localhost:5173/rehome-form

3. **填寫基本資訊**
   - 名稱: 測試草稿動物
   - 物種: 選擇「狗」或「貓」
   - 其他資訊可選填

4. **點擊「儲存草稿」按鈕**
   - 應該看到 "草稿已儲存到資料庫" 的提示
   - 瀏覽器 Console 可以看到 API 請求

5. **驗證草稿已儲存**
   - 前往「我的送養」頁面: http://localhost:5173/my-rehomes
   - 點擊「草稿」篩選
   - 應該可以看到剛才儲存的草稿

6. **再次編輯草稿**
   - 重新開啟送養表單頁面
   - 修改一些資訊
   - 再次點擊「儲存草稿」
   - 應該看到 "草稿已更新" 的提示
   - 驗證不會創建重複的草稿記錄

### API 測試

\\\powershell
# 1. 登入
\ = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method POST -ContentType "application/json" -Body '{\"email\":\"test@example.com\",\"password\":\"Test123\"}'

# 2. 創建草稿
\ = '{\"name\":\"測試草稿\",\"species\":\"DOG\",\"description\":\"測試描述\",\"status\":\"DRAFT\"}'
\@{notifications=System.Object[]; page=1; pages=1; per_page=20; total=1} = Invoke-RestMethod -Uri "http://localhost:5000/api/animals" -Method POST -Headers @{Authorization=\"Bearer \\"; \"Content-Type\"=\"application/json\"} -Body \

Write-Host \"草稿 ID: \\"

# 3. 查詢草稿列表
\ = Invoke-RestMethod -Uri "http://localhost:5000/api/animals?owner_id=\&status=DRAFT" -Method GET -Headers @{Authorization=\"Bearer \\"}

Write-Host \"草稿數量: \\"
\\\

## 功能特點

1. ✅ **資料庫持久化**: 草稿儲存到後端資料庫,不會因為清除瀏覽器快取而遺失
2. ✅ **避免重複創建**: 第一次儲存後記住 ID,後續更新而不是創建新記錄
3. ✅ **雙重保險**: 同時儲存到 localStorage 作為備份
4. ✅ **編輯模式支援**: 可以載入並繼續編輯已儲存的草稿
5. ✅ **基本驗證**: 確保至少填寫名稱和物種才能儲存

## 相關文件

- 後端 API: \ackend/app/blueprints/animals.py\ (第 118-154 行)
- 前端 API: \rontend/src/api/animals.ts\
- 我的送養頁面: \rontend/src/pages/MyRehomes.vue\

## 已知限制

1. 照片尚未上傳時儲存草稿,照片資訊會存在 localStorage 但不會上傳到伺服器
2. 需要填寫名稱和物種才能儲存草稿 (最小必要資訊)

## 後續改進建議

1. 考慮增加自動儲存功能 (每隔一段時間自動儲存)
2. 顯示草稿最後儲存時間
3. 支援多個草稿版本管理
4. 增加草稿儲存狀態指示器 (儲存中/已儲存/儲存失敗)
