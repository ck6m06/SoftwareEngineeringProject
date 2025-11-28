# 快速生成測試帳號指南

## 📋 概述

本腳本可以快速生成專案所需的測試帳號，包括管理員、收容所會員和一般會員。

## 🚀 使用方法

### 方法 1: Docker 環境（推薦）

```bash
# 確保 Docker 容器正在運行
docker-compose ps

# 執行腳本
docker-compose exec backend python create_test_accounts.py
```

### 方法 2: 本地環境

```bash
cd backend

# 啟動虛擬環境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 執行腳本
python create_test_accounts.py
```

## 📊 自動建立的測試帳號

腳本會自動建立以下 4 個測試帳號：

### 1. 管理員帳號
- **Email**: admin@test.com
- **密碼**: Admin123
- **角色**: ADMIN
- **權限**: 
  - ✅ 訪問管理後台
  - ✅ 管理所有用戶
  - ✅ 審核領養申請
  - ✅ 管理醫療記錄
  - ✅ 查看任務狀態
  - ✅ 查看審計日誌

### 2. 收容所會員
- **Email**: shelter@test.com
- **密碼**: Shelter123
- **角色**: SHELTER_MEMBER
- **關聯收容所**: 測試收容所
- **權限**:
  - ✅ 管理收容所資料
  - ✅ 新增/編輯動物資料
  - ✅ 管理領養申請
  - ✅ 批次匯入動物
  - ✅ 查看任務狀態

### 3. 一般會員
- **Email**: user@test.com
- **密碼**: User123
- **角色**: GENERAL_MEMBER
- **權限**:
  - ✅ 瀏覽動物列表
  - ✅ 提交領養申請
  - ✅ 發佈送養資訊
  - ✅ 查看通知

### 4. 一般會員 2
- **Email**: user2@test.com
- **密碼**: User123
- **角色**: GENERAL_MEMBER
- **用途**: 額外測試帳號

## ⚙️ 腳本功能

1. **智能檢查**: 自動檢查帳號是否已存在，避免重複建立
2. **密碼雜湊**: 使用 bcrypt 安全地雜湊密碼
3. **關聯資料**: 自動建立收容所並關聯到收容所會員
4. **交易管理**: 使用資料庫交易確保資料一致性
5. **詳細輸出**: 顯示建立過程和結果摘要

## 📝 執行範例

```
============================================================
🚀 開始建立測試帳號...
============================================================

⏭️  跳過: admin@test.com (已存在)
   角色: ADMIN
   驗證狀態: ✅ 已驗證

⏭️  跳過: shelter@test.com (已存在)
   角色: SHELTER_MEMBER
   驗證狀態: ✅ 已驗證

✅ 建立: user@test.com
   使用者名稱: general_user
   密碼: User123
   角色: GENERAL_MEMBER
   描述: 一般會員 - 可瀏覽和申請領養

✅ 建立: user2@test.com
   使用者名稱: general_user2
   密碼: User123
   角色: GENERAL_MEMBER
   描述: 一般會員 2 - 額外測試帳號

============================================================
✅ 測試帳號建立完成!
   建立: 2 個
   跳過: 2 個
============================================================

📋 測試帳號摘要:
------------------------------------------------------------
角色             | Email                | 密碼
------------------------------------------------------------
管理員           | admin@test.com       | Admin123
收容所會員       | shelter@test.com     | Shelter123
一般會員         | user@test.com        | User123
一般會員2        | user2@test.com       | User123
------------------------------------------------------------

🌐 前端登入頁面: http://localhost:5173/login
📚 API 文檔: http://localhost:5000/api/docs
```

## 🔧 自訂腳本

如需建立額外的測試帳號，可以編輯 `backend/create_test_accounts.py`：

```python
test_accounts = [
    {
        'email': 'custom@test.com',
        'username': 'custom_user',
        'password': 'Custom123',
        'role': UserRole.GENERAL_MEMBER,
        'verified': True,
        'first_name': '自訂',
        'last_name': '用戶',
        'description': '自訂測試帳號'
    },
    # ... 更多帳號
]
```

## ⚠️ 注意事項

1. **生產環境**: 此腳本僅用於開發/測試環境，請勿在生產環境使用
2. **密碼安全**: 測試密碼已公開，僅用於開發測試
3. **重複執行**: 腳本可以安全地重複執行，已存在的帳號會被跳過
4. **資料庫連接**: 確保資料庫正在運行且可連接

## 🔗 相關文件

- [TEST_ACCOUNTS.md](TEST_ACCOUNTS.md) - 完整測試帳號列表
- [README.md](README.md) - 專案說明
- [docs/development.md](docs/development.md) - 開發指南

---

**最後更新**: 2025-10-26
