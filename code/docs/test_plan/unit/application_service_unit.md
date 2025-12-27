# Application Service 單元測試計劃

## 文件說明
本文件記錄 ApplicationService 的所有單元測試案例，共計 39 個測試案例。

---

**測試編號：UT-APPLICATIONSERVICE-001**

**測試目標**：TC-01: 管理員可以看到所有申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.list_applications()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 ApplicationService.list_applications()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-002**

**測試目標**：TC-02: 一般會員審核模式（看自己動物的申請）  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.list_applications()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-003**

**測試目標**：TC-03: 一般會員我的申請模式  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.list_applications()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-004**

**測試目標**：TC-04: 收容所成員包含收容所動物  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.list_applications()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-005**

**測試目標**：TC-05: 依狀態篩選  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.list_applications()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-006**

**測試目標**：TC-06: 無效狀態拋出錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.list_applications()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-007**

**測試目標**：TC-07: 非管理員不能查詢其他用戶的申請  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.list_applications()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-008**

**測試目標**：TC-08: 管理員可以查詢指定申請人  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.list_applications()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-009**

**測試目標**：TC-09: 成功創建申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `ApplicationService.create_application()` 方法
4. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 提供測試數據
- 執行 ApplicationService.create_application()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-010**

**測試目標**：TC-10: 非一般會員不能申請  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.create_application()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-011**

**測試目標**：TC-11: 缺少 animal_id  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.create_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-012**

**測試目標**：TC-12: 動物不存在  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.create_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-013**

**測試目標**：TC-13: 不能申請已領養動物  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.create_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-014**

**測試目標**：TC-14: 不能申請未發布動物  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.create_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-015**

**測試目標**：TC-15: 不能申請自己的動物  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.create_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-016**

**測試目標**：TC-16: 重複申請拋出衝突錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.create_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-017**

**測試目標**：TC-17: 冪等性鍵值返回已存在的申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.create_application()` 方法
3. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-018**

**測試目標**：TC-18: 成功批准申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 執行 ApplicationService.review_application()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-019**

**測試目標**：TC-19: 成功拒絕申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 執行 ApplicationService.review_application()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-020**

**測試目標**：TC-20: 申請不存在  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-021**

**測試目標**：TC-21: 無權限審核  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-022**

**測試目標**：TC-22: 管理員不能審核申請  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-023**

**測試目標**：TC-23: 無效操作  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-024**

**測試目標**：TC-24: 不能審核非待審核申請  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-025**

**測試目標**：TC-25: 樂觀鎖衝突  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-026**

**測試目標**：TC-26: 成功撤回申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.withdraw_application()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 執行 ApplicationService.withdraw_application()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-027**

**測試目標**：TC-27: 不能撤回其他人的申請  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.withdraw_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-028**

**測試目標**：TC-28: 不能撤回已批准申請  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.withdraw_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-029**

**測試目標**：TC-29: 管理員可以指派申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.assign_application()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 執行 ApplicationService.assign_application()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-030**

**測試目標**：TC-30: 非管理員不能指派  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.assign_application()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-031**

**測試目標**：TC-31: 指派給無效受理人  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.assign_application()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-032**

**測試目標**：TC-32: 管理員查詢指定申請人的申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.list_applications()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-033**

**測試目標**：TC-33: 用 animal_id 過濾申請  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.list_applications()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-034**

**測試目標**：TC-34: 動物有待審核申請時拋出衝突錯誤  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.create_application()` 方法
3. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-035**

**測試目標**：TC-35: 通知失敗不影響申請創建  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.create_application()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 執行 ApplicationService.create_application()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-036**

**測試目標**：TC-36: 通知失敗不影響審核  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：收容所成員  
**測試流程**：
- 執行 ApplicationService.review_application()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-037**

**測試目標**：TC-37: 通知失敗不影響指派  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.assign_application()` 方法
3. 驗證結果符合預期
4. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 執行 ApplicationService.assign_application()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-038**

**測試目標**：TC-38: 審核通過且發送 email 通知（owner 類型）  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 執行 ApplicationService.review_application()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-APPLICATIONSERVICE-039**

**測試目標**：TC-39: 審核通過且發送 email 通知（shelter 類型）  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `ApplicationService.review_application()` 方法
3. 驗證結果符合預期

**測試角色**：收容所成員  
**測試流程**：
- 執行 ApplicationService.review_application()
- 驗證結果值正確

**測試結果**：✅ 通過

---

