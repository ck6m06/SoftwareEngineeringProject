# AnimalService 單元測試計劃

## 文件說明
本文件記錄 AnimalService 的所有單元測試案例，共計 60 個測試案例。

---

**測試編號：UT-ANIMAL-001**

**測試目標**：驗證收容所成員創建動物歸屬收容所  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 收容所成員（UserRole.SHELTER_MEMBER）提供動物資料
2. 呼叫 `AnimalService.create_animal(user, data)`
3. 驗證動物的 shelter_id 等於用戶的 primary_shelter_id

**測試角色**：收容所成員  
**測試流程**：
- Mock 收容所成員用戶對象（role=SHELTER_MEMBER, primary_shelter_id=10）
- 提供動物資料 {'name': '小白', 'species': 'DOG'}
- 執行創建操作
- 驗證 animal.shelter_id == 10 且 animal.owner_id is None

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-002**

**測試目標**：驗證一般會員創建個人動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 一般會員（UserRole.GENERAL_MEMBER）提供動物資料
2. 執行創建操作
3. 驗證動物的 owner_id 等於用戶 ID

**測試角色**：一般會員  
**測試流程**：
- Mock 一般會員用戶對象（user_id=2, role=GENERAL_MEMBER, primary_shelter_id=None）
- 提供動物資料 {'name': '小黑', 'species': 'CAT'}
- 執行創建操作
- 驗證 animal.owner_id == 2 且 animal.shelter_id is None

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-003**

**測試目標**：驗證管理員可指定收容所  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 管理員（UserRole.ADMIN）提供動物資料及指定的 shelter_id
2. 執行創建操作
3. 驗證動物歸屬指定的收容所

**測試角色**：平台管理員  
**測試流程**：
- Mock 管理員用戶對象（role=ADMIN）
- 提供動物資料 {'name': '小花', 'species': 'DOG', 'shelter_id': 20}
- 執行創建操作
- 驗證 animal.shelter_id == 20

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-004**

**測試目標**：驗證防護測試（同時指定 owner 和 shelter）  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 測試不能同時設定 owner_id 和 shelter_id

**測試角色**：平台  
**測試流程**：
- 驗證資料完整性約束

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-005**

**測試目標**：驗證擁有者可更新自己的動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 擁有者提供更新資料
2. 呼叫 `AnimalService.update_animal(animal_id, user, data)`
3. 驗證資料更新成功

**測試角色**：動物擁有者  
**測試流程**：
- Mock 動物擁有者（user_id=1）
- Mock 動物對象（animal_id=100, owner_id=1）
- Mock permission_service.can_manage_animal 返回 True
- 提供更新資料 {'name': '新名字'}
- 驗證 animal.name == '新名字'

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-006**

**測試目標**：驗證已刪除動物拋出 NotFoundError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 查詢已刪除的動物
2. 驗證拋出 NotFoundError

**測試角色**：使用者  
**測試流程**：
- Mock Animal.query.filter_by(deleted_at=None).first() 返回 None
- 呼叫 update_animal(999, user, data)
- 預期拋出 NotFoundError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-007**

**測試目標**：驗證無權限用戶拋出 PermissionDeniedError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 非擁有者嘗試更新動物
2. 驗證拋出 PermissionDeniedError

**測試角色**：非擁有者  
**測試流程**：
- Mock permission_service.can_manage_animal 返回 False
- 呼叫 update_animal(100, user, data)
- 預期拋出 PermissionDeniedError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-008**

**測試目標**：驗證更新多個欄位  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 同時更新動物的多個屬性（name, breed, color, description）
2. 驗證所有欄位都正確更新

**測試角色**：動物擁有者  
**測試流程**：
- 提供多欄位更新資料
- 執行更新操作
- 逐一驗證各欄位的新值

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-009**

**測試目標**：驗證更新動物出生日期 (dob)  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 更新動物的 dob 欄位
2. 驗證日期正確設定

**測試角色**：動物擁有者  
**測試流程**：
- 提供 {'dob': '2020-01-15'}
- 執行更新
- 驗證 animal.dob 不為 None

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-010**

**測試目標**：驗證更新醫療摘要 (medical_summary)  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 更新動物的 medical_summary 欄位
2. 驗證內容正確設定

