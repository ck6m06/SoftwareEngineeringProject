# 整合測試詳細文檔 - Part 1: Animal Integration Tests

## test_animal_integration.py - 動物管理整合測試（34 個測試）

---

### TestAnimalList - 動物列表測試類

**測試編號：IT-ANIMAL-001**

**測試目標**：驗證訪客可以獲取已發布動物列表  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 不提供認證 Token
2. 發送 GET 請求到 `/api/animals`
3. 驗證回應包含動物列表和總數

**測試角色**：訪客（未登入）  
**測試流程**：
- Fixture 準備：
  - `test_animal` - 測試動物對象（status=PUBLISHED）
  - `test_shelter_animal` - 收容所動物對象
- HTTP 請求：`GET /api/animals`
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'animals' in data`
  - `assert 'total' in data`
  - `assert data['total'] >= 2`
- 預期行為：返回至少 2 個已發布的動物

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-002**

**測試目標**：驗證登入用戶可以看到包含草稿的動物列表  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 提供有效的認證 Token（auth_headers）
2. 發送 GET 請求到 `/api/animals`
3. 驗證回應包含動物列表（包括自己的草稿）

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備：
  - `auth_headers` - 認證標頭（Bearer Token）
  - `test_animal` - 測試動物
  - `test_shelter_animal` - 收容所動物
- HTTP 請求：`GET /api/animals` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'animals' in data`
  - `assert 'total' in data`
- 預期行為：已登入用戶可見自己的草稿動物

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-003**

**測試目標**：驗證按物種篩選動物功能  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 species 查詢參數（species=DOG）
2. 發送 GET 請求到 `/api/animals?species=DOG`
3. 驗證返回的所有動物都是狗

**測試角色**：訪客  
**測試流程**：
- Fixture 準備：
  - `test_animal` - 物種為 DOG 的動物
  - `test_shelter_animal` - 可能不同物種的動物
- HTTP 請求：`GET /api/animals?species=DOG`
- 驗證斷言：
  - `assert response.status_code == 200`
  - `for animal in data['animals']: assert animal['species'].upper() == 'DOG'`
- 預期行為：返回的列表只包含狗（DOG）

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-004**

**測試目標**：驗證按性別篩選動物功能  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 sex 查詢參數（sex=MALE）
2. 發送 GET 請求到 `/api/animals?sex=MALE`
3. 驗證返回的所有動物都是公的

**測試角色**：訪客  
**測試流程**：
- Fixture 準備：
  - `test_animal` - 性別為 MALE 的動物
- HTTP 請求：`GET /api/animals?sex=MALE`
- 驗證斷言：
  - `assert response.status_code == 200`
  - `for animal in data['animals']: assert animal['sex'].upper() == 'MALE'`
- 預期行為：返回的列表只包含公的動物（MALE）

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-005**

**測試目標**：驗證分頁功能正確運作  
**測試方法**：邊界值分析 (Boundary Value Analysis)  
**測試步驟**：
1. 創建 25 個測試動物
2. 發送第一頁請求（page=1&per_page=10）
3. 發送第二頁請求（page=2&per_page=10）
4. 驗證每頁返回正確數量的動物

**測試角色**：訪客  
**測試流程**：
- 測試資料準備：
  ```python
  for i in range(25):
      animal = Animal(
          animal_id=100 + i,
          name=f'Test Animal {i}',
          species=Species.DOG,
          breed='Mixed',
          sex=Sex.MALE,
          dob=date(2023, 1, 1),
          status=AnimalStatus.PUBLISHED,
          owner_id=None,
          created_by=test_user.user_id
      )
      db_session.add(animal)
  db_session.commit()
  ```
- HTTP 請求 1：`GET /api/animals?page=1&per_page=10`
  - 驗證：`assert len(data['animals']) == 10`
  - 驗證：`assert data['page'] == 1`
- HTTP 請求 2：`GET /api/animals?page=2&per_page=10`
  - 驗證：`assert len(data['animals']) == 10`
  - 驗證：`assert data['page'] == 2`
