# 🚀 下階段實作詳細規劃
生成時間: 2025-10-26 16:06:08

---

## 📊 當前系統狀態總覽

### ✅ 已完成模組 (100%)
| 模組 | 後端 | 前端 | 測試 | 狀態 |
|------|------|------|------|------|
| **密碼重置** | ✅ 100% | ✅ 100% | ✅ PHASE4 | 🎉 完全實作 |
| **通知中心** | ✅ 100% | ✅ 100% | ⚠️ 缺測試 | 🎉 功能完成 |
| **動物管理** | ✅ 100% | ✅ 100% | ✅ PHASE2 | 🎉 完全實作 |
| **醫療記錄** | ✅ 100% | ✅ 100% | ✅ PHASE8 | 🎉 完全實作 |
| **任務狀態** | ✅ 100% | ✅ 100% | ⚠️ 缺測試 | 🎉 功能完成 |

### ⚠️ 未完成模組
| 模組 | 後端 | 前端 | 完成度 | 缺失項目 |
|------|------|------|--------|----------|
| **收容所管理** | 80% | 0% | 40% | 缺前端頁面 |
| **用戶個資** | 70% | 50% | 60% | 缺GDPR功能 |
| **審計日誌** | 100% | 0% | 50% | 缺前端頁面 |

---

## 🎯 優先級 P0 - 緊急功能 (0項)

**✅ 全部完成!** 密碼重置、通知中心已實作

---

## �� 優先級 P1 - 高價值功能 (2項)

### 📋 #1: 收容所管理頁面
**預計時間:** 3-4 小時
**完成度:** 40% (後端80%完成)
**用戶價值:** ⭐⭐⭐⭐⭐

