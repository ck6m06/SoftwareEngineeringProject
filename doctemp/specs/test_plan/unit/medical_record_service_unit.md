# MedicalRecord Service 單元測試計劃

## 文件說明
本文件記錄 MedicalRecordService 的所有單元測試案例，共計 31 個測試案例。

---

**測試編號：UT-MEDICALRECORDSERVICE-001**

**測試目標**：測試管理員可以看到所有動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.list_animals_for_medical_records()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-002**

**測試目標**：測試收容所成員可以看到自己的和收容所的動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.list_animals_for_medical_records()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-003**

**測試目標**：測試一般用戶只能看到自己的動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.list_animals_for_medical_records()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-004**

**測試目標**：測試管理員可以創建醫療記錄  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.create_medical_record()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-005**

**測試目標**：測試動物不存在時拋出異常  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `MedicalRecordService.create_medical_record()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-006**

**測試目標**：測試用戶不存在時拋出異常  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.create_medical_record()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-007**

**測試目標**：測試無權限用戶創建醫療記錄時拋出異常  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.create_medical_record()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：收容所成員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-008**

**測試目標**：測試創建者可以在24小時內更新  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.update_medical_record()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-009**

**測試目標**：測試記錄不存在時拋出異常  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `MedicalRecordService.update_medical_record()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-010**

**測試目標**：測試管理員不能直接編輯醫療記錄  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.update_medical_record()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-011**

**測試目標**：測試超過24小時後無法更新  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.update_medical_record()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：收容所成員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-012**

**測試目標**：測試管理員可以驗證醫療記錄  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.verify_medical_record()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-013**

**測試目標**：測試非管理員無法驗證醫療記錄  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.verify_medical_record()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-014**

**測試目標**：測試解析 YYYY-MM-DD 格式  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 呼叫 `MedicalRecordService.parse_date()` 方法
2. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-015**

**測試目標**：測試解析 YYYY/MM/DD 格式  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 呼叫 `MedicalRecordService.parse_date()` 方法
2. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-016**

**測試目標**：測試解析 DD/MM/YYYY 格式  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 呼叫 `MedicalRecordService.parse_date()` 方法
2. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-017**

**測試目標**：測試解析 DD-MM-YYYY 格式  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 呼叫 `MedicalRecordService.parse_date()` 方法
2. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-018**

**測試目標**：測試解析帶有空白的日期  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 呼叫 `MedicalRecordService.parse_date()` 方法
2. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-019**

**測試目標**：測試無效日期格式拋出異常  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `MedicalRecordService.parse_date()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-020**

**測試目標**：測試成功列出動物的醫療記錄  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.list_animal_medical_records()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-021**

**測試目標**：測試動物不存在時拋出異常  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `MedicalRecordService.list_animal_medical_records()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-022**

**測試目標**：測試成功獲取醫療記錄  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.get_medical_record()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-023**

**測試目標**：測試記錄不存在時拋出異常  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `MedicalRecordService.get_medical_record()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-024**

**測試目標**：測試按名稱過濾  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.list_animals_for_medical_records()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-025**

**測試目標**：測試按品種過濾  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.list_animals_for_medical_records()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-026**

**測試目標**：測試按物種過濾  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.list_animals_for_medical_records()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-027**

**測試目標**：測試按年齡範圍過濾  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.list_animals_for_medical_records()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-028**

**測試目標**：測試過濾已領養動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備要刪除的對象
2. 執行刪除操作
3. 驗證刪除標記或實際刪除
4. 確認數據庫操作

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-029**

**測試目標**：測試過濾未領養動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備要刪除的對象
2. 執行刪除操作
3. 驗證刪除標記或實際刪除
4. 確認數據庫操作

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-030**

**測試目標**：測試創建醫療紀錄並添加附件  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.create_medical_record()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-MEDICALRECORDSERVICE-031**

**測試目標**：測試更新醫療紀錄並添加新附件  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `MedicalRecordService.update_medical_record()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

