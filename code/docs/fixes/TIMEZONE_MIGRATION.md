# 系統時間修正 - 台北時區遷移

## 問題描述
系統原本使用 `datetime.utcnow()` 導致顯示的時間比台北時間慢 8 小時。

## 解決方案
採用**方案 3：後端程式碼全面改用台北時間**

### 核心修改
1. 創建 `app/utils/datetime_helper.py` 提供台北時區函數
2. 所有 Models 的時間戳記 `default` 改用 `get_naive_taipei_now`
3. 所有 Services、Tasks、Blueprints 中的 `datetime.utcnow()` 改用 `get_naive_taipei_now()`

## 修改的檔案清單

### 1. Utility Functions (1 個檔案)
- ✅ `app/utils/datetime_helper.py` - 新增 `get_naive_taipei_now()` 函數

### 2. Models (8 個檔案)
所有 Model 的 `created_at`, `updated_at` 欄位都已修改：
- ✅ `app/models/user.py` - User
- ✅ `app/models/shelter.py` - Shelter
- ✅ `app/models/animal.py` - Animal, AnimalImage (含 age 計算)
- ✅ `app/models/application.py` - Application
- ✅ `app/models/medical_record.py` - MedicalRecord
- ✅ `app/models/others.py` - Notification, Job, Attachment, AuditLog
- ✅ `app/models/pending_registration.py` - PendingRegistration

### 3. Services (9 個檔案)
所有 Service 中的 `datetime.utcnow()` 調用都已替換：
- ✅ `app/services/auth_service.py` - 6 處 (註冊驗證碼、登入時間、密碼修改時間)
- ✅ `app/services/notification_service.py` - 3 處 (創建、標記已讀)
- ✅ `app/services/medical_record_service.py` - 3 處 (權限檢查、更新時間)
- ✅ `app/services/application_service.py` - 3 處 (提交時間、審核時間)
- ✅ `app/services/job_service.py` - 5 處 (任務完成時間)
- ✅ `app/services/admin_service.py` - 2 處 (帳號鎖定時間)
- ✅ `app/services/shelter_service.py` - 6 處 (更新時間)
- ✅ `app/services/user_service.py` - 2 處 (更新時間、密碼修改時間)
- ✅ `app/services/attachment_service.py` - 1 處 (刪除時間)
- ✅ `app/services/audit_service.py` - 1 處 (審計時間戳)

### 4. Tasks (1 個檔案)
- ✅ `app/tasks/animal_tasks.py` - 11 處 (批次任務時間戳)

### 5. Blueprints (1 個檔案)
- ✅ `app/blueprints/shelters.py` - 1 處 (日期計算)

## 修改模式

### Model 修改
```python
# Before
from datetime import datetime
created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
updated_at = db.Column(db.DateTime(6), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# After
from app.utils.datetime_helper import get_naive_taipei_now
created_at = db.Column(db.DateTime(6), default=get_naive_taipei_now, nullable=False)
updated_at = db.Column(db.DateTime(6), default=get_naive_taipei_now, onupdate=get_naive_taipei_now, nullable=False)
```

### Service/Task 修改
```python
# Before
from datetime import datetime
user.last_login_at = datetime.utcnow()

# After
from app.utils.datetime_helper import get_naive_taipei_now
user.last_login_at = get_naive_taipei_now()
```

## 驗證
執行以下指令確認所有 `datetime.utcnow()` 都已替換：
```bash
grep -r "datetime\.utcnow()" app/
```
應該沒有任何結果。

## 注意事項
1. 所有時間都使用 naive datetime（無時區資訊），符合 SQLAlchemy 需求
2. 時間比較邏輯（如過期檢查）確保兩邊都使用台北時間
3. 資料庫中已存在的舊資料時間不會自動轉換，新資料會使用台北時間
4. 如果需要與外部系統對接，可能需要額外的時區轉換

## 修改日期
2025-01-XX

## 修改者
GitHub Copilot (Automated Migration)
