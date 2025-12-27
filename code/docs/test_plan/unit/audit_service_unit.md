# Audit Service 單元測試計劃

## 文件說明
本文件記錄 AuditService 的所有單元測試案例，共計 13 個測試案例。

---

**測試編號：UT-AUDITSERVICE-001**

**測試目標**：TC-01: 完整參數記錄審計日誌  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 執行 AuditService.log()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-002**

**測試目標**：TC-02: 不立即提交的日誌記錄  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-003**

**測試目標**：TC-03: 最小參數記錄（系統操作）  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 執行 AuditService.log()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-004**

**測試目標**：TC-04: 異常處理不影響主流程  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-005**

**測試目標**：TC-05: 記錄成功登入  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log_login()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 執行 AuditService.log_login()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-006**

**測試目標**：TC-06: 記錄失敗登入  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log_login()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 執行 AuditService.log_login()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-007**

**測試目標**：TC-07: 記錄申請審核  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log_application_review()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 執行 AuditService.log_application_review()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-008**

**測試目標**：TC-08: 記錄動物發布  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log_animal_publish()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AuditService.log_animal_publish()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-009**

**測試目標**：TC-09: 記錄收容所驗證  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log_shelter_verify()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AuditService.log_shelter_verify()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-010**

**測試目標**：TC-10: 記錄收容所取消驗證  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log_shelter_verify()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AuditService.log_shelter_verify()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-011**

**測試目標**：TC-11: 記錄用戶封禁  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log_user_ban()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AuditService.log_user_ban()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-012**

**測試目標**：TC-12: 記錄資料匯出  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log_data_export()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 執行 AuditService.log_data_export()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-AUDITSERVICE-013**

**測試目標**：TC-13: 記錄資料刪除  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AuditService.log_data_deletion()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 執行 AuditService.log_data_deletion()
- 驗證結果值正確

**測試結果**：✅ 通過

---