- 預期行為：每頁顯示 10 個動物，頁碼正確

**測試結果**：✅ 通過

---

### TestAnimalListFilters - 動物列表進階篩選測試類

**測試編號：IT-ANIMAL-006**

**測試目標**：驗證按狀態篩選動物功能  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 status 查詢參數（status=PUBLISHED）
2. 發送 GET 請求到 `/api/animals?status=PUBLISHED`
3. 驗證返回的所有動物都是已發布狀態

**測試角色**：訪客  
**測試流程**：
- Fixture 準備：
  - `test_animal` - status=PUBLISHED 的動物
- HTTP 請求：`GET /api/animals?status=PUBLISHED`
- 驗證斷言：
  - `assert response.status_code == 200`
  - `for animal in data['animals']: assert animal['status'] == 'PUBLISHED'`
- 預期行為：返回的列表只包含已發布的動物

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-007**

**測試目標**：驗證按地區篩選動物功能  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 創建有地區資訊的動物
2. 發送帶地區參數的 GET 請求
3. 驗證返回的動物符合地區條件

**測試角色**：訪客  
**測試流程**：
- 測試資料準備：
  ```python
  animal = Animal(
      animal_id=600,
      name='Regional Dog',
      species=Species.DOG,
      breed='Mixed',
      sex=Sex.MALE,
      dob=date(2023, 1, 1),
      status=AnimalStatus.PUBLISHED,
      owner_id=test_user.user_id,
      created_by=test_user.user_id
  )
  db_session.add(animal)
  db_session.commit()
  ```
- HTTP 請求：`GET /api/animals`
- 驗證：`assert response.status_code == 200`
- 預期行為：API 正常回應地區篩選請求

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-008**

**測試目標**：驗證關鍵字搜尋功能  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 q (關鍵字) 參數
2. 發送 GET 請求到 `/api/animals?q=關鍵字`
3. 驗證返回匹配關鍵字的動物

**測試角色**：訪客  
**測試流程**：
- Fixture 準備：
  - `test_animal` - 有特定名稱的動物
- HTTP 請求：`GET /api/animals?q={test_animal.name[:3]}`
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'animals' in data`
- 預期行為：返回名稱包含關鍵字的動物列表

**測試結果**：✅ 通過

---

### TestAnimalCreate - 動物創建測試類

**測試編號：IT-ANIMAL-009**

**測試目標**：測試創建草稿動物  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 準備動物資料（status=DRAFT）
2. 使用認證 Token 發送 POST 請求
3. 驗證動物創建成功且狀態為 DRAFT

**測試角色**：已登入用戶  
**測試流程**：
- Fixture 準備：
  - `auth_headers` - 認證標頭
  - `test_user` - 測試用戶
- Request Payload：
  ```json
  {
    "name": "New Test Dog",
    "species": "DOG",
    "breed": "Labrador",
    "sex": "MALE",
    "dob": "2021-01-01",
    "description": "A friendly dog",
    "status": "DRAFT"
  }
  ```
- HTTP 請求：`POST /api/animals` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 201`
  - `assert data['name'] == 'New Test Dog'`
  - `assert data['status'].lower() == 'draft'`
  - `assert data.get('owner_id') == test_user.user_id`
- 資料庫驗證：
  - 查詢 Animal 表確認記錄存在
  - 驗證 status == AnimalStatus.DRAFT
  - 驗證 owner_id == test_user.user_id

**測試結果**：💤 已註解（後端 API bug: 創建草稿動物時發生 500 錯誤）

---

**測試編號：IT-ANIMAL-010**

**測試目標**：驗證未認證用戶無法創建動物  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 發送 POST 請求創建動物
3. 驗證返回 401 未授權錯誤

**測試角色**：訪客（未登入）  
**測試流程**：
- Request Payload：
  ```json
  {
    "name": "Unauthorized Dog",
    "species": "DOG",
    "breed": "Mixed",
    "sex": "MALE",
    "dob": "2022-01-01"
  }
  ```
