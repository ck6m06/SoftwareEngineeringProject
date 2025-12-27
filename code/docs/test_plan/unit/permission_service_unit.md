# Permission Service 單元測試計劃

## 文件說明
本文件記錄 PermissionService 的所有單元測試案例，共計 26 個測試案例。

---

**測試編號：UT-PERMISSIONSERVICE-001**

**測試目標**：TC-01: 擁有者可以管理個人送養動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_manage_animal()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-002**

**測試目標**：TC-02: 非擁有者不能管理個人動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_manage_animal()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-003**

**測試目標**：TC-03: 收容所成員可以管理自己收容所的動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_manage_animal()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-004**

**測試目標**：TC-04: 收容所成員不能管理其他收容所動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_manage_animal()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-005**

**測試目標**：TC-05: 管理員可以管理收容所動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_manage_animal()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-006**

**測試目標**：TC-06: 管理員不能管理個人動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_manage_animal()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-007**

**測試目標**：TC-06a: None 用戶不能管理動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_manage_animal()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-008**

**測試目標**：TC-06b: 用戶不能管理 None 動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_manage_animal()` 方法
3. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-009**

**測試目標**：TC-07: 任何人可以查看已發布的動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_view_animal()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-010**

**測試目標**：TC-08: 未登入用戶不能查看草稿動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_view_animal()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-011**

**測試目標**：TC-09: 擁有者可以查看自己的草稿  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_view_animal()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-012**

**測試目標**：TC-10: 擁有者可以審核申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_review_application()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-013**

**測試目標**：TC-11: 收容所成員可以審核收容所申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_review_application()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-014**

**測試目標**：TC-12: 非擁有者不能審核申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_review_application()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-015**

**測試目標**：TC-12a: None application 不能審核  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_review_application()` 方法
3. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-016**

**測試目標**：TC-12b: 沒有動物的申請不能審核  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_review_application()` 方法
3. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-017**

**測試目標**：TC-13: 申請人可以查看自己的申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_view_application()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-018**

**測試目標**：TC-14: 動物擁有者可以查看申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_view_application()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-019**

**測試目標**：TC-15: 管理員可以查看任何申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_view_application()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-020**

**測試目標**：TC-15a: None application 不能查看  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_view_application()` 方法
3. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-021**

**測試目標**：TC-15b: 非申請人且無動物的申請不能查看  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_view_application()` 方法
3. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-022**

**測試目標**：TC-16: 擁有者可以提交草稿動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_submit_animal_for_review()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-023**

**測試目標**：TC-17: 管理員可以發布待審核動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_publish_animal()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-024**

**測試目標**：TC-18: 非管理員不能發布動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_publish_animal()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-025**

**測試目標**：TC-19: 管理員可以拒絕待審核動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_reject_animal()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

**測試編號：UT-PERMISSIONSERVICE-026**

**測試目標**：TC-20: 非管理員不能拒絕動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `PermissionService.can_reject_animal()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