**測試角色**：動物擁有者  
**測試流程**：
- 提供 {'medical_summary': '健康狀況良好'}
- 執行更新
- 驗證 animal.medical_summary == '健康狀況良好'

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-011**

**測試目標**：驗證更新動物狀態欄位  
**測試方法**：狀態轉換測試 (State Transition Testing)  
**測試步驟**：
1. 直接更新 status 欄位
2. 驗證狀態變更

**測試角色**：動物擁有者  
**測試流程**：
- 提供 {'status': 'PUBLISHED'}
- 驗證 animal.status == AnimalStatus.PUBLISHED

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-012**

**測試目標**：驗證軟刪除設定 deleted_at 時間戳  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 擁有者刪除動物
2. 驗證 deleted_at 欄位被設定

**測試角色**：動物擁有者  
**測試流程**：
- Mock animal.deleted_at = None
- Mock permission_service.can_manage_animal 返回 True
- 呼叫 delete_animal(100, user)
- 驗證 animal.deleted_at is not None

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-013**

**測試目標**：驗證管理員可以刪除任何動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 管理員刪除非自己的動物
2. 驗證刪除成功（即使 can_manage_animal 返回 False）

**測試角色**：平台管理員  
**測試流程**：
- Mock 管理員（role=ADMIN）
- Mock animal.owner_id = 999（不是管理員的）
- Mock permission_service.can_manage_animal 返回 False
- 執行刪除操作
- 驗證 animal.deleted_at is not None

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-014**

**測試目標**：驗證取得動物基本資料  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 animal_id
2. 呼叫 `AnimalService.get_animal(animal_id)`
3. 驗證返回動物對象

**測試角色**：使用者  
**測試流程**：
- Mock Animal.query.filter_by(animal_id=1, deleted_at=None).first() 返回動物
- 呼叫 get_animal(1)
- 驗證返回的動物資料

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-015**

**測試目標**：驗證動物不存在拋出 NotFoundError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 查詢不存在的 animal_id
2. 驗證拋出 NotFoundError

**測試角色**：使用者  
**測試流程**：
- Mock query 返回 None
- 呼叫 get_animal(999)
- 預期拋出 NotFoundError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-016**

**測試目標**：驗證排除已刪除動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 查詢時自動過濾 deleted_at != None 的動物
2. 驗證 filter_by 呼叫包含 deleted_at=None

**測試角色**：使用者  
**測試流程**：
- 驗證查詢條件包含 deleted_at=None
- 確保已刪除動物不被返回

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-017**

**測試目標**：驗證訪客只看已發布動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 未登入用戶查詢動物列表
2. 驗證只返回 status=PUBLISHED 的動物

**測試角色**：訪客（未登入）  
**測試流程**：
- 不提供 current_user_id
- 執行 list_animals({'page': 1, 'per_page': 20})
- 驗證查詢條件包含 status=PUBLISHED
- 驗證返回分頁結果

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-018**

**測試目標**：驗證依物種篩選  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 species 參數
2. 驗證返回符合物種的動物

**測試角色**：使用者  
**測試流程**：
- 提供 {'species': 'DOG', 'page': 1}
- 驗證查詢條件包含 species=DOG
- 驗證返回結果

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-019**

**測試目標**：驗證分頁功能正確運作  
**測試方法**：邊界值分析 (Boundary Value Analysis)  
**測試步驟**：
1. 提供 page 和 per_page 參數
2. 驗證分頁資訊正確

**測試角色**：使用者  
**測試流程**：
- 提供 {'page': 2, 'per_page': 20}
- Mock pagination 返回 total=100, pages=5, page=2
- 驗證返回的 page 和 total 正確

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-020**

**測試目標**：驗證關鍵字搜尋功能  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 q (關鍵字) 參數
2. 驗證搜尋 name 或 description 欄位

**測試角色**：使用者  
**測試流程**：
- 提供 {'q': '小白', 'page': 1}
- 驗證查詢使用 filter 進行模糊搜尋
- 驗證返回匹配的動物

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-021**

**測試目標**：驗證來源類型篩選 - 收容所  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 source_type='shelter'
2. 驗證只返回 shelter_id IS NOT NULL 的動物

