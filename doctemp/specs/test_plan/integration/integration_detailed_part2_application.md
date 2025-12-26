# 整合測試詳細文檔 - Part 2: Application Integration Tests

## test_application_integration.py - 領養申請整合測試（12 個測試）

---

### TestApplicationCreate - 創建領養申請測試類

**測試編號：IT-APPLICATION-001**

**測試目標**：驗證用戶成功創建領養申請  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 創建申請人用戶（不同於動物擁有者）
2. 準備領養申請資料
3. 使用申請人的 Token 發送 POST 請求
4. 驗證申請創建成功且狀態為 PENDING

**測試角色**：已登入用戶（申請人）  
**測試流程**：
- 測試資料準備：
  ```python
  applicant = User(
      email='applicant@test.com',
      username='applicant',
      password_hash=hash_password('Password123'),
      role=UserRole.GENERAL_MEMBER,
      verified=True
  )
  db_session.add(applicant)
  db_session.commit()
  
  applicant_token = create_access_token(identity=applicant.user_id)
  applicant_headers = {
      'Authorization': f'Bearer {applicant_token}',
      'Content-Type': 'application/json'
  }
  ```
- Request Payload：
  ```json
  {
    "animal_id": 1,
    "type": "ADOPTION",
    "contact_phone": "0912345678",
    "contact_address": "台北市中正區",
    "occupation": "工程師",
    "housing_type": "公寓",
    "has_experience": true,
    "reason": "想要給動物一個溫暖的家"
  }
  ```
- HTTP 請求：`POST /api/applications` with headers=applicant_headers
- 驗證斷言：
  - `assert response.status_code == 201`
  - `assert 'application' in data`
  - `assert application_data['animal_id'] == test_animal.animal_id`
  - `assert application_data['applicant_id'] == applicant.user_id`
  - `assert application_data['type'] == 'ADOPTION'`
  - `assert application_data['status'] == 'PENDING'`
- 資料庫驗證：
  - 查詢 Application 表確認記錄存在
  - 驗證 contact_phone == '0912345678'
- 預期行為：成功創建領養申請

**測試結果**：✅ 通過

---

**測試編號：IT-APPLICATION-002**

**測試目標**：驗證未認證用戶無法創建申請  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 嘗試創建領養申請
3. 驗證返回 401 Unauthorized

**測試角色**：訪客（未登入）  
**測試流程**：
- Request Payload：
  ```json
  {
    "animal_id": 1,
    "type": "ADOPTION"
  }
  ```
- HTTP 請求：`POST /api/applications` with content_type='application/json'（無 auth headers）
- 驗證斷言：
  - `assert response.status_code == 401`
- 預期行為：未登入無法創建申請

**測試結果**：✅ 通過

---

**測試編號：IT-APPLICATION-003**

**測試目標**：驗證為不存在的動物創建申請返回 404  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 提供不存在的 animal_id（999999）
2. 嘗試創建申請
3. 驗證返回 404 Not Found

**測試角色**：已登入用戶  
**測試流程**：
- Request Payload：
  ```json
  {
    "animal_id": 999999,
    "type": "ADOPTION"
  }
  ```
