# Phase 3 測試指南 - Applications 模組與進階功能

**測試日期**: 2025-10-26  
**測試範圍**: 領養申請流程、Idempotency、Optimistic Locking  
**前置條件**: Phase 1 & Phase 2 測試通過

---

## 📋 測試環境設定

### 1. 啟動所有服務
```powershell
cd C:\Users\user\Desktop\school_work\software_eng\midterm_work\SoftwareEngineeringProject\proj_new

# 啟動後端 (Docker)
docker-compose up -d

# 啟動前端
cd frontend
npm run dev
```

### 2. 確認服務狀態
- ✅ 前端: http://localhost:5173
- ✅ 後端: http://localhost:5000
- ✅ 資料庫: MySQL (port 3307)
- ✅ MinIO: http://localhost:9000

### 3. 測試帳號
```
一般使用者:
- Email: test@example.com
- Password: Test1234

管理員:
- Email: admin@example.com
- Password: Admin1234
```

---

## 🎯 Phase 3 測試項目

### 測試區塊 A: 領養申請功能 (Application Creation)

#### A1. 瀏覽並申請動物
**目的**: 測試完整的申請流程

**步驟**:
1. 以一般使用者登入 (test@example.com)
2. 前往「瀏覽動物」頁面 (http://localhost:5173/animals)
3. 點擊任一「已上架」(PUBLISHED) 的動物
4. 確認顯示「我想領養」按鈕
5. 點擊「我想領養」按鈕

**預期結果**:
- ✅ 彈出申請表單對話框
- ✅ 顯示動物資訊摘要 (照片、名稱、品種)
- ✅ 申請類型選項: 領養、中途送養
- ✅ 顯示申請說明與條款

---

#### A2. 提交領養申請
**目的**: 測試申請提交與 Idempotency 機制

**步驟**:
1. 在申請表單中:
   - 選擇「領養」類型
   - 勾選「同意條款」
2. 點擊「確認申請」
3. 觀察頁面跳轉

**預期結果**:
- ✅ 顯示「提交中...」狀態
- ✅ 成功後自動跳轉至「我的申請」頁面
- ✅ 申請列表中出現新申請
- ✅ 狀態顯示為「待審核」(PENDING)

**後端驗證**:
```bash
# 查看後端日誌確認 Idempotency-Key
docker logs pet-adoption-backend --tail 50
```
應看到類似: `Created application with idempotency_key: apply-{animal_id}-{timestamp}`

---

#### A3. 防止重複申請
**目的**: 測試 Idempotency 機制防止重複提交

**步驟**:
1. 前往相同動物的詳情頁
2. 再次點擊「我想領養」
3. 填寫表單並提交

**預期結果**:
- ✅ 顯示錯誤訊息: "您已經申請過此動物了"
- ✅ HTTP 狀態碼: 409 Conflict
- ✅ 不會建立重複申請

---

#### A4. 無法申請自己的動物
**目的**: 測試擁有權驗證

**步驟**:
1. 前往「我的送養」頁面
2. 點擊自己刊登的動物
3. 確認沒有「我想領養」按鈕

**預期結果**:
- ✅ 不顯示「我想領養」按鈕
- ✅ 顯示「編輯」按鈕 (如果是擁有者)

**額外測試** (如果透過 API 強制提交):
```bash
# 使用 curl 測試 (需替換 token 和 animal_id)
curl -X POST http://localhost:5000/api/applications \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"animal_id": YOUR_OWN_ANIMAL_ID, "type": "ADOPTION"}'
```
預期: `400 Bad Request` - "您不能申請自己刊登的動物"

---

### 測試區塊 B: 我的申請管理 (My Applications)

#### B1. 查看申請列表
**目的**: 測試申請列表顯示與篩選

**步驟**:
1. 登入後前往「我的申請」(http://localhost:5173/my/applications)
2. 觀察申請卡片顯示

**預期結果**:
- ✅ 顯示所有申請記錄
- ✅ 每個卡片包含:
  - 動物照片
  - 動物名稱、品種
  - 申請類型 (領養/中途送養)
  - 申請狀態 (顏色標籤)
  - 提交日期
  - 操作按鈕 (撤銷/查看)

---

#### B2. 狀態篩選
**目的**: 測試申請狀態篩選功能

**步驟**:
1. 點擊「全部」按鈕
2. 依序點擊各狀態按鈕:
   - 待審核 (PENDING)
   - 審核中 (UNDER_REVIEW)
   - 已通過 (APPROVED)
   - 已拒絕 (REJECTED)
   - 已撤銷 (WITHDRAWN)

**預期結果**:
- ✅ 按鈕顯示當前選中狀態 (藍色背景)
- ✅ 列表僅顯示對應狀態的申請
- ✅ 若無資料顯示空狀態訊息

---

#### B3. 撤銷申請
**目的**: 測試撤銷功能

**步驟**:
1. 找到一個「待審核」或「審核中」的申請
2. 點擊「撤銷申請」按鈕
3. 確認彈出確認對話框
4. 點擊「確認」

**預期結果**:
- ✅ 顯示確認對話框
- ✅ 成功後狀態變更為「已撤銷」
- ✅ 該申請從當前篩選消失 (如果在待審核/審核中篩選)
- ✅ 在「已撤銷」篩選中出現

**限制驗證**:
- 「已通過」、「已拒絕」、「已撤銷」的申請不顯示撤銷按鈕

---

#### B4. 分頁功能
**目的**: 測試申請列表分頁

**步驟**:
1. 確保有超過 10 筆申請記錄 (如果沒有,多建立幾筆)
2. 觀察頁面底部分頁控制
3. 點擊「下一頁」
4. 點擊「上一頁」
5. 點擊特定頁碼

**預期結果**:
- ✅ 每頁顯示最多 10 筆記錄
- ✅ 分頁按鈕正確顯示總頁數
- ✅ 當前頁碼高亮顯示
- ✅ 第一頁時「上一頁」按鈕禁用
- ✅ 最後一頁時「下一頁」按鈕禁用

---

### 測試區塊 C: 申請審核 (Application Review - 需管理員權限)

#### C1. 指派審核人員
**目的**: 測試申請指派功能

**步驟**:
1. 以管理員身份登入 (admin@example.com)
2. 使用 API 測試工具 (如 Postman 或 curl):
```bash
curl -X POST http://localhost:5000/api/applications/{application_id}/assign \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assignee_id": REVIEWER_USER_ID}'
```

**預期結果**:
- ✅ 狀態變更為「審核中」(UNDER_REVIEW)
- ✅ `assignee_id` 欄位更新
- ✅ `version` 欄位自動遞增

---

#### C2. 審核申請 (核准)
**目的**: 測試申請核准流程與 Optimistic Locking

**步驟**:
1. 取得申請詳情 (含 version):
```bash
curl -X GET http://localhost:5000/api/applications/{application_id} \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

2. 核准申請:
```bash
curl -X POST http://localhost:5000/api/applications/{application_id}/review \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "review_notes": "申請人條件符合,核准領養",
    "version": CURRENT_VERSION
  }'
```

**預期結果**:
- ✅ 狀態變更為「已通過」(APPROVED)
- ✅ `reviewed_at` 時間戳記更新
- ✅ `review_notes` 儲存審核意見
- ✅ `version` 遞增
- ✅ 建立 Audit Log 記錄

**Audit Log 驗證**:
```sql
-- 在資料庫中查詢
SELECT * FROM audit_logs 
WHERE entity_type = 'application' 
  AND entity_id = {application_id}
ORDER BY created_at DESC LIMIT 5;
```

---

#### C3. 審核申請 (拒絕)
**目的**: 測試申請拒絕流程

**步驟**:
```bash
curl -X POST http://localhost:5000/api/applications/{application_id}/review \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reject",
    "review_notes": "申請人未提供完整資料",
    "version": CURRENT_VERSION
  }'