**測試角色**：使用者  
**測試流程**：
- 提供 {'source_type': 'shelter', 'page': 1}
- 驗證篩選條件
- 驗證返回收容所動物

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-022**

**測試目標**：驗證來源類型篩選 - 個人  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 source_type='personal'
2. 驗證只返回 owner_id IS NOT NULL 的動物

**測試角色**：使用者  
**測試流程**：
- 提供 {'source_type': 'personal', 'page': 1}
- 驗證篩選條件
- 驗證返回個人動物

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-023**

**測試目標**：驗證地區篩選  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 region 參數
2. 驗證返回該地區的動物

**測試角色**：使用者  
**測試流程**：
- 提供 {'region': '台北', 'page': 1}
- 驗證篩選邏輯
- 驗證返回結果

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-024**

**測試目標**：驗證年齡範圍篩選（MySQL）  
**測試方法**：邊界值分析 (Boundary Value Analysis)  
**測試步驟**：
1. 提供 min_age 和 max_age 參數
2. 驗證使用 TIMESTAMPDIFF 計算年齡（MySQL）

**測試角色**：使用者  
**測試流程**：
- Mock db.engine.name = 'mysql'
- 提供 {'min_age': 6, 'max_age': 24, 'page': 1}
- 驗證年齡計算邏輯（月份）
- 驗證返回符合年齡範圍的動物

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-025**

**測試目標**：驗證年齡範圍篩選（SQLite）  
**測試方法**：邊界值分析 (Boundary Value Analysis)  
**測試步驟**：
1. 提供 min_age 參數
2. 驗證 SQLite 使用替代的日期計算方法

**測試角色**：使用者  
**測試流程**：
- Mock db.engine.name = 'sqlite'
- 提供 {'min_age': 6, 'page': 1}
- 驗證使用 SQLite 相容的日期函數
- 驗證返回結果

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-026**

**測試目標**：驗證 owner_id 篩選（查詢自己）  
**測試方法**：決策表測試 (Decision Table Testing)  
**測試步驟**：
1. 用戶查詢自己的動物（owner_id=current_user_id）
2. 驗證可以看到自己所有狀態的動物

**測試角色**：一般會員  
**測試流程**：
- Mock user (role=GENERAL_MEMBER)
- 提供 {'owner_id': 5, 'page': 1}, current_user_id=5
- 驗證不限制 status
- 驗證返回所有自己的動物

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-027**

**測試目標**：驗證收容所成員查詢 owner_id  
**測試方法**：決策表測試 (Decision Table Testing)  
**測試步驟**：
1. 收容所成員查詢特定 owner_id
2. 驗證權限處理

**測試角色**：收容所成員  
**測試流程**：
- Mock user (role=SHELTER_MEMBER, primary_shelter_id=10)
- 提供 {'owner_id': 5, 'page': 1}, current_user_id=5
- 驗證查詢邏輯
- 驗證返回結果

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-028**

**測試目標**：驗證訪客查詢 owner_id（只看已發布）  
**測試方法**：決策表測試 (Decision Table Testing)  
**測試步驟**：
1. 未登入用戶查詢特定 owner_id 的動物
2. 驗證只返回 status=PUBLISHED 的動物

**測試角色**：訪客  
**測試流程**：
- 提供 {'owner_id': 5, 'page': 1}, current_user_id=None
- 驗證強制 status=PUBLISHED
- 驗證返回公開動物

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-029**

**測試目標**：驗證查詢其他用戶的動物  
**測試方法**：決策表測試 (Decision Table Testing)  
**測試步驟**：
1. 用戶 A 查詢用戶 B 的動物
2. 驗證只能看到已發布的

**測試角色**：使用者  
**測試流程**：
- 提供 {'owner_id': 5, 'page': 1}, current_user_id=10
- 驗證限制 status=PUBLISHED
- 驗證返回結果

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-030**

**測試目標**：驗證 created_by 篩選  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 created_by 參數
2. 驗證返回該用戶創建的動物

**測試角色**：使用者  
**測試流程**：
- 提供 {'created_by': 10, 'page': 1}
- 驗證篩選條件
- 驗證返回結果

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-031**

**測試目標**：驗證依收容所 ID 篩選  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 shelter_id 參數
2. 驗證返回該收容所的動物