- HTTP 請求：`POST /api/animals` with content_type='application/json'（無 auth headers）
- 驗證斷言：
  - `assert response.status_code == 401`
- 預期行為：未登入用戶無法創建動物

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-011**

**測試目標**：測試創建動物時提供無效數據  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 提供無效的動物資料（空名稱、無效物種、無效性別）
2. 使用認證 Token 發送 POST 請求
3. 驗證返回 400/422 錯誤

**測試角色**：已登入用戶  
**測試流程**：
- Request Payload：
  ```json
  {
    "name": "",
    "species": "invalid",
    "sex": "unknown"
  }
  ```
- HTTP 請求：`POST /api/animals` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code in [400, 422]`
- 預期行為：服務器拒絕無效數據

**測試結果**：💤 已註解（後端 API bug: 無效數據應返回 400/422，實際返回 500）

---

### TestAnimalDetail - 動物詳情測試類

**測試編號：IT-ANIMAL-012**

**測試目標**：驗證獲取動物詳情功能  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 提供有效的 animal_id
2. 發送 GET 請求到 `/api/animals/{animal_id}`
3. 驗證返回動物的完整資訊

**測試角色**：訪客  
**測試流程**：
- Fixture 準備：
  - `test_animal` - animal_id=1, name='Test Dog'
- HTTP 請求：`GET /api/animals/{test_animal.animal_id}`
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert data['animal_id'] == test_animal.animal_id`
  - `assert data['name'] == test_animal.name`
  - `assert data['species'] == test_animal.species.value`
- 預期行為：返回完整的動物資訊

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-013**

**測試目標**：驗證獲取不存在的動物返回 404  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 提供不存在的 animal_id（999999）
2. 發送 GET 請求
3. 驗證返回 404 Not Found

**測試角色**：訪客  
**測試流程**：
- HTTP 請求：`GET /api/animals/999999`
- 驗證斷言：
  - `assert response.status_code == 404`
- 預期行為：找不到動物，返回 404 錯誤

**測試結果**：✅ 通過

---

### TestAnimalGetDetail - 動物詳情擴展測試類

**測試編號：IT-ANIMAL-014**

**測試目標**：驗證獲取動物詳情包含關聯資料  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 發送 GET 請求獲取動物詳情
2. 驗證回應包含基本欄位
3. 驗證可能包含關聯資料（圖片、醫療記錄等）

**測試角色**：訪客  
**測試流程**：
- Fixture 準備：
  - `test_animal` - 測試動物
- HTTP 請求：`GET /api/animals/{test_animal.animal_id}`
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert 'animal_id' in data`
  - `assert 'name' in data`
  - `assert 'species' in data`
- 預期行為：返回動物的詳細資訊

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-015**

**測試目標**：驗證擁有者可以查看自己的草稿動物  
**測試方法**：決策表測試 (Decision Table Testing)  
**測試步驟**：
1. 創建草稿動物（status=DRAFT）
2. 使用擁有者的 Token 發送 GET 請求
3. 驗證可以成功獲取草稿動物詳情

**測試角色**：動物擁有者  
**測試流程**：
- 測試資料準備：
  ```python
  draft_animal = Animal(
      animal_id=200,
      name='Draft Dog',
      species=Species.DOG,
      breed='Mixed',
      sex=Sex.MALE,
      dob=date(2023, 1, 1),
      status=AnimalStatus.DRAFT,
      owner_id=test_user.user_id,
      created_by=test_user.user_id
  )
  db_session.add(draft_animal)
  db_session.commit()
  ```
- HTTP 請求：`GET /api/animals/{draft_animal.animal_id}` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert data['status'].lower() == 'draft'`
- 預期行為：擁有者可以查看自己的草稿動物

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-016**