#### 需要實作的功能:
1. **Shelters.vue** - 收容所列表頁面
   - 🔧 功能需求:
     * 收容所卡片展示(名稱、地址、聯絡方式、動物數量)
     * 搜尋與篩選(地區、驗證狀態)
     * 分頁
     * 點擊進入詳情頁
   
   - 📝 API 端點:
     * GET /api/shelters (已存在)
     * 回應格式: { shelters: [], total: 0 }
   
   - 🎨 UI 設計:
     * 使用卡片佈局(grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
     * 驗證標記(綠色 ✓ / 灰色 ⏳)
     * 動物數量 badge
     * 響應式設計

2. **ShelterDetail.vue** - 收容所詳情頁面
   - 🔧 功能需求:
     * 收容所完整資訊
     * 該收容所的動物列表
     * 聯絡表單
     * 管理員可編輯
   
   - 📝 API 端點:
     * GET /api/shelters/{id} (已存在)
     * GET /api/animals?shelter_id={id} (已存在)
   
   - 🎨 UI 設計:
     * 上半部:收容所資訊卡片
     * 下半部:動物列表 tab
     * 編輯按鈕(僅管理員可見)

3. **路由配置**
   \\\	ypescript
   // frontend/src/router/index.ts 新增:
   {
     path: '/shelters',
     name: 'Shelters',
     component: () => import('@/pages/Shelters.vue'),
     meta: { title: '收容所列表' }
   },
   {
     path: '/shelters/:id',
     name: 'ShelterDetail',
     component: () => import('@/pages/ShelterDetail.vue'),
     meta: { title: '收容所詳情' }
   }
   \\\

4. **導航整合**
   - Home.vue: 新增「瀏覽收容所」區塊
   - Navbar: 新增收容所連結

#### 實作步驟:
1. ✅ 檢查後端 API (已完成80%)
2. 📄 建立 shelters.ts API client
3. 🎨 建立 Shelters.vue (列表)
4. 🎨 建立 ShelterDetail.vue (詳情)
5. 🔗 配置路由
6. 🧭 整合導航
7. ✅ 測試功能
8. 📝 撰寫 PHASE10_TEST_GUIDE.md

---

### 📋 #2: 審計日誌查詢頁面 (Admin)
**預計時間:** 2-3 小時
**完成度:** 50% (後端100%完成)
**用戶價值:** ⭐⭐⭐⭐

#### 需要實作的功能:
1. **AuditLogs.vue** - 日誌查詢頁面(僅限管理員)
   - 🔧 功能需求:
     * 日誌列表展示
     * 多重篩選(action、時間範圍、actor_id、target_type)
     * 時間軸顯示
     * JSON 詳情展開/摺疊
     * 匯出 CSV 功能
   
   - 📝 API 端點:
     * GET /api/audit-logs (已存在)
     * 查詢參數: action, actor_id, target_type, start_date, end_date, page, per_page
   
   - 🎨 UI 設計:
     * 上方:篩選列(日期選擇器、下拉選單)
     * 中間:時間軸列表
     * 每個項目:展開可看 before_state / after_state
     * 匯出按鈕(轉 CSV)

2. **auditLogs.ts API Client**
   \\\	ypescript
   // frontend/src/api/auditLogs.ts
   export interface AuditLogFilters {
     action?: string;
     actor_id?: number;
     target_type?: string;
     start_date?: string;
     end_date?: string;
     page?: number;
     per_page?: number;
   }
   
   export async function getAuditLogs(filters?: AuditLogFilters) {
     const response = await api.get('/audit-logs', { params: filters });
     return response.data;
   }
   \\\

3. **路由配置** (僅限 ADMIN)
   \\\	ypescript
   {
     path: '/audit-logs',
     name: 'AuditLogs',
     component: () => import('@/pages/AuditLogs.vue'),
     meta: { 
       title: '審計日誌', 
       requiresAuth: true, 
       requiresRole: ['ADMIN'] 
     }
   }
   \\\

4. **AdminDashboard 整合**
   - 新增「審計日誌」快捷按鈕

#### 實作步驟:
1. ✅ 確認後端 API (已100%完成)
2. 📄 建立 auditLogs.ts API client
3. 🎨 建立 AuditLogs.vue
4. 🔗 配置路由(ADMIN only)
5. 🧭 整合到 AdminDashboard
6. ✅ 測試查詢與篩選
7. 📝 更新測試文件

---

## 🎯 優先級 P2 - 完善功能 (3項)

### 📋 #3: 用戶個人資料頁面
**預計時間:** 2 小時
**完成度:** 60%
**用戶價值:** ⭐⭐⭐⭐

#### 需要實作的功能:
1. **UserProfile.vue** - 個人資料編輯
   - 🔧 功能需求:
     * 顯示當前資料
     * 編輯個人資訊(username, first_name, last_name, phone_number)
     * 修改密碼(需輸入舊密碼)
     * 頭像上傳
   
   - 📝 API 端點:
     * GET /api/auth/me (已存在)
     * PATCH /api/users/{id} (已存在)
     * POST /api/uploads/avatar (需檢查)
   
   - 🎨 UI 設計:
     * Tab 切換:個人資料 / 安全設定 / 帳號管理
     * 表單驗證
     * 儲存成功提示

#### 實作步驟:
1. 📄 檢查 users.ts API client
2. 🎨 建立 UserProfile.vue
3. 🔗 配置路由
4. 🧭 Navbar 加入「個人設定」選單
5. ✅ 測試編輯功能

---

### 📋 #4: GDPR 個資管理功能
**預計時間:** 3 小時
**完成度:** 30%
**用戶價值:** ⭐⭐⭐

#### 需要實作的功能:
1. **後端 API** (需新增)
   \\\python
   # backend/app/blueprints/users.py
   
   @users_bp.route('/data/export', methods=['POST'])
   @jwt_required()
   def export_user_data():
       \"\"\"個資匯出(Job Pattern)\"\"\"
       user_id = int(get_jwt_identity())
       
       # 建立 Job
       job = Job(
           job_type='data_export',
           status=JobStatus.PENDING,
           created_by=user_id
       )
       db.session.add(job)
       db.session.commit()
       
       # 加入 Celery 隊列
       export_user_data_task.delay(job.job_id)
       
       return jsonify({
           'message': '資料匯出已開始',
           'job_id': job.job_id
       }), 202
   
   @users_bp.route('/data/delete-request', methods=['POST'])
   @jwt_required()
   def request_account_deletion():
       \"\"\"帳號刪除申請\"\"\"
       user_id = int(get_jwt_identity())
       
       # 建立 Job
       job = Job(
           job_type='account_deletion_request',
           status=JobStatus.PENDING,
           created_by=user_id
       )
       db.session.add(job)
       db.session.commit()
       
       # 通知管理員審核
       notify_admins_for_deletion_approval.delay(job.job_id)
       
       return jsonify({
           'message': '刪除申請已提交,待管理員審核',
           'job_id': job.job_id
       }), 202
   \\\

2. **Celery Worker** (需實作)
   \\\python
   # backend/app/tasks/user_tasks.py (新檔案)
   
   from app.celery import celery
   
   @celery.task
   def export_user_data_task(job_id):
       \"\"\"匯出用戶所有資料為 JSON/CSV\"\"\"
       job = Job.query.get(job_id)
       user = User.query.get(job.created_by)
       
       # 收集所有資料
       data = {
           'user': user.to_dict(include_sensitive=True),
           'applications': [a.to_dict() for a in user.applications],
           'rehomes': [r.to_dict() for r in user.rehomes],
           'notifications': [n.to_dict() for n in user.notifications]
       }
       
       # 儲存到 S3/MinIO
       file_url = upload_json_to_storage(data, f'exports/user_{user.user_id}.json')
       
       # 發送 email 通知
       email_service.send_data_export_email(user.email, file_url)
       
       job.status = JobStatus.SUCCEEDED
       job.result_summary = {'file_url': file_url}
       db.session.commit()
   \\\

3. **前端 UI** (UserProfile.vue 新增 Tab)
   - 「帳號管理」Tab 加入:
     * 匯出個資按鈕
     * 刪除帳號按鈕(顯示警告對話框)

#### 實作步驟:
1. 🔧 新增後端 API (users.py)
2. 🔧 實作 Celery Worker (user_tasks.py)
3. 🎨 前端 UI 整合(UserProfile.vue)
4. ✅ 測試匯出與刪除流程
5. 📝 更新測試文件

---

### 📋 #5: Email 驗證結果頁面
**預計時間:** 1 小時
**完成度:** 50%
**用戶價值:** ⭐⭐⭐

#### 需要實作的功能:
1. **EmailVerification.vue**
   - 🔧 功能需求:
     * 自動從 URL 讀取 token
     * 呼叫 GET /api/auth/verify?token=...
     * 顯示驗證成功/失敗畫面
     * 3秒後自動跳轉登入頁
   
   - 📝 API 端點:
     * GET /api/auth/verify?token=... (已存在)
   
   - 🎨 UI 設計:
     * 載入中:Spinner
     * 成功:綠色勾勾 + 「Email 驗證成功」
     * 失敗:紅色叉叉 + 錯誤訊息 + 重發按鈕

2. **路由配置**
   \\\	ypescript
   {
     path: '/verify-email',
     name: 'EmailVerification',
     component: () => import('@/pages/EmailVerification.vue'),
     meta: { title: 'Email 驗證' }
   }
   \\\

#### 實作步驟:
1. �� 建立 EmailVerification.vue
2. 🔗 配置路由
3. ✅ 測試驗證流程
4. 📝 更新 PHASE4_TEST_GUIDE.md

---

## 🎯 優先級 P3 - 進階功能 (3項)

### 📋 #6: Jobs 測試文件
**預計時間:** 30 分鐘
**用戶價值:** ⭐⭐

#### 需要實作:
- 📝 建立 \PHASE9_TEST_GUIDE.md\
  * 測試背景任務狀態查詢
  * 測試 Retry/Cancel 功能
  * 測試自動刷新機制
  * 角色權限測試(ADMIN, SHELTER_MEMBER)

---

### 📋 #7: 建立 SHELTER_MEMBER 測試帳號
**預計時間:** 5 分鐘
**用戶價值:** ⭐⭐

#### SQL 指令:
\\\sql
-- 1. 建立 shelter_member 角色測試帳號
INSERT INTO users (email, password_hash, username, first_name, last_name, role, verified) 
VALUES (
  'shelter@test.com',
  -- 密碼: Shelter123
  '\\\',
  'shelter_tester',
  'Shelter',
  'Tester',
  'SHELTER_MEMBER',
  1
);

-- 2. 建立對應的 shelter 記錄
INSERT INTO shelters (name, address, phone_number, email, verified, created_by)
VALUES (
  '測試收容所',
  '台北市測試區測試路123號',
  '02-12345678',
  'shelter@test.com',
  1,
  (SELECT user_id FROM users WHERE email='shelter@test.com')
);
\\\

#### 更新文件:
- 📝 更新 TEST_ACCOUNTS.md
  * 新增 shelter@test.com 帳號說明
  * 新增收容所管理測試場景

---

### 📋 #8: Celery Worker 完整實作
**預計時間:** 4-5 小時
**用戶價值:** ⭐⭐⭐⭐

#### 需要實作的 Worker:
1. **Animal Batch Import Worker**
   \\\python
   # backend/app/tasks/animal_tasks.py
   @celery.task(bind=True)
   def process_animal_batch_import(self, job_id):
       \"\"\"處理動物批次匯入\"\"\"
       # 1. 下載 CSV from S3
       # 2. 驗證資料格式
       # 3. 批次插入
       # 4. 更新 Job 狀態
   \\\

2. **Email Async Workers**
   \\\python
   # backend/app/tasks/email_tasks.py
   @celery.task
   def send_verification_email_async(user_email, username, token):
       email_service.send_verification_email(user_email, username, token)
   
   @celery.task
   def send_password_reset_email_async(user_email, username, token):
       email_service.send_password_reset_email(user_email, username, token)
   \\\

3. **Data Export Worker** (GDPR)
   - 已在 #4 說明

#### 實作步驟:
1. 🔧 建立 tasks/ 目錄結構
2. 🔧 實作各個 worker
3. 🔧 修改現有 API 改用 .delay() 呼叫
4. ✅ 測試非同步執行
5. 📝 撰寫 worker 文件

---

## 📊 實作建議順序

### Week 1: 高價值 UI (用戶可見)
1. **Day 1-2**: 收容所管理頁面 (#1)
2. **Day 3**: 審計日誌頁面 (#2)
3. **Day 4**: 用戶個人資料頁面 (#3)
4. **Day 5**: Email 驗證頁面 (#5)

### Week 2: 進階功能 & 後端強化
1. **Day 1-2**: GDPR 功能 (#4)
2. **Day 3-4**: Celery Worker 實作 (#8)
3. **Day 5**: 測試文件補齊 (#6, #7)

---

## 🎯 快速勝利項目 (Quick Wins)
以下項目可優先完成以快速提升完成度:

1. ✅ **建立 SHELTER_MEMBER 測試帳號** (5 min) - #7
2. ✅ **EmailVerification.vue** (1 hr) - #5
3. ✅ **PHASE9_TEST_GUIDE.md** (30 min) - #6

---

## 📈 預期結果

完成上述所有項目後:
- 📊 整體完成度: 90%  **98%**
- 🎨 前端完成度: 62%  **95%**
- ⚙️ 後端完成度: 85%  **95%**
- ✅ 測試文件: 60%  **90%**

---

## 🚀 下一步行動

請選擇您想優先實作的項目:

**快速選項:**
- 輸入 \1\  收容所管理頁面
- 輸入 \2\  審計日誌頁面
- 輸入 \3\  用戶個人資料頁面
- 輸入 \4\  GDPR 功能
- 輸入 \5\  Email 驗證頁面
- 輸入 \quick\  執行快速勝利項目(#5,#6,#7)
- 輸入 \ll\  按照建議順序全部實作

---
生成完畢! 🎉