**測試角色**：使用者  
**測試流程**：
- 提供 {'shelter_id': 10, 'page': 1}
- 驗證篩選條件
- 驗證返回結果

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-032**

**測試目標**：驗證依性別篩選  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 提供 sex 參數
2. 驗證返回符合性別的動物

**測試角色**：使用者  
**測試流程**：
- 提供 {'sex': 'MALE', 'page': 1}
- 驗證篩選條件
- 驗證返回雄性動物

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-033**

**測試目標**：驗證提交審核功能  
**測試方法**：狀態轉換測試 (State Transition Testing)  
**測試步驟**：
1. 擁有者將動物從 DRAFT 提交審核
2. 呼叫 `AnimalService.submit_for_review(animal_id, user)`
3. 驗證狀態變更為 SUBMITTED

**測試角色**：動物擁有者  
**測試流程**：
- Mock animal.status = AnimalStatus.DRAFT
- Mock permission_service.can_submit_animal_for_review 返回 True
- 執行 submit_for_review(100, user)
- 驗證 animal.status == AnimalStatus.SUBMITTED

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-034**

**測試目標**：驗證發布動物功能  
**測試方法**：狀態轉換測試 (State Transition Testing)  
**測試步驟**：
1. 管理員將 SUBMITTED 動物發布
2. 呼叫 `AnimalService.publish_animal(animal_id, admin)`
3. 驗證狀態變更為 PUBLISHED

**測試角色**：平台管理員  
**測試流程**：
- Mock animal.status = AnimalStatus.SUBMITTED
- Mock permission_service.can_publish_animal 返回 True
- 執行 publish_animal(100, admin)
- 驗證 animal.status == AnimalStatus.PUBLISHED

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-035**

**測試目標**：驗證下架動物功能  
**測試方法**：狀態轉換測試 (State Transition Testing)  
**測試步驟**：
1. 擁有者下架 PUBLISHED 動物
2. 呼叫 `AnimalService.retire_animal(animal_id, user)`
3. 驗證狀態變更為 RETIRED

**測試角色**：動物擁有者  
**測試流程**：
- Mock animal.status = AnimalStatus.PUBLISHED
- Mock permission_service.can_manage_animal 返回 True
- 執行 retire_animal(100, user)
- 驗證 animal.status == AnimalStatus.RETIRED

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-036**

**測試目標**：驗證拒絕動物並記錄原因  
**測試方法**：狀態轉換測試 (State Transition Testing)  
**測試步驟**：
1. 管理員拒絕 SUBMITTED 動物
2. 提供拒絕原因
3. 驗證狀態變回 DRAFT 且記錄原因

**測試角色**：平台管理員  
**測試流程**：
- Mock animal.status = AnimalStatus.SUBMITTED
- Mock permission_service.can_reject_animal 返回 True
- 執行 reject_animal(100, admin, '資料不完整')
- 驗證 animal.status == AnimalStatus.DRAFT
- 驗證 animal.rejection_reason == '資料不完整'

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-037**

**測試目標**：驗證管理員可下架任何動物  
**測試方法**：狀態轉換測試 (State Transition Testing)  
**測試步驟**：
1. 管理員下架非自己的動物
2. 驗證下架成功（即使 can_manage_animal 返回 False）

**測試角色**：平台管理員  
**測試流程**：
- Mock admin (role=ADMIN)
- Mock animal.owner_id = 999
- Mock permission_service.can_manage_animal 返回 False
- 執行 retire_animal(100, admin)
- 驗證 animal.status == AnimalStatus.RETIRED

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-038**

**測試目標**：驗證提交審核權限不足拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 無權限用戶嘗試提交審核
2. 驗證拋出 PermissionDeniedError

**測試角色**：非擁有者  
**測試流程**：
- Mock permission_service.can_submit_animal_for_review 返回 False
- 執行 submit_for_review(100, user)
- 預期拋出 PermissionDeniedError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-039**

**測試目標**：驗證發布動物權限不足拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 非管理員嘗試發布動物
2. 驗證拋出 PermissionDeniedError

**測試角色**：非管理員  
**測試流程**：
- Mock permission_service.can_publish_animal 返回 False
- 執行 publish_animal(100, user)
- 預期拋出 PermissionDeniedError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-040**