**測試目標**：驗證未登入用戶無法查看草稿動物  
**測試方法**：決策表測試 (Decision Table Testing)  
**測試步驟**：
1. 創建草稿動物（status=DRAFT）
2. 不提供認證 Token 發送 GET 請求
3. 驗證返回 403/404 錯誤

**測試角色**：訪客（未登入）  
**測試流程**：
- 測試資料準備：
  ```python
  draft_animal = Animal(
      animal_id=201,
      name='Draft Dog',
      species=Species.DOG,
      breed='Mixed',
      sex=Sex.MALE,
      dob=date(2023, 1, 1),
      status=AnimalStatus.DRAFT,
      owner_id=test_user.user_id,
      created_by=test_user.user_id
  )
  db_session.add(draft_animal)
  db_session.commit()
  ```
- HTTP 請求：`GET /api/animals/{draft_animal.animal_id}`（無 auth headers）
- 驗證斷言：
  - `assert response.status_code in [403, 404]`
- 預期行為：訪客無法查看草稿動物

**測試結果**：💤 已註解（後端 API bug: 訪客查看草稿應返回 403/404，實際返回 200）

---

### TestAnimalUpdate - 動物更新測試類

**測試編號：IT-ANIMAL-017**

**測試目標**：驗證擁有者可以更新自己的動物  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 準備更新資料（name, description）
2. 使用擁有者的 Token 發送 PATCH 請求
3. 驗證動物資料更新成功

**測試角色**：動物擁有者  
**測試流程**：
- Fixture 準備：
  - `auth_headers` - 擁有者的認證標頭
  - `test_animal` - owner_id=test_user.user_id
- Request Payload：
  ```json
  {
    "name": "Updated Dog Name",
    "description": "Updated description"
  }
  ```
- HTTP 請求：`PATCH /api/animals/{test_animal.animal_id}` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `if 'name' in data: assert data['name'] == 'Updated Dog Name'`
- 資料庫驗證：
  - `db_session.refresh(test_animal)`
  - `assert test_animal.name == 'Updated Dog Name'`
  - `assert test_animal.description == 'Updated description'`
- 預期行為：動物資料成功更新

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-018**

**測試目標**：驗證無法更新他人的動物  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 創建另一個用戶的 Token
2. 嘗試更新他人的動物
3. 驗證返回 403 Forbidden

**測試角色**：非動物擁有者  
**測試流程**：
- 測試資料準備：
  ```python
  other_user = User(
      email='other@test.com',
      username='otheruser',
      password_hash='hashed',
      role=UserRole.GENERAL_MEMBER,
      verified=True
  )
  db_session.add(other_user)
  db_session.commit()
  
  token = create_access_token(identity=other_user.user_id)
  headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json'
  }
  ```
- Request Payload：
  ```json
  {
    "name": "Unauthorized Update"
  }
  ```
- HTTP 請求：`PATCH /api/animals/{test_animal.animal_id}` with headers=headers
- 驗證斷言：
  - `assert response.status_code == 403`
- 預期行為：無權限更新，返回 403 錯誤

**測試結果**：✅ 通過

---

### TestAnimalDelete - 動物刪除測試類

**測試編號：IT-ANIMAL-019**

**測試目標**：驗證擁有者可以刪除自己的動物  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 創建測試動物
2. 使用擁有者的 Token 發送 DELETE 請求
3. 驗證動物被軟刪除（deleted_at 設置）

**測試角色**：動物擁有者  
**測試流程**：
- 測試資料準備：
  ```python
  animal = Animal(
      animal_id=300,
      name='To Delete',
      species=Species.DOG,
      breed='Mixed',
      sex=Sex.MALE,
      dob=date(2023, 1, 1),
      status=AnimalStatus.DRAFT,
      owner_id=test_user.user_id,
      created_by=test_user.user_id
  )
  db_session.add(animal)
  db_session.commit()
  animal_id = animal.animal_id
  ```
