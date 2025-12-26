# 整合測試計劃 - 收容所管理系統 (Shelter)

## test_shelter_integration.py - 收容所管理整合測試

### TestShelterCreate - 收容所創建測試類

**測試編號：IT-SHELTER-001**

**測試目標**：驗證創建收容所需要認證  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 發送 POST 請求嘗試創建收容所
3. 驗證返回 401 Unauthorized 錯誤

**測試角色**：訪客（未登入）  
**測試流程**：
- 準備收容所資料：
  ```json
  {
    "name": "未認證收容所",
    "contact_email": "test@test.com",
    "contact_phone": "02-1111-1111",
    "address": {
      "city": "台北市"
    }
  }
  ```
- 發送 `POST /api/shelters` 帶 data=json 但不帶認證 headers
- 驗證 response.status_code == 401

**測試結果**：✅ 通過

---

### TestShelterList - 收容所列表測試類

**測試編號：IT-SHELTER-002**

**測試目標**：驗證獲取已驗證的收容所列表  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 確保測試收容所已驗證
2. 發送 GET 請求到 `/api/shelters`
3. 驗證返回的所有收容所都是已驗證狀態

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備測試收容所和認證標頭（test_shelter, auth_headers）
- 設置收容所為已驗證：
  ```python
  test_shelter.verified = True
  db_session.commit()
  ```
- 發送 `GET /api/shelters` 帶 headers=auth_headers
- 驗證 response.status_code == 200
- 驗證 'shelters' in data
- 驗證 len(data['shelters']) > 0
- 遍歷所有收容所驗證 shelter['verified'] == True

**測試結果**：✅ 通過

---

**測試編號：IT-SHELTER-003**

**測試目標**：驗證按地區篩選收容所功能  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 發送帶地區篩選參數的 GET 請求到 `/api/shelters?region=台北`
2. 驗證返回的收容所符合地區條件

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備認證標頭
- 發送 `GET /api/shelters?region=台北` 帶 headers=auth_headers
- 驗證 response.status_code == 200
- 驗證 'shelters' in data

**測試結果**：✅ 通過

---

**測試編號：IT-SHELTER-004**

**測試目標**：驗證收容所列表分頁功能  
**測試方法**：邊界值分析 (Boundary Value Analysis)  
**測試步驟**：
1. 發送帶分頁參數的 GET 請求到 `/api/shelters?page=1&per_page=10`
2. 驗證回應包含分頁資訊

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備認證標頭
- 發送 `GET /api/shelters?page=1&per_page=10` 帶 headers=auth_headers
- 驗證 response.status_code == 200
- 驗證 'shelters' in data
- 驗證 'total' in data
- 驗證 'page' in data
- 驗證 'per_page' in data

**測試結果**：✅ 通過

---

### TestShelterDetail - 收容所詳情測試類

**測試編號：IT-SHELTER-005**

**測試目標**：驗證獲取收容所詳情  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 確保測試收容所已驗證
2. 發送 GET 請求到 `/api/shelters/{shelter_id}`
3. 驗證返回完整的收容所資訊

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備測試收容所和認證標頭（test_shelter, auth_headers）
- 設置收容所為已驗證：
  ```python
  test_shelter.verified = True
  db_session.commit()
  ```
- 發送 `GET /api/shelters/{test_shelter.shelter_id}` 帶 headers=auth_headers
- 驗證 response.status_code == 200
- 驗證 data['shelter_id'] == test_shelter.shelter_id
- 驗證 data['name'] == test_shelter.name

**測試結果**：✅ 通過

---

**測試編號：IT-SHELTER-006**

**測試目標**：驗證獲取不存在的收容所返回 404  
**測試方法**：邊界值分析 (Boundary Value Analysis)  
**測試步驟**：
1. 發送 GET 請求到不存在的收容所 ID
2. 驗證返回 404 Not Found 錯誤

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備認證標頭
- 發送 `GET /api/shelters/99999` 帶 headers=auth_headers
- 驗證 response.status_code == 404