**測試目標**：驗證拒絕動物權限不足拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 非管理員嘗試拒絕動物
2. 驗證拋出 PermissionDeniedError

**測試角色**：非管理員  
**測試流程**：
- Mock permission_service.can_reject_animal 返回 False
- 執行 reject_animal(100, user, '理由')
- 預期拋出 PermissionDeniedError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-041**

**測試目標**：驗證提交審核時狀態錯誤拋出 ValidationError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 嘗試提交非 DRAFT 狀態的動物
2. 驗證拋出 ValidationError

**測試角色**：動物擁有者  
**測試流程**：
- Mock animal.status = AnimalStatus.PUBLISHED
- 執行 submit_for_review(100, user)
- 預期拋出 ValidationError('只能提交草稿狀態的動物')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-042**

**測試目標**：驗證發布已發布動物拋出 ValidationError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 嘗試發布已經是 PUBLISHED 的動物
2. 驗證拋出 ValidationError

**測試角色**：平台管理員  
**測試流程**：
- Mock animal.status = AnimalStatus.PUBLISHED
- 執行 publish_animal(100, admin)
- 預期拋出 ValidationError('動物已經是發布狀態')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-043**

**測試目標**：驗證下架已下架動物拋出 ValidationError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 嘗試下架已經是 RETIRED 的動物
2. 驗證拋出 ValidationError

**測試角色**：動物擁有者  
**測試流程**：
- Mock animal.status = AnimalStatus.RETIRED
- 執行 retire_animal(100, user)
- 預期拋出 ValidationError('動物已經是下架狀態')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-044**

**測試目標**：驗證拒絕非待審核動物拋出 ValidationError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 嘗試拒絕非 SUBMITTED 狀態的動物
2. 驗證拋出 ValidationError

**測試角色**：平台管理員  
**測試流程**：
- Mock animal.status = AnimalStatus.PUBLISHED
- 執行 reject_animal(100, admin, '理由')
- 預期拋出 ValidationError('只能拒絕待審核狀態的動物')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-045**

**測試目標**：驗證拒絕動物未提供原因拋出 ValidationError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 拒絕動物但提供空白原因
2. 驗證拋出 ValidationError

**測試角色**：平台管理員  
**測試流程**：
- Mock animal.status = AnimalStatus.SUBMITTED
- 執行 reject_animal(100, admin, '   ')  # 空白字串
- 預期拋出 ValidationError('請提供拒絕原因')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-046**

**測試目標**：驗證新增圖片功能  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 擁有者上傳動物圖片
2. 呼叫 `AnimalService.add_image(animal_id, user, key, url)`
3. 驗證創建 AnimalImage 記錄

**測試角色**：動物擁有者  
**測試流程**：
- Mock permission_service.can_manage_animal 返回 True
- Mock 圖片數量查詢返回 0
- 執行 add_image(100, user, 'key', 'url')
- 驗證 AnimalImage 類別被呼叫

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-047**

**測試目標**：驗證刪除圖片功能  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 擁有者刪除動物圖片
2. 呼叫 `AnimalService.delete_image(animal_id, image_id, user)`
3. 驗證圖片記錄被刪除

**測試角色**：動物擁有者  
**測試流程**：
- Mock permission_service.can_manage_animal 返回 True
- Mock AnimalImage.query 返回圖片對象
- 執行 delete_image(100, 50, user)
- 驗證 db.session.delete 被呼叫

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-048**

**測試目標**：驗證重新排序圖片功能  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 擁有者調整圖片順序
2. 呼叫 `AnimalService.reorder_images(animal_id, user, orders)`
3. 驗證圖片 order 欄位更新

**測試角色**：動物擁有者  
**測試流程**：
- Mock permission_service.can_manage_animal 返回 True
- Mock 兩張圖片對象（image1.order=1, image2.order=2）
- 提供新順序 [{'image_id': 2, 'order': 1}, {'image_id': 1, 'order': 2}]
- 執行 reorder_images(100, user, orders)
- 驗證 image1.order == 2 且 image2.order == 1

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-049**

**測試目標**：驗證新增圖片權限不足拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 無權限用戶嘗試新增圖片
2. 驗證拋出 PermissionDeniedError