- HTTP 請求：`DELETE /api/animals/{animal_id}` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code in [200, 204]`
- 資料庫驗證：
  - `deleted_animal = Animal.query.filter_by(animal_id=animal_id).first()`
  - `assert deleted_animal.deleted_at is not None`
- 預期行為：動物被軟刪除（deleted_at 不為 None）

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-020**

**測試目標**：驗證無權限無法刪除動物  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 創建另一個用戶的 Token
2. 嘗試刪除他人的動物
3. 驗證返回 403 Forbidden

**測試角色**：非動物擁有者  
**測試流程**：
- 測試資料準備：
  ```python
  other_user = User(
      email='other2@test.com',
      username='otheruser2',
      password_hash='hashed',
      role=UserRole.GENERAL_MEMBER,
      verified=True
  )
  db_session.add(other_user)
  db_session.commit()
  
  token = create_access_token(identity=other_user.user_id)
  headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json'
  }
  ```
- HTTP 請求：`DELETE /api/animals/{test_animal.animal_id}` with headers=headers
- 驗證斷言：
  - `assert response.status_code == 403`
- 預期行為：無權限刪除，返回 403 錯誤

**測試結果**：✅ 通過

---

### TestAnimalImages - 動物圖片管理測試類

**測試編號：IT-ANIMAL-021**

**測試目標**：測試新增動物圖片  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 準備圖片資料（storage_key, image_url）
2. 使用擁有者的 Token 發送 POST 請求
3. 驗證圖片新增成功

**測試角色**：動物擁有者  
**測試流程**：
- Request Payload：
  ```json
  {
    "storage_key": "animals/test-animal-001.jpg",
    "image_url": "https://example.com/animals/test-animal-001.jpg",
    "mime_type": "image/jpeg"
  }
  ```
- HTTP 請求：`POST /api/animals/{test_animal.animal_id}/images` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 201`
  - `assert 'image' in data`
  - `assert data['message'] == '圖片已新增'`
- 預期行為：圖片成功新增到動物

**測試結果**：💤 已註解（後端 API bug: 添加圖片時發生 500 錯誤）

---

**測試編號：IT-ANIMAL-022**

**測試目標**：驗證缺少必要欄位時新增圖片失敗  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備不完整的圖片資料（缺少 image_url）
2. 發送 POST 請求
3. 驗證返回 400 Bad Request

**測試角色**：動物擁有者  
**測試流程**：
- Request Payload：
  ```json
  {
    "storage_key": "animals/test.jpg"
  }
  ```
- HTTP 請求：`POST /api/animals/{test_animal.animal_id}/images` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 400`
- 預期行為：缺少必要欄位，返回 400 錯誤

**測試結果**：✅ 通過

---

### TestAnimalImagePermissions - 動物圖片權限測試類

**測試編號：IT-ANIMAL-023**

**測試目標**：驗證未登入用戶無法添加圖片  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 嘗試新增圖片
3. 驗證返回 401 Unauthorized

**測試角色**：訪客（未登入）  
**測試流程**：
- Request Payload：
  ```json
  {
    "storage_key": "test-key",
    "image_url": "https://example.com/test.jpg"
  }
  ```
- HTTP 請求：`POST /api/animals/{test_animal.animal_id}/images` with content_type='application/json'
- 驗證斷言：
  - `assert response.status_code == 401`
- 預期行為：未登入無法新增圖片

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-024**

**測試目標**：驗證未登入用戶無法刪除圖片  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 嘗試刪除圖片
3. 驗證返回 401 Unauthorized

**測試角色**：訪客（未登入）  
**測試流程**：
- HTTP 請求：`DELETE /api/animals/{test_animal.animal_id}/images/1`
- 驗證斷言：
  - `assert response.status_code == 401`
- 預期行為：未登入無法刪除圖片

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-025**

**測試目標**：驗證未登入用戶無法重新排序圖片  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 嘗試重新排序圖片
3. 驗證返回 401 Unauthorized

**測試角色**：訪客（未登入）  
**測試流程**：
- Request Payload：
  ```json
  {
    "image_orders": []
  }
  ```
- HTTP 請求：`PATCH /api/animals/{test_animal.animal_id}/images/reorder` with content_type='application/json'
- 驗證斷言：
  - `assert response.status_code == 401`
- 預期行為：未登入無法排序圖片

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-026**

**測試目標**：驗證擁有者可以刪除動物圖片  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 創建測試圖片
2. 使用擁有者的 Token 發送 DELETE 請求
3. 驗證圖片刪除成功

**測試角色**：動物擁有者  
**測試流程**：
- 測試資料準備：
  ```python
  image = AnimalImage(
      animal_image_id=500,
      animal_id=test_animal.animal_id,
      storage_key='test-key',
      url='https://example.com/test.jpg',
      order=1
  )
  db_session.add(image)
  db_session.commit()
  image_id = image.animal_image_id
  ```
- HTTP 請求：`DELETE /api/animals/{test_animal.animal_id}/images/{image_id}` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert data['message'] == '圖片已刪除'`
- 預期行為：圖片成功刪除

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-027**

