# Admin Service 單元測試計劃

## 文件說明
本文件記錄 AdminService 的所有單元測試案例，共計 23 個測試案例。

---

**測試編號：UT-ADMINSERVICE-001**

**測試目標**：TC-01: 返回完整的系統統計資料  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.get_system_statistics()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-002**

**測試目標**：TC-02: 分頁列出用戶  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_all_users()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AdminService.list_all_users()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-003**

**測試目標**：TC-03: 依角色篩選用戶  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_all_users()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-004**

**測試目標**：TC-04: 關鍵字搜尋用戶  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_all_users()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-005**

**測試目標**：TC-05: 無效角色拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_all_users()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-006**

**測試目標**：TC-06: 成功封禁用戶  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.ban_user()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-007**

**測試目標**：TC-07: 用戶不存在拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.ban_user()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-008**

**測試目標**：TC-08: 不能封禁管理員  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.ban_user()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-009**

**測試目標**：TC-09: 成功解除封禁  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.unban_user()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AdminService.unban_user()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-010**

**測試目標**：TC-10: 用戶不存在拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.unban_user()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-011**

**測試目標**：TC-11: 分頁列出動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_all_animals()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AdminService.list_all_animals()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-012**

**測試目標**：TC-12: 依狀態篩選動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_all_animals()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-013**

**測試目標**：TC-13: 包含已刪除動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_all_animals()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-014**

**測試目標**：TC-14: 分頁列出申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_all_applications()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AdminService.list_all_applications()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-015**

**測試目標**：TC-15: 依狀態篩選申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_all_applications()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-016**

**測試目標**：TC-16: 基本審計日誌列表  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_audit_logs()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AdminService.list_audit_logs()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-017**

**測試目標**：TC-17: 依操作者篩選  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_audit_logs()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-018**

**測試目標**：TC-18: 依操作類型篩選  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_audit_logs()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-019**

**測試目標**：TC-19: 依日期範圍篩選  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_audit_logs()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-020**

**測試目標**：TC-20: 無效開始日期格式  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_audit_logs()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-021**

**測試目標**：TC-21: 無效結束日期格式  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_audit_logs()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-022**

**測試目標**：TC-22: 審計日誌包含操作者資訊  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.list_audit_logs()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AdminService.list_audit_logs()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-ADMINSERVICE-023**

**測試目標**：TC-23: 取得審核員列表  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AdminService.get_reviewers()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 AdminService.get_reviewers()
- 驗證結果值正確

**測試結果**：✅ 通過

---

