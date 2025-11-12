# Phase 6 Test Guide - Celery Workers & Background Tasks

**測試目的**: 驗證 Celery Workers 功能，包括批次匯入/匯出動物、非同步郵件發送、任務重試機制。

**測試環境**:
- Backend: http://localhost:5000
- Redis: localhost:6379
- Celery Worker: 需手動啟動
- PostgreSQL: localhost:5432

**前置條件**:
- Redis 已安裝並啟動
- Celery 已安裝 (`pip install celery redis`)
- Worker 已啟動 (參考 CELERY_WORKER_GUIDE.md)
- 至少有一個收容所管理員帳號

---

## 測試區塊 A: Celery Worker 啟動與基礎檢查

### A1. 安裝依賴
**目的**: 確保所有必要套件已安裝

**步驟**:
```powershell
cd backend
pip install celery redis
```

**預期結果**:
- ✅ Celery 成功安裝
- ✅ Redis 客戶端成功安裝

**實際結果**: ___________

---

### A2. 啟動 Redis
**目的**: 確保 Redis 服務運行

**步驟**:
```powershell
# Windows (使用 Docker)
docker run -d -p 6379:6379 --name redis redis:alpine

# 或使用 Redis for Windows
redis-server
```

**驗證 Redis**:
```powershell
redis-cli ping
# 應返回: PONG
```

**預期結果**:
- ✅ Redis 成功啟動
- ✅ `redis-cli ping` 返回 PONG

**實際結果**: ___________

---

### A3. 啟動 Celery Worker
**目的**: 啟動背景任務處理器

**步驟**:
```powershell
cd backend
python start_worker.py
```

**預期輸出**:
```
-------------- celery@HOSTNAME v5.x.x
--- ***** ----- 
-- ******* ---- Windows-10-x.x.x
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         app:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 4 (solo)
-- ******* ---- .> task events: OFF
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . app.tasks.animal_tasks.process_animal_batch_export
  . app.tasks.animal_tasks.process_animal_batch_import
  . app.tasks.email_tasks.send_application_notification_email_task
  . app.tasks.email_tasks.send_bulk_notification_email_task
  . app.tasks.email_tasks.send_password_reset_email_task
  . app.tasks.email_tasks.send_verification_email_task
```

**預期結果**:
- ✅ Worker 成功啟動
- ✅ 顯示 6 個已註冊的 tasks
- ✅ 使用 solo pool (Windows)
- ✅ 連線到 Redis

**實際結果**: ___________

---

### A4. 檢查已註冊任務
**目的**: 驗證所有 tasks 正確註冊

**步驟**:
```powershell
# 開啟新的 PowerShell 視窗
cd backend
celery -A app.celery:celery inspect registered
```

**預期結果**:
```json
{
  "celery@HOSTNAME": [
    "app.tasks.animal_tasks.process_animal_batch_export",
    "app.tasks.animal_tasks.process_animal_batch_import",
    "app.tasks.email_tasks.send_application_notification_email_task",
    "app.tasks.email_tasks.send_bulk_notification_email_task",
    "app.tasks.email_tasks.send_password_reset_email_task",
    "app.tasks.email_tasks.send_verification_email_task"
  ]
}
```

**實際結果**: ___________

---

## 測試區塊 B: 批次匯入動物任務

### B1. 創建批次匯入任務
**目的**: 測試批次匯入 API 是否正確創建 Job 並加入 Celery 隊列

**前置**: 
- 以收容所管理員身份登入
- 取得 JWT token

**準備測試 CSV**:
```csv
name,species,breed,age,gender,color,size,description,health_status
小白,狗,混種,3,公,白色,中型,活潑親人的狗狗,健康
小黑,貓,美短,2,母,黑色,小型,安靜溫和的貓咪,健康
小花,狗,拉布拉多,5,母,黃色,大型,友善愛玩的拉拉,健康
```

**步驟**:
```bash
# 1. 上傳 CSV 到 MinIO 或暫存 (目前 MinIO 未實作，會返回錯誤)
# 2. 創建批次匯入任務
curl -X POST http://localhost:5000/api/shelters/1/batch-import \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_url": "animals-import/test.csv",
    "options": {
      "batch_size": 100
    }
  }'
```

**預期 Response** (202 Accepted):
```json
{
  "message": "批次匯入已加入隊列",
  "job_id": 1,
  "status": "pending"
}
```

**預期 Worker 日誌**:
```
[INFO] Task app.tasks.animal_tasks.process_animal_batch_import[task-id] received
[INFO] Task app.tasks.animal_tasks.process_animal_batch_import[task-id] started
[ERROR] Task app.tasks.animal_tasks.process_animal_batch_import[task-id] failed: NotImplementedError('MinIO service not yet implemented...')
```