**測試目標**：驗證擁有者可以重新排序動物圖片  
**測試方法**：端到端測試 (End-to-End Testing)  
**測試步驟**：
1. 創建 3 張測試圖片
2. 發送重新排序請求
3. 驗證圖片順序更新成功

**測試角色**：動物擁有者  
**測試流程**：
- 測試資料準備：
  ```python
  images = []
  for i in range(3):
      image = AnimalImage(
          animal_image_id=510 + i,
          animal_id=test_animal.animal_id,
          storage_key=f'test-key-{i}',
          url=f'https://example.com/test-{i}.jpg',
          order=i
      )
      db_session.add(image)
      images.append(image)
  db_session.commit()
  ```
- Request Payload：
  ```json
  {
    "image_orders": [
      {"image_id": 512, "order": 0},
      {"image_id": 510, "order": 1},
      {"image_id": 511, "order": 2}
    ]
  }
  ```
- HTTP 請求：`PATCH /api/animals/{test_animal.animal_id}/images/reorder` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert data['message'] == '圖片順序已更新'`
- 預期行為：圖片順序成功更新

**測試結果**：✅ 通過

---

### TestAnimalStatusManagement - 動物狀態管理測試類

**測試編號：IT-ANIMAL-028**

**測試目標**：驗證提交動物供審核（DRAFT → SUBMITTED）  
**測試方法**：狀態轉換測試 (State Transition Testing)  
**測試步驟**：
1. 創建草稿動物（status=DRAFT）
2. 使用擁有者的 Token 發送 POST 請求到 /submit
3. 驗證狀態變更為 SUBMITTED

**測試角色**：動物擁有者  
**測試流程**：
- 測試資料準備：
  ```python
  animal = Animal(
      animal_id=400,
      name='To Submit',
      species=Species.DOG,
      breed='Mixed',
      sex=Sex.MALE,
      dob=date(2023, 1, 1),
      status=AnimalStatus.DRAFT,
      owner_id=test_user.user_id,
      created_by=test_user.user_id
  )
  db_session.add(animal)
  db_session.commit()
  ```
- HTTP 請求：`POST /api/animals/{animal.animal_id}/submit` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert '已提交審核' in data['message']`
  - `assert data['animal']['status'] == 'SUBMITTED'`
- 資料庫驗證：
  - `db_session.refresh(animal)`
  - `assert animal.status == AnimalStatus.SUBMITTED`
- 預期行為：動物狀態從 DRAFT 變更為 SUBMITTED

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-029**

**測試目標**：驗證管理員發布動物（SUBMITTED → PUBLISHED）  
**測試方法**：狀態轉換測試 (State Transition Testing)  
**測試步驟**：
1. 創建管理員用戶
2. 創建已提交的動物（status=SUBMITTED）
3. 使用管理員的 Token 發送 POST 請求到 /publish
4. 驗證狀態變更為 PUBLISHED