- HTTP 請求：`POST /api/applications` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 404`
- 預期行為：找不到動物，返回 404 錯誤

**測試結果**：✅ 通過

---

**測試編號：IT-APPLICATION-004**

**測試目標**：驗證無法創建重複申請  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 創建第一個申請
2. 嘗試用相同用戶和動物創建第二個申請
3. 驗證返回 409 Conflict

**測試角色**：已登入用戶（申請人）  
**測試流程**：
- 測試資料準備：
  ```python
  applicant = User(
      email='applicant_dup@test.com',
      username='applicant_dup',
      password_hash=hash_password('Password123'),
      role=UserRole.GENERAL_MEMBER,
      verified=True
  )
  db_session.add(applicant)
  db_session.commit()
  
  application = Application(
      application_id=100,
      applicant_id=applicant.user_id,
      animal_id=test_animal.animal_id,
      type=ApplicationType.ADOPTION,
      status=ApplicationStatus.PENDING
  )
  db_session.add(application)
  db_session.commit()
  
  applicant_token = create_access_token(identity=applicant.user_id)
  applicant_headers = {
      'Authorization': f'Bearer {applicant_token}',
      'Content-Type': 'application/json'
  }
  ```
- Request Payload：
  ```json
  {
    "animal_id": 1,
    "type": "ADOPTION",
    "contact_phone": "0912345678",
    "contact_address": "台北市",
    "reason": "想領養"
  }
  ```
- HTTP 請求：`POST /api/applications` with headers=applicant_headers
- 驗證斷言：
  - `assert response.status_code == 409`
- 預期行為：檢測到重複申請，返回 409 錯誤

**測試結果**：✅ 通過

---

### TestApplicationList - 申請列表測試類

**測試編號：IT-APPLICATION-005**

**測試目標**：驗證獲取我的申請列表  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 創建測試申請
2. 使用申請人的 Token 發送 GET 請求
3. 驗證返回的申請列表包含該申請

**測試角色**：已登入用戶（申請人）  
**測試流程**：
- 測試資料準備：
  ```python
  application = Application(
      application_id=101,
      applicant_id=test_user.user_id,
      animal_id=test_animal.animal_id,
      type=ApplicationType.ADOPTION,
      status=ApplicationStatus.PENDING
  )
  db_session.add(application)
  db_session.commit()
  ```
- HTTP 請求：`GET /api/applications` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'items' in data`
  - `assert len(data['items']) > 0`
  - `assert data['items'][0]['applicant_id'] == test_user.user_id`
- 預期行為：返回當前用戶的所有申請

**測試結果**：✅ 通過

---

**測試編號：IT-APPLICATION-006**

**測試目標**：驗證按狀態篩選申請列表  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 創建不同狀態的申請
2. 提供 status 查詢參數
3. 驗證返回的申請都符合指定狀態

**測試角色**：已登入用戶  
**測試流程**：
- 測試資料準備：
  ```python
  app1 = Application(
      application_id=102,
      applicant_id=test_user.user_id,
      animal_id=test_animal.animal_id,
      type=ApplicationType.ADOPTION,
      status=ApplicationStatus.PENDING
  )
  db_session.add(app1)
  db_session.commit()
  ```
- HTTP 請求：`GET /api/applications?status=PENDING` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'items' in data`
  - `for app in data['items']: assert app['status'] == 'PENDING'`
- 預期行為：只返回 PENDING 狀態的申請

**測試結果**：✅ 通過

---

### TestApplicationReview - 申請審核測試類

**測試編號：IT-APPLICATION-007**

**測試目標**：驗證動物擁有者批准申請  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 創建申請人和申請記錄
2. 使用動物擁有者的 Token 發送審核請求
3. 驗證申請狀態變更為 APPROVED

**測試角色**：動物擁有者  
**測試流程**：
- 測試資料準備：
  ```python
  applicant = User(
      email='applicant@test.com',
      username='applicant',
      password_hash=hash_password('Password123'),
      role=UserRole.GENERAL_MEMBER,
      verified=True
  )
  db_session.add(applicant)
  db_session.commit()
  
  application = Application(
      application_id=103,
      applicant_id=applicant.user_id,
      animal_id=test_animal.animal_id,
      type=ApplicationType.ADOPTION,
      status=ApplicationStatus.PENDING
  )
  db_session.add(application)
  db_session.commit()
  ```
- Request Payload：
  ```json
  {
    "action": "approve",
    "review_notes": "申請通過"
  }
  ```
- HTTP 請求：`POST /api/applications/{application.application_id}/review` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'application' in data or 'status' in data`
  - `app_status = data.get('application', {}).get('status') or data.get('status')`
  - `assert app_status == 'APPROVED'`