```

**預期結果**:
- ✅ 狀態變更為「已拒絕」(REJECTED)
- ✅ 拒絕原因記錄在 `review_notes`
- ✅ 建立 Audit Log 記錄

---

#### C4. Optimistic Locking 測試
**目的**: 測試併發衝突檢測

**步驟**:
1. 取得申請當前 version (假設為 3)
2. 第一次審核請求 (使用 version=3):
```bash
curl -X POST http://localhost:5000/api/applications/{application_id}/review \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "approve", "version": 3}'
```

3. 第二次審核請求 (仍使用過期的 version=3):
```bash
curl -X POST http://localhost:5000/api/applications/{application_id}/review \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "reject", "version": 3}'
```

**預期結果**:
- ✅ 第一次請求: `200 OK` - 審核成功,version 變為 4
- ✅ 第二次請求: `409 Conflict` - 錯誤訊息: "申請已被其他人修改,請重新載入"
- ✅ 保護資料完整性,避免覆蓋他人的變更

---

### 測試區塊 D: 整合測試 (End-to-End Scenarios)

#### D1. 完整領養流程
**目的**: 測試從申請到核准的完整流程

**步驟**:
1. **使用者 A**: 登入並申請領養動物 X
2. **管理員**: 指派審核給使用者 B
3. **使用者 B**: 審核並核准申請
4. **使用者 A**: 查看申請狀態變更

**預期結果**:
- ✅ 每個步驟狀態正確變更
- ✅ 所有 Audit Log 記錄完整
- ✅ 通知系統觸發 (如已實作)

---

#### D2. 多重申請場景
**目的**: 測試同一使用者申請多個動物

**步驟**:
1. 使用者申請動物 A (領養)
2. 使用者申請動物 B (中途送養)
3. 使用者申請動物 C (領養)
4. 前往「我的申請」查看

**預期結果**:
- ✅ 三筆申請都成功建立
- ✅ 每筆申請有獨立的 `idempotency_key`
- ✅ 列表正確顯示所有申請
- ✅ 可以分別操作各筆申請

---

#### D3. 申請撤銷後重新申請
**目的**: 測試撤銷後是否可再次申請

**步驟**:
1. 申請動物 X
2. 撤銷該申請
3. 再次申請動物 X

**預期結果**:
- ✅ 撤銷成功
- ✅ 可以重新申請 (因為 idempotency_key 不同)
- ✅ 建立新的申請記錄

---

### 測試區塊 E: API 錯誤處理測試

#### E1. 未登入訪問
**步驟**:
```bash
curl -X POST http://localhost:5000/api/applications \
  -H "Content-Type: application/json" \
  -d '{"animal_id": 1, "type": "ADOPTION"}'