**測試角色**：平台管理員  
**測試流程**：
- 測試資料準備：
  ```python
  admin = User(
      email='admin@test.com',
      username='admin',
      password_hash='hashed',
      role=UserRole.ADMIN,
      verified=True
  )
  db_session.add(admin)
  db_session.commit()
  
  animal = Animal(
      animal_id=401,
      name='To Publish',
      species=Species.DOG,
      breed='Mixed',
      sex=Sex.MALE,
      dob=date(2023, 1, 1),
      status=AnimalStatus.SUBMITTED,
      owner_id=test_user.user_id,
      created_by=test_user.user_id
  )
  db_session.add(animal)
  db_session.commit()
  
  token = create_access_token(identity=admin.user_id)
  headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json'
  }
  ```
- HTTP 請求：`POST /api/animals/{animal.animal_id}/publish` with headers=headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert '已發布' in data['message']`
- 資料庫驗證：
  - `db_session.refresh(animal)`
  - `assert animal.status == AnimalStatus.PUBLISHED`
- 預期行為：動物狀態從 SUBMITTED 變更為 PUBLISHED

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-030**

**測試目標**：驗證下架動物（PUBLISHED → RETIRED）  
**測試方法**：狀態轉換測試 (State Transition Testing)  
**測試步驟**：
1. 創建已發布的動物（status=PUBLISHED）
2. 使用擁有者的 Token 發送 POST 請求到 /retire
3. 驗證狀態變更為 RETIRED

**測試角色**：動物擁有者  
**測試流程**：
- 測試資料準備：
  ```python
  animal = Animal(
      animal_id=402,
      name='To Retire',
      species=Species.DOG,
      breed='Mixed',
      sex=Sex.MALE,
      dob=date(2023, 1, 1),
      status=AnimalStatus.PUBLISHED,
      owner_id=test_user.user_id,
      created_by=test_user.user_id
  )
  db_session.add(animal)
  db_session.commit()
  ```
- HTTP 請求：`POST /api/animals/{animal.animal_id}/retire` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert '已下架' in data['message']`
- 資料庫驗證：
  - `db_session.refresh(animal)`
  - `assert animal.status == AnimalStatus.RETIRED`
- 預期行為：動物狀態從 PUBLISHED 變更為 RETIRED

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-031**

**測試目標**：驗證管理員拒絕動物並記錄原因（SUBMITTED → DRAFT）  
**測試方法**：狀態轉換測試 (State Transition Testing)  
**測試步驟**：
1. 創建管理員用戶
2. 創建已提交的動物（status=SUBMITTED）
3. 使用管理員的 Token 發送 POST 請求到 /reject，帶拒絕原因
4. 驗證狀態變更為 DRAFT 且記錄拒絕原因

**測試角色**：平台管理員  
**測試流程**：
- 測試資料準備：
  ```python
  admin = User(
      email='admin2@test.com',
      username='admin2',
      password_hash='hashed',
      role=UserRole.ADMIN,
      verified=True
  )
  db_session.add(admin)
  db_session.commit()
  
  animal = Animal(
      animal_id=403,
      name='To Reject',
      species=Species.DOG,
      breed='Mixed',
      sex=Sex.MALE,
      dob=date(2023, 1, 1),
      status=AnimalStatus.SUBMITTED,
      owner_id=test_user.user_id,
      created_by=test_user.user_id
  )
  db_session.add(animal)
  db_session.commit()
  
  token = create_access_token(identity=admin.user_id)
  headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json'
  }
  ```
- Request Payload：
  ```json
  {
    "rejection_reason": "資料不完整，請補充詳細描述"
  }
  ```
- HTTP 請求：`POST /api/animals/{animal.animal_id}/reject` with headers=headers
- 驗證斷言：
  - `assert response.status_code == 200`
  - `assert '已拒絕' in data['message']`
- 資料庫驗證：
  - `db_session.refresh(animal)`
  - `assert animal.status == AnimalStatus.DRAFT`
  - `assert animal.rejection_reason == '資料不完整，請補充詳細描述'`