- 資料庫驗證：
  - `db_session.refresh(application)`
  - `assert application.status == ApplicationStatus.APPROVED`
  - `assert application.review_notes == '申請通過'`
- 預期行為：申請狀態變更為 APPROVED

**測試結果**：✅ 通過

---

**測試編號：IT-APPLICATION-008**

**測試目標**：驗證動物擁有者拒絕申請並提供原因  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 創建申請人和申請記錄
2. 使用動物擁有者的 Token 發送拒絕請求
3. 驗證申請狀態變更為 REJECTED 且記錄原因

**測試角色**：動物擁有者  
**測試流程**：
- 測試資料準備：（同 IT-APPLICATION-007，但使用不同 application_id）
- Request Payload：
  ```json
  {
    "action": "reject",
    "review_notes": "申請條件不符"
  }
  ```
- HTTP 請求：`POST /api/applications/{application.application_id}/review` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - 驗證 status == 'REJECTED'
- 資料庫驗證：
  - `assert application.status == ApplicationStatus.REJECTED`
  - `assert application.review_notes == '申請條件不符'`
- 預期行為：申請狀態變更為 REJECTED 並記錄原因

**測試結果**：✅ 通過

---

**測試編號：IT-APPLICATION-009**

**測試目標**：驗證無權限用戶無法審核申請  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 創建申請記錄
2. 使用非擁有者的 Token 嘗試審核
3. 驗證返回 403 Forbidden

**測試角色**：非動物擁有者  
**測試流程**：
- 測試資料準備：創建其他用戶的申請
- Request Payload：
  ```json
  {
    "action": "approve",
    "review_notes": "嘗試審核"
  }
  ```
- HTTP 請求：`POST /api/applications/{application.application_id}/review` with headers=auth_headers（非擁有者）
- 驗證斷言：
  - `assert response.status_code == 403`
- 預期行為：無權限審核，返回 403 錯誤

**測試結果**：✅ 通過

---

### TestApplicationDetail - 申請詳情測試類

**測試編號：IT-APPLICATION-010**

**測試目標**：驗證申請人可以獲取自己的申請詳情  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 創建申請記錄
2. 使用申請人的 Token 發送 GET 請求
3. 驗證返回申請的完整資訊

**測試角色**：申請人  
**測試流程**：
- 測試資料準備：創建申請記錄（applicant_id=test_user.user_id）
- HTTP 請求：`GET /api/applications/{application.application_id}` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert data['application_id'] == application.application_id`
  - `assert data['applicant_id'] == test_user.user_id`
- 預期行為：返回完整的申請詳情

**測試結果**：✅ 通過

---

**測試編號：IT-APPLICATION-011**

**測試目標**：驗證動物擁有者可以查看申請詳情  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 創建申請記錄
2. 使用動物擁有者的 Token 發送 GET 請求
3. 驗證可以獲取申請詳情

**測試角色**：動物擁有者  
**測試流程**：
- 測試資料準備：創建其他用戶的申請（針對 test_user 擁有的動物）
- HTTP 請求：`GET /api/applications/{application.application_id}` with headers=auth_headers（動物擁有者）
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert data['application_id'] == application.application_id`
- 預期行為：動物擁有者可以查看針對其動物的申請

**測試結果**：✅ 通過

---

**測試編號：IT-APPLICATION-012**

**測試目標**：驗證無權限用戶無法查看申請詳情  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 創建申請記錄
2. 使用無關用戶的 Token 嘗試查看
3. 驗證返回 403 Forbidden

**測試角色**：無關用戶  
**測試流程**：
- 測試資料準備：創建其他用戶的申請（針對其他用戶的動物）
- HTTP 請求：`GET /api/applications/{application.application_id}` with headers=auth_headers（無關用戶）
- 驗證斷言：
  - `assert response.status_code == 403`
- 預期行為：無權限查看，返回 403 錯誤

**測試結果**：✅ 通過

---