```

**預期結果**:
- ✅ `401 Unauthorized`
- ✅ 錯誤訊息: "Missing authorization header"

---

#### E2. 申請不存在的動物
**步驟**:
```bash
curl -X POST http://localhost:5000/api/applications \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"animal_id": 99999, "type": "ADOPTION"}'
```

**預期結果**:
- ✅ `404 Not Found`
- ✅ 錯誤訊息: "動物不存在"

---

#### E3. 申請未上架的動物
**步驟**:
1. 建立一個草稿狀態的動物
2. 嘗試申請該動物

**預期結果**:
- ✅ `400 Bad Request`
- ✅ 錯誤訊息: "此動物尚未上架或已下架"

---

#### E4. 無效的申請類型
**步驟**:
```bash
curl -X POST http://localhost:5000/api/applications \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"animal_id": 1, "type": "INVALID_TYPE"}'
```

**預期結果**:
- ✅ `400 Bad Request`
- ✅ 驗證錯誤訊息

---

#### E5. 非審核人員嘗試審核
**步驟**:
```bash
curl -X POST http://localhost:5000/api/applications/{application_id}/review \
  -H "Authorization: Bearer NORMAL_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'
```

**預期結果**:
- ✅ `403 Forbidden`
- ✅ 錯誤訊息: "無權限操作"

---

### 測試區塊 F: 資料庫驗證

#### F1. 檢查 Idempotency Key
**SQL 查詢**:
```sql
SELECT application_id, animal_id, applicant_id, idempotency_key, created_at
FROM applications
ORDER BY created_at DESC
LIMIT 10;
```

**驗證**:
- ✅ `idempotency_key` 欄位有值且唯一
- ✅ 格式: `apply-{animal_id}-{timestamp}`

---

#### F2. 檢查 Version 欄位
**SQL 查詢**:
```sql
SELECT application_id, status, version, created_at, updated_at
FROM applications
WHERE application_id = {test_application_id};
```

**驗證**:
- ✅ 新建立的申請 `version = 0`
- ✅ 每次審核/指派後 `version` 遞增
- ✅ `updated_at` 正確更新

---

#### F3. 檢查 Audit Logs
**SQL 查詢**:
```sql
SELECT 
  audit_log_id,
  action,
  entity_type,
  entity_id,
  user_id,
  changes,
  created_at
FROM audit_logs
WHERE entity_type = 'application'
  AND entity_id = {test_application_id}