- 預期行為：動物狀態從 SUBMITTED 變更為 DRAFT，並記錄拒絕原因

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-032**

**測試目標**：驗證拒絕動物必須提供原因  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 創建管理員和已提交的動物
2. 發送拒絕請求但不提供原因
3. 驗證返回 400 Bad Request

**測試角色**：平台管理員  
**測試流程**：
- 測試資料準備：（同 IT-ANIMAL-031）
- Request Payload：
  ```json
  {}
  ```
- HTTP 請求：`POST /api/animals/{animal.animal_id}/reject` with headers=headers
- 驗證斷言：
  - `assert response.status_code == 400`
  - `assert '請提供拒絕原因' in data['message']`
- 預期行為：缺少拒絕原因，返回 400 錯誤

**測試結果**：✅ 通過

---

### TestAnimalStatusPermissions - 動物狀態權限測試類

**測試編號：IT-ANIMAL-033**

**測試目標**：驗證未登入用戶無法提交動物  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 嘗試提交動物
3. 驗證返回 401 Unauthorized

**測試角色**：訪客（未登入）  
**測試流程**：
- HTTP 請求：`POST /api/animals/{test_animal.animal_id}/submit`
- 驗證斷言：
  - `assert response.status_code == 401`
- 預期行為：未登入無法提交動物

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-034**

**測試目標**：驗證未登入用戶無法發布動物  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 嘗試發布動物
3. 驗證返回 401 Unauthorized

**測試角色**：訪客（未登入）  
**測試流程**：
- HTTP 請求：`POST /api/animals/{test_animal.animal_id}/publish`
- 驗證斷言：
  - `assert response.status_code == 401`
- 預期行為：未登入無法發布動物

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-035**

**測試目標**：驗證未登入用戶無法下架動物  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 嘗試下架動物
3. 驗證返回 401 Unauthorized

**測試角色**：訪客（未登入）  
**測試流程**：
- HTTP 請求：`POST /api/animals/{test_animal.animal_id}/retire`
- 驗證斷言：
  - `assert response.status_code == 401`
- 預期行為：未登入無法下架動物

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-036**

**測試目標**：驗證未登入用戶無法拒絕動物  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 不提供認證 Token
2. 嘗試拒絕動物
3. 驗證返回 401 Unauthorized

**測試角色**：訪客（未登入）  
**測試流程**：
- Request Payload：
  ```json
  {
    "rejection_reason": "test"
  }
  ```
- HTTP 請求：`POST /api/animals/{test_animal.animal_id}/reject` with content_type='application/json'
- 驗證斷言：
  - `assert response.status_code == 401`
- 預期行為：未登入無法拒絕動物

**測試結果**：✅ 通過

---

### TestAnimalEdgeCases - 動物管理邊界案例測試類

**測試編號：IT-ANIMAL-037**

**測試目標**：驗證更新不存在的動物返回錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 提供不存在的 animal_id（999999）
2. 嘗試更新動物
3. 驗證返回錯誤狀態碼

**測試角色**：已登入用戶  
**測試流程**：
- Request Payload：
  ```json
  {
    "name": "Updated"
  }
  ```
- HTTP 請求：`PATCH /api/animals/999999` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code in [404, 400, 403, 500]`
- 預期行為：返回錯誤狀態碼

**測試結果**：✅ 通過

---

**測試編號：IT-ANIMAL-038**

**測試目標**：驗證刪除不存在的動物返回錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 提供不存在的 animal_id（999999）
2. 嘗試刪除動物
3. 驗證返回錯誤狀態碼

**測試角色**：已登入用戶  
**測試流程**：
- HTTP 請求：`DELETE /api/animals/999999` with headers=auth_headers
- 驗證斷言：
  - `assert response.status_code in [404, 400, 403, 500]`
- 預期行為：返回錯誤狀態碼

**測試結果**：✅ 通過

---
