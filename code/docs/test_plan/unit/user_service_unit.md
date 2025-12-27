# User Service 單元測試計劃

## 文件說明
本文件記錄 UserService 的所有單元測試案例，共計 24 個測試案例。

---

**測試編號：UT-USERSERVICE-001**

**測試目標**：Test getting own user includes sensitive info  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.get_user()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-002**

**測試目標**：Test admin can view others sensitive info  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.get_user()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-003**

**測試目標**：Test regular user cannot view others sensitive info  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.get_user()` 方法
3. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-004**

**測試目標**：Test user not found raises exception  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `UserService.get_user()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-005**

**測試目標**：Test user can update own info  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `UserService.update_user()` 方法
4. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 提供測試數據
- 執行 UserService.update_user()

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-006**

**測試目標**：Test admin can update user role  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `UserService.update_user()` 方法
4. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 提供測試數據
- 執行 UserService.update_user()

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-007**

**測試目標**：Test regular user cannot update role  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `UserService.update_user()` 方法
4. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 提供測試數據
- 執行 UserService.update_user()

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-008**

**測試目標**：Test updating email requires reverification  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `UserService.update_user()` 方法
4. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 提供測試數據
- 執行 UserService.update_user()

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-009**

**測試目標**：Test duplicate email raises conflict  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `UserService.update_user()` 方法
4. 驗證結果符合預期
5. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 驗證拋出 ConflictError 異常
- 提供測試數據

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-010**

**測試目標**：Test unauthorized update raises permission denied  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `UserService.update_user()` 方法
4. 驗證結果符合預期
5. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 驗證拋出 PermissionDeniedError 異常
- 提供測試數據

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-011**

**測試目標**：Test successfully changing password  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.change_password()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-012**

**測試目標**：Test cannot change others password  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `UserService.change_password()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-013**

**測試目標**：Test wrong old password raises validation error  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.change_password()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-014**

**測試目標**：Test short new password raises validation error  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.change_password()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-015**

**測試目標**：Test successfully requesting data export  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.request_data_export()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-016**

**測試目標**：Test cannot export others data  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `UserService.request_data_export()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-017**

**測試目標**：Test export fails when user not found  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `UserService.request_data_export()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-018**

**測試目標**：Test user can request own data deletion  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.request_data_deletion()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-019**

**測試目標**：Test admin can delete user data  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.request_data_deletion()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-020**

**測試目標**：Test regular user cannot delete others data  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.request_data_deletion()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-021**

**測試目標**：Test deletion fails when user not found  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.request_data_deletion()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-022**

**測試目標**：Test missing old password raises validation error  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.change_password()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-023**

**測試目標**：Test missing new password raises validation error  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `UserService.change_password()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-USERSERVICE-024**

**測試目標**：Test change password fails when user not found  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `UserService.change_password()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