**測試結果**：✅ 通過

---

### TestShelterUpdate - 收容所更新測試類

**測試編號：IT-SHELTER-007**

**測試目標**：驗證非收容所成員無法更新收容所資料  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 使用非收容所成員的認證 Token
2. 嘗試更新收容所資料
3. 驗證返回 403 Forbidden 錯誤

**測試角色**：非收容所成員的已登入用戶  
**測試流程**：
- Fixture 準備測試收容所和普通用戶認證標頭（test_shelter, auth_headers）
- 準備更新資料：
  ```json
  {
    "description": "試圖更新"
  }
  ```
- 發送 `PATCH /api/shelters/{test_shelter.shelter_id}` 帶 data=json 和 headers=auth_headers
- 驗證 response.status_code == 403

**測試結果**：✅ 通過

---

### TestShelterVerification - 收容所驗證測試類

**測試編號：IT-SHELTER-008**

**測試目標**：驗證管理員可以驗證收容所  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 使用管理員認證 Token
2. 發送驗證請求（verified=True）
3. 驗證收容所狀態更新為已驗證

**測試角色**：系統管理員  
**測試流程**：
- Fixture 準備測試收容所和管理員認證標頭（test_shelter, admin_headers）
- 準備驗證資料：
  ```json
  {
    "verified": true,
    "notes": "資料完整，已驗證"
  }
  ```
- 發送 `POST /api/shelters/{test_shelter.shelter_id}/verify` 帶 data=json 和 headers=admin_headers
- 驗證 response.status_code == 200
- 刷新資料庫記錄：db_session.refresh(test_shelter)
- 驗證 test_shelter.verified == True

**測試結果**：✅ 通過

---

**測試編號：IT-SHELTER-009**

**測試目標**：驗證管理員可以拒絕驗證收容所  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 使用管理員認證 Token
2. 發送拒絕驗證請求（verified=False）
3. 驗證收容所狀態保持未驗證

**測試角色**：系統管理員  
**測試流程**：
- Fixture 準備測試收容所和管理員認證標頭（test_shelter, admin_headers）
- 準備拒絕驗證資料：
  ```json
  {
    "verified": false,
    "notes": "資料不完整"
  }
  ```
- 發送 `POST /api/shelters/{test_shelter.shelter_id}/verify` 帶 data=json 和 headers=admin_headers
- 驗證 response.status_code == 200
- 刷新資料庫記錄：db_session.refresh(test_shelter)
- 驗證 test_shelter.verified == False

**測試結果**：✅ 通過

---

**測試編號：IT-SHELTER-010**

**測試目標**：驗證非管理員無法驗證收容所  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 使用普通用戶認證 Token
2. 嘗試驗證收容所
3. 驗證返回 403 Forbidden 錯誤

**測試角色**：普通用戶  
**測試流程**：
- Fixture 準備測試收容所和普通用戶認證標頭（test_shelter, auth_headers）
- 準備驗證資料：
  ```json
  {
    "verified": true
  }
  ```
- 發送 `POST /api/shelters/{test_shelter.shelter_id}/verify` 帶 data=json 和 headers=auth_headers
- 驗證 response.status_code == 403

**測試結果**：✅ 通過

---

## 📊 Shelter 模組測試統計

- **總測試數**：10 個
- **通過測試**：10 個 ✅ (100%)
- **失敗測試**：0 個
- **跳過測試**：0 個 ⏭️
- **已註解測試**：0 個 💤

**測試覆蓋範圍**：
- ✅ 收容所創建（含認證檢查）
- ✅ 收容所列表查詢（含分頁、地區篩選）
- ✅ 收容所詳情查詢
- ✅ 收容所資料更新（含權限檢查）
- ✅ 收容所驗證流程（管理員審核）