ORDER BY created_at DESC;
```

**驗證**:
- ✅ 審核操作有對應的 audit log
- ✅ `action` = 'application_review'
- ✅ `changes` 包含審核動作和意見 (JSON 格式)

---

#### F4. 檢查外鍵關聯
**SQL 查詢**:
```sql
SELECT 
  a.application_id,
  a.status,
  u.username AS applicant_name,
  an.name AS animal_name,
  r.username AS reviewer_name
FROM applications a
LEFT JOIN users u ON a.applicant_id = u.user_id
LEFT JOIN animals an ON a.animal_id = an.animal_id
LEFT JOIN users r ON a.assignee_id = r.user_id
WHERE a.application_id = {test_application_id};
```

**驗證**:
- ✅ 所有外鍵正確關聯
- ✅ 申請人、動物、審核人資料正確顯示

---

## 🔍 效能測試 (Performance)

### P1. 大量申請列表載入
**目的**: 測試分頁效能

**步驟**:
1. 建立 50+ 筆申請記錄
2. 訪問「我的申請」頁面
3. 測量載入時間

**預期結果**:
- ✅ 首次載入 < 2 秒
- ✅ 分頁切換 < 500ms
- ✅ 不會一次載入所有記錄

---

### P2. Idempotency Key 查詢效能
**SQL 測試**:
```sql
EXPLAIN SELECT * FROM applications 
WHERE idempotency_key = 'apply-1-1234567890' 
  AND applicant_id = 1;
```

**驗證**:
- ✅ 使用索引查詢 (type = 'ref' 或 'const')
- ✅ rows < 10
- ✅ 查詢時間 < 10ms

---

## 📊 測試檢查清單

### 功能完整性
- [ ] A1-A4: 申請建立流程 (4/4)
- [ ] B1-B4: 我的申請管理 (4/4)
- [ ] C1-C4: 申請審核功能 (4/4)
- [ ] D1-D3: 整合測試 (3/3)
- [ ] E1-E5: 錯誤處理 (5/5)
- [ ] F1-F4: 資料庫驗證 (4/4)

### 架構模式驗證
- [ ] Idempotency 機制正常運作
- [ ] Optimistic Locking 防止併發衝突
- [ ] Audit Logging 完整記錄
- [ ] RBAC 權限控制正確

### UI/UX 驗證
- [ ] 所有按鈕和表單可正常操作
- [ ] 錯誤訊息清晰易懂
- [ ] 載入狀態正確顯示
- [ ] 響應式設計在不同螢幕尺寸正常

---

## 🐛 已知問題與限制

### 當前限制
1. 前端尚未實作申請詳情頁面
2. 通知系統僅後端實作,前端 UI 未完成
3. 電子郵件通知功能未啟用
4. WebSocket 即時通知未實作

### 未來改進
1. 新增申請詳情頁面 (含完整時間軸)
2. 實作前端通知中心
3. 整合電子郵件服務
4. 新增申請附件上傳功能

---

## 📝 測試報告範本

```
測試日期: _______________
測試人員: _______________
測試環境: Development

【測試結果統計】
- 總測試項目: 24
- 通過項目: ___
- 失敗項目: ___
- 跳過項目: ___

【重大問題】
1. 
2. 

【建議事項】
1. 
2. 

【測試結論】
□ 通過,可進入下一階段
□ 需修復問題後重新測試
```

---

## 🎓 測試技巧

### 使用 Browser DevTools
1. **Network Tab**: 觀察 API 請求和響應
2. **Console Tab**: 查看前端錯誤和日誌
3. **Application > Local Storage**: 檢查 JWT token

### 使用 Docker 查看日誌
```powershell
# 即時查看後端日誌
docker logs -f pet-adoption-backend

# 查看最近 100 行
docker logs pet-adoption-backend --tail 100

# 搜尋特定關鍵字
docker logs pet-adoption-backend | Select-String "application"
```

### 資料庫查詢技巧
```bash
# 進入 MySQL 容器
docker exec -it pet-adoption-db mysql -u root -p

# 使用資料庫
USE pet_adoption;

# 查看最近建立的申請
SELECT * FROM applications ORDER BY created_at DESC LIMIT 5;
```

---

**測試完成後**: 請填寫測試報告並將結果回報給專案負責人。

**下一階段**: Phase 4 - Email Verification & Job Pattern 測試