**預期結果**:
- ✅ API 返回 202 Accepted
- ✅ Job 記錄已創建 (status = PENDING)
- ✅ Worker 收到任務
- ⚠️ 任務失敗 (因為 MinIO 未實作)

**實際結果**: ___________

---

### B2. 檢查 Job 狀態
**目的**: 驗證 Job 狀態更新

**步驟**:
```bash
# 使用上一步返回的 job_id
curl -X GET http://localhost:5000/api/jobs/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**預期 Response**:
```json
{
  "job_id": 1,
  "job_type": "IMPORT_ANIMALS",
  "status": "FAILED",
  "created_by": 2,
  "created_at": "2025-10-26T...",
  "started_at": "2025-10-26T...",
  "completed_at": "2025-10-26T...",
  "result_summary": {
    "error": "MinIO service not yet implemented...",
    "error_type": "NotImplementedError"
  }
}
```

**預期結果**:
- ✅ Job 狀態變為 FAILED
- ✅ result_summary 包含錯誤訊息
- ✅ started_at 和 completed_at 已記錄

**實際結果**: ___________

---

## 測試區塊 C: Email 非同步任務

### C1. 密碼重置郵件任務
**目的**: 測試非同步發送密碼重置郵件

**步驟**:
```bash
# 請求密碼重置
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

**預期行為**:
1. API 立即返回成功 (不等待郵件發送)
2. Worker 在背景處理郵件發送任務

**目前實作**: 郵件發送是同步的 (TODO: 改為異步)

**改進建議**: 在 `auth.py` 中替換為:
```python
# 舊代碼 (同步)
email_service.send_password_reset_email(user.email, token)

# 新代碼 (異步)
from app.tasks import send_password_reset_email_task
send_password_reset_email_task.delay(user.email, token)
```

**預期結果**:
- ✅ API 快速返回 (< 100ms)
- ✅ Worker 日誌顯示郵件任務
- ✅ 郵件發送成功或失敗記錄在 Worker 日誌

**實際結果**: ___________

---

### C2. 申請通知郵件任務
**目的**: 測試申請狀態變更時的郵件通知

**步驟**:
```bash
# 1. 創建申請
curl -X POST http://localhost:5000/api/animals/1/applications \
  -H "Authorization: Bearer USER_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "motivation": "我想領養這隻可愛的動物",
    "living_situation": "獨立公寓，有陽台",
    "experience": "曾養過2隻貓"
  }'

# 2. 審核者通過申請 (應觸發郵件)
curl -X POST http://localhost:5000/api/applications/1/review \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approved",
    "reviewer_notes": "申請條件符合",
    "version": 1
  }'
```

**目前實作**: 無自動郵件通知 (TODO)

**改進建議**: 在 `applications.py` 的審核端點中添加:
```python
from app.tasks import send_application_notification_email_task

if decision == 'approved':
    send_application_notification_email_task.delay(
        user_email=application.user.email,
        animal_name=application.animal.name,
        status='approved',
        message=reviewer_notes
    )
```

**預期結果**:
- ✅ 審核完成後自動發送郵件
- ✅ Worker 處理郵件任務
- ✅ 用戶收到通知郵件

**實際結果**: ___________

---

## 測試區塊 D: 任務重試機制

### D1. 測試重試邏輯
**目的**: 驗證失敗任務的自動重試

**測試方法**: 暫時停止 Redis 模擬失敗

**步驟**:
```bash
# 1. 觸發郵件任務
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. 立即停止 Redis
docker stop redis

# 3. 觀察 Worker 日誌
```

**預期 Worker 日誌**:
```
[INFO] Task send_password_reset_email_task[id] received
[WARNING] Task send_password_reset_email_task[id] retry: Retry in 60s (attempt 1/3)
[WARNING] Task send_password_reset_email_task[id] retry: Retry in 120s (attempt 2/3)
[WARNING] Task send_password_reset_email_task[id] retry: Retry in 240s (attempt 3/3)
[ERROR] Task send_password_reset_email_task[id] failed after 3 retries
```

**重試策略**:
- 第 1 次: 60 秒後重試
- 第 2 次: 120 秒後重試
- 第 3 次: 240 秒後重試
- 指數退避: countdown = 60 * (2 ** retries)

**預期結果**:
- ✅ 任務自動重試 3 次
- ✅ 每次重試間隔遞增
- ✅ 3 次失敗後標記為 FAILED

**實際結果**: ___________

---

## 測試區塊 E: Celery 監控與管理

### E1. 檢查活躍任務
**目的**: 查看正在執行的任務

**步驟**:
```powershell
celery -A app.celery:celery inspect active
```