**測試角色**：非擁有者  
**測試流程**：
- Mock permission_service.can_manage_animal 返回 False
- 執行 add_image(100, user, 'key', 'url')
- 預期拋出 PermissionDeniedError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-050**

**測試目標**：驗證刪除不存在的圖片拋出 NotFoundError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 嘗試刪除不存在的圖片 ID
2. 驗證拋出 NotFoundError

**測試角色**：動物擁有者  
**測試流程**：
- Mock permission_service.can_manage_animal 返回 True
- Mock AnimalImage.query 返回 None
- 執行 delete_image(100, 50, user)
- 預期拋出 NotFoundError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-051**

**測試目標**：驗證新增圖片時動物不存在拋出 NotFoundError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 為不存在的動物新增圖片
2. 驗證拋出 NotFoundError

**測試角色**：使用者  
**測試流程**：
- Mock Animal.query 返回 None
- 執行 add_image(999, user, 'key', 'url')
- 預期拋出 NotFoundError('動物不存在')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-052**

**測試目標**：驗證刪除圖片時動物不存在拋出 NotFoundError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 為不存在的動物刪除圖片
2. 驗證拋出 NotFoundError

**測試角色**：使用者  
**測試流程**：
- Mock Animal.query 返回 None
- 執行 delete_image(999, 50, user)
- 預期拋出 NotFoundError('動物不存在')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-053**

**測試目標**：驗證重新排序圖片時動物不存在拋出 NotFoundError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 為不存在的動物排序圖片
2. 驗證拋出 NotFoundError

**測試角色**：使用者  
**測試流程**：
- Mock Animal.query 返回 None
- 執行 reorder_images(999, user, [])
- 預期拋出 NotFoundError('動物不存在')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-054**

**測試目標**：驗證重新排序圖片權限不足拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 無權限用戶嘗試排序圖片
2. 驗證拋出 PermissionDeniedError

**測試角色**：非擁有者  
**測試流程**：
- Mock permission_service.can_manage_animal 返回 False
- 執行 reorder_images(100, user, [])
- 預期拋出 PermissionDeniedError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-055**

**測試目標**：驗證無效物種值拋出 ValidationError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 查詢時提供無效的 species 值
2. 驗證拋出 ValidationError

**測試角色**：使用者  
**測試流程**：
- 提供 {'species': 'INVALID_SPECIES', 'page': 1}
- 預期拋出 ValidationError(match='無效的物種值')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-056**

**測試目標**：驗證無效性別值拋出 ValidationError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 查詢時提供無效的 sex 值
2. 驗證拋出 ValidationError

**測試角色**：使用者  
**測試流程**：
- 提供 {'sex': 'INVALID_SEX', 'page': 1}
- 預期拋出 ValidationError(match='無效的性別值')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-057**

**測試目標**：驗證無效狀態值拋出 ValidationError  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 查詢時提供無效的 status 值
2. 驗證拋出 ValidationError

**測試角色**：使用者  
**測試流程**：
- 提供 {'status': 'INVALID_STATUS', 'page': 1}
- 預期拋出 ValidationError(match='無效的狀態值')

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-058**

**測試目標**：驗證更新動物時無效物種拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 更新動物時提供無效的 species
2. 驗證拋出 ValidationError 或 ValueError

**測試角色**：動物擁有者  
**測試流程**：
- Mock permission_service.can_manage_animal 返回 True
- 提供 {'species': 'INVALID'}
- 預期拋出 ValidationError 或 ValueError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-059**

**測試目標**：驗證更新動物時無效性別拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 更新動物時提供無效的 sex
2. 驗證拋出 ValidationError 或 ValueError

**測試角色**：動物擁有者  
**測試流程**：
- Mock permission_service.can_manage_animal 返回 True
- 提供 {'sex': 'INVALID'}
- 預期拋出 ValidationError 或 ValueError

**測試結果**：✅ 通過

---

**測試編號：UT-ANIMAL-060**

**測試目標**：驗證更新動物時無效狀態拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 更新動物時提供無效的 status
2. 驗證拋出 ValidationError 或 ValueError

**測試角色**：動物擁有者  
**測試流程**：
- Mock permission_service.can_manage_animal 返回 True
- 提供 {'status': 'INVALID'}
- 預期拋出 ValidationError 或 ValueError

**測試結果**：✅ 通過

---

