# 系統問題與解決方案

**建立時間:** 2025-10-26 18:26:02

---

## 問題 1: 註冊時沒有寄驗證信到信箱

### 現況
- ✅ **已實作**: 驗證郵件發送功能 (email_service.py)
- ⚠️ **狀態**: 目前僅記錄日誌，未實際發送郵件
- 📝 **原因**: 開發環境未配置郵件服務器 (SendGrid/AWS SES)

### 解決方案
**選項 A: 開發環境 - 查看日誌中的驗證連結**
- 註冊後查看 backend Docker 日誌
- 找到驗證 token 並手動構建連結
- 指令: `docker logs pet-adoption-backend | Select-String "EMAIL VERIFICATION"`

**選項 B: 生產環境 - 整合郵件服務**
1. 註冊 SendGrid 或 AWS SES
2. 配置 SMTP 設定到 .env
3. 修改 email_service.py 實際發送郵件

**選項 C: 開發便利 - 自動驗證**
- 註冊後自動設置 verified=True
- 跳過郵件驗證流程

### 建議
開發階段使用**選項 C**最方便，生產環境必須使用**選項 B**。

---

## 問題 2: 已審核通過領養的動物應該不能重複領養

### 需求分析
- 當申請狀態為 APPROVED 時，該動物應標記為已領養
- 已領養動物不應再接受新申請
- 需要顯示「已被領養」狀態

### 實作計畫
1. **後端修改**:
   - 當申請被批准時，更新動物狀態為 ADOPTED
   - 添加 ADOPTED 狀態到 AnimalStatus enum
   - 阻止對已領養動物的新申請

2. **前端修改**:
   - 顯示「已被領養」標籤
   - 隱藏「我想領養」按鈕
   - 在動物列表中過濾已領養動物(可選)

---

## 問題 3: 通知頁面無法正常使用

### 需要檢查
1. 通知 API 是否正常回應
2. 前端是否正確處理通知資料
3. 通知生成是否正常觸發

### 測試步驟
1. 訪問 /notifications 頁面
2. 檢查瀏覽器 Console 錯誤
3. 檢查 Network 面板 API 回應
4. 回報具體錯誤訊息

---

## 問題 4: 刊登送養資訊草稿沒有正確儲存

### 需要確認
1. RehomeForm 是否有儲存草稿功能
2. 草稿是否提交到後端
3. 後端是否正確儲存 DRAFT 狀態

### 檢查項目
- 表單提交時的 status 參數
- 後端 animals API 的草稿處理
- 「儲存草稿」按鈕是否存在且運作

---

## 問題 5: 如何建立管理員與收容所帳號

### 現有測試帳號
```
管理員帳號:
- Email: admin@test.com
- Password: Admin123
- Role: ADMIN

收容所帳號:
- Email: shelter@test.com  
- Password: Shelter123
- Role: SHELTER_MEMBER

一般用戶:
- Email: user@test.com
- Password: User123
- Role: GENERAL_MEMBER
```

### 建立新帳號方法

**方法 A: 直接操作資料庫**
```sql
-- 建立管理員
UPDATE users 
SET role = 'ADMIN' 
WHERE email = 'your-email@example.com';

-- 建立收容所帳號
UPDATE users 
SET role = 'SHELTER_MEMBER' 
WHERE email = 'shelter-email@example.com';
```

**方法 B: 透過後端 API (需管理員權限)**
- 建立管理員專用的用戶管理 API
- 允許管理員修改用戶角色

**方法 C: 註冊時選擇角色 (不建議)**
- 安全性問題: 任何人都可註冊為管理員
- 需要額外的審核機制

### 建議實作
建立「超級管理員工具」:
1. 管理員登入後可訪問 /admin/users
2. 提供「變更用戶角色」功能
3. 需要記錄審計日誌

---

## 立即可執行的修復

### 修復 1: 註冊自動驗證 (開發環境)
位置: `backend/app/blueprints/auth.py`
修改註冊邏輯，新用戶自動驗證。

### 修復 2: 添加 ADOPTED 狀態
1. 修改 AnimalStatus enum
2. 申請批准時更新動物狀態
3. 前端顯示「已被領養」

### 修復 3: 管理員工具
建立用戶角色管理頁面。

---

**需要更多資訊的問題:**
- 問題 3: 需要具體錯誤訊息
- 問題 4: 需要確認草稿功能的預期行為