**預期輸出**:
```json
{
  "celery@HOSTNAME": [
    {
      "id": "task-id",
      "name": "app.tasks.animal_tasks.process_animal_batch_import",
      "args": [1],
      "kwargs": {},
      "time_start": 1234567890.123,
      "acknowledged": true,
      "delivery_info": {...}
    }
  ]
}
```

**實際結果**: ___________

---

### E2. 檢查任務統計
**目的**: 查看 Worker 統計資訊

**步驟**:
```powershell
celery -A app.celery:celery inspect stats
```

**預期輸出**: 包含
- total: 總任務數
- app.tasks.xxx: 各任務執行次數
- rusage: 資源使用情況

**實際結果**: ___________

---

### E3. 安裝並啟動 Flower (可選)
**目的**: 使用 Web UI 監控 Celery

**步驟**:
```powershell
pip install flower
celery -A app.celery:celery flower --port=5555
```

**訪問**: http://localhost:5555

**預期結果**:
- ✅ Flower UI 成功啟動
- ✅ 顯示 Worker 狀態
- ✅ 顯示任務列表與執行歷史
- ✅ 可以即時監控任務進度

**實際結果**: ___________

---

## 測試區塊 F: 整合測試

### F1. 完整批次匯入流程 (當 MinIO 實作後)
**情境**: 收容所管理員批次匯入動物資料

**步驟**:
1. 準備 CSV 檔案 (100 筆動物資料)
2. 上傳到 MinIO
3. 創建批次匯入 Job
4. Worker 處理任務
5. 檢查 Job 狀態和結果
6. 驗證動物已新增到資料庫

**預期流程**:
```
API (POST /batch-import) 
  → 創建 Job (PENDING)
  → Celery 接收任務
  → Worker 開始處理 (RUNNING)
  → 下載 CSV
  → 解析並驗證資料
  → 批次插入資料庫
  → 更新 Job (SUCCEEDED)
  → 返回統計結果
```

**實際結果**: ___________

---

### F2. 郵件發送整合流程
**情境**: 新用戶註冊 → 發送驗證郵件

**步驟**:
1. 用戶註冊
2. 系統生成驗證 token
3. 異步發送驗證郵件
4. 用戶點擊連結驗證

**目前狀態**: 郵件是同步發送 (TODO: 改為異步)

**改進清單**:
- [ ] `auth.py` - 註冊時異步發送驗證郵件
- [ ] `auth.py` - 密碼重置異步發送郵件
- [ ] `applications.py` - 申請狀態變更異步通知

**實際結果**: ___________

---

## 測試區塊 G: 效能測試

### G1. 批次任務效能
**目的**: 測試大量資料匯入的效能

**測試數據**: 1000 筆動物資料

**測量指標**:
- 總執行時間
- 平均每筆處理時間
- 記憶體使用量
- CPU 使用率

**預期效能**:
- 1000 筆資料 < 30 秒
- 平均 ~30ms/筆
- 記憶體 < 500MB

**實際結果**: ___________

---

### G2. 並發任務處理
**目的**: 測試 Worker 處理多個任務的能力

**步驟**:
1. 同時觸發 10 個郵件發送任務
2. 觀察 Worker 處理順序
3. 檢查是否有任務遺失

**預期行為**:
- ✅ 所有任務都被處理
- ✅ 並發數量 = 4 (concurrency 設定)
- ✅ 任務排隊等待處理

**實際結果**: ___________

---

## 測試總結

### 完成的功能 (✅)
- [ ] A1-A4: Celery Worker 基礎設定
- [ ] B1-B2: 批次匯入 API 整合
- [ ] C1-C2: Email 任務 (部分異步)
- [ ] D1: 重試機制
- [ ] E1-E3: 監控工具
- [ ] F1-F2: 整合流程
- [ ] G1-G2: 效能測試

### 待完成的功能 (TODO)
1. **MinIO 服務整合**: 實作檔案上傳/下載
2. **批次匯出功能**: 完整實作並測試
3. **郵件異步化**: 將所有郵件改為異步發送
4. **通知整合**: 任務完成後發送系統通知
5. **錯誤處理**: 改進錯誤訊息和用戶反饋
6. **任務取消**: 實作任務取消功能
7. **任務優先級**: 設定不同任務的優先級

### 發現的問題
1. MinIO 服務未實作，批次匯入無法完整測試
2. 郵件發送仍為同步，影響 API 回應時間
3. Worker 在 Windows 必須使用 solo pool (效能較差)

---

**測試完成日期**: ___________  
**測試人員**: ___________  
**Worker 版本**: Celery 5.x.x  
**Redis 版本**: ___________
