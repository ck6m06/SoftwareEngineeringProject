# 整合測試詳細文檔 - Part 4: Medical Records Integration Tests

## test_medical_integration.py - 醫療記錄整合測試（12 個測試）

---

### TestMedicalRecordCreate - 創建醫療記錄測試類

**測試編號：IT-MEDICAL-001**

**測試目標**：驗證非收容所員工無法創建醫療記錄  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 使用一般用戶的 Token
2. 嘗試創建醫療記錄
3. 驗證返回 403 Forbidden

**測試角色**：一般會員  
**測試流程**：
- Fixture 準備：
  - `auth_headers` - 一般用戶的認證標頭
  - `test_shelter_animal` - 收容所動物
- Request Payload：
  ```json
  {
    "record_type": "CHECKUP",
    "date": "2024-01-15",
    "provider": "測試醫院",
    "details": "測試創建"
  }
  ```
- HTTP 請求：`POST /api/medical-records/animals/{test_shelter_animal.animal_id}/medical-records` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 403`
- 預期行為：一般用戶無權限創建醫療記錄

**測試結果**：✅ 通過

---

**測試編號：IT-MEDICAL-002**

**測試目標**：驗證為不存在的動物創建醫療記錄返回 404  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 使用不存在的 animal_id（99999）
2. 嘗試創建醫療記錄
3. 驗證返回 404 Not Found

**測試角色**：收容所員工  
**測試流程**：
- Request Payload：
  ```json
  {
    "record_type": "CHECKUP",
    "date": "2024-01-15",
    "provider": "測試醫院",
    "details": "測試"
  }
  ```
- HTTP 請求：`POST /api/medical-records/animals/99999/medical-records` with headers
- 驗證斷言：
  - `assert response.status_code == 404`
- 預期行為：找不到動物，返回 404 錯誤

**測試結果**：✅ 通過

---

### TestMedicalRecordList - 醫療記錄列表測試類

**測試編號：IT-MEDICAL-003**

**測試目標**：驗證獲取動物的醫療記錄列表  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 創建測試醫療記錄
2. 發送 GET 請求獲取列表
3. 驗證返回包含醫療記錄

**測試角色**：已登入用戶  
**測試流程**：
- 測試資料準備：
  ```python
  record = MedicalRecord(
      medical_record_id=200,
      animal_id=test_shelter_animal.animal_id,
      record_type=RecordType.CHECKUP,
      date=date(2024, 1, 15),
      provider='測試醫院',
      details='測試記錄',
      verified=True,
      verified_by=test_shelter_member.user_id
  )
  db_session.add(record)
  db_session.commit()
  ```
- HTTP 請求：`GET /api/medical-records/animals/{test_shelter_animal.animal_id}/medical-records` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'medical_records' in data`
  - `assert len(data['medical_records']) > 0`
- 預期行為：返回動物的醫療記錄列表

**測試結果**：✅ 通過

---

**測試編號：IT-MEDICAL-004**

**測試目標**：驗證帶過濾條件的醫療記錄列表  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 record_type 查詢參數
2. 發送 GET 請求
3. 驗證返回的記錄符合指定類型

**測試角色**：已登入用戶  
**測試流程**：
- HTTP 請求：`GET /api/medical-records/animals/{test_shelter_animal.animal_id}/medical-records?record_type=VACCINE` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'medical_records' in data`
- 預期行為：返回指定類型的醫療記錄

**測試結果**：✅ 通過

---

**測試編號：IT-MEDICAL-005**

**測試目標**：驗證只顯示已驗證的醫療記錄  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 verified=true 查詢參數
2. 發送 GET 請求
3. 驗證所有返回的記錄都已驗證

**測試角色**：已登入用戶  
**測試流程**：
- HTTP 請求：`GET /api/medical-records/animals/{test_shelter_animal.animal_id}/medical-records?verified=true` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'medical_records' in data`
  - `for record in data['medical_records']: assert record['verified'] == True`
- 預期行為：只返回已驗證的醫療記錄

**測試結果**：✅ 通過

---

### TestMedicalRecordUpdate - 醫療記錄更新測試類

**測試編號：IT-MEDICAL-006**

**測試目標**：驗證24小時內可以更新醫療記錄  
**測試方法**：邊界值分析 (Boundary Value Analysis)  
**測試步驟**：
1. 創建剛創建的醫療記錄（created_at=now）
2. 使用收容所員工的 Token 發送 PATCH 請求
3. 驗證記錄更新成功

**測試角色**：收容所員工（記錄創建者）  
**測試流程**：
- 測試資料準備：
  ```python
  from app.utils.datetime_helper import get_naive_taipei_now
  
  record = MedicalRecord(
      medical_record_id=202,
      animal_id=test_shelter_animal.animal_id,
      record_type=RecordType.CHECKUP,
      date=date(2024, 1, 15),
      provider='原醫院',
      details='原記錄',
      verified=False,
      created_at=get_naive_taipei_now()
  )
  db_session.add(record)
  db_session.commit()
  ```
- Request Payload：
  ```json
  {
    "details": "更新後的詳細信息",
    "provider": "更新後醫院"
  }
  ```
- HTTP 請求：`PATCH /api/medical-records/{record.medical_record_id}` with headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'medical_record' in data`
  - `assert data['medical_record']['details'] == '更新後的詳細信息'`
- 資料庫驗證：
  - `db_session.refresh(record)`
  - `assert record.provider == '更新後醫院'`
- 預期行為：24小時內可以更新記錄

**測試結果**：✅ 通過

---
