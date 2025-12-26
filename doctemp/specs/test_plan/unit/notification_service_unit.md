# Notification Service 單元測試計劃

## 文件說明
本文件記錄 NotificationService 的所有單元測試案例，共計 21 個測試案例。

---

**測試編號：UT-NOTIFICATIONSERVICE-001**

**測試目標**：Test successfully creating notification  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.create()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-002**

**測試目標**：Test creating notification without commit  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.create()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-003**

**測試目標**：Test notification when animal owner exists  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.notify_application_submitted()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-004**

**測試目標**：Test notification when animal belongs to shelter  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.notify_application_submitted()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-005**

**測試目標**：Test no notification when animal doesn't exist  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.notify_application_submitted()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-006**

**測試目標**：Test notification when application is approved  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.notify_application_reviewed()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-007**

**測試目標**：Test listing all notifications  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.list_notifications()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-008**

**測試目標**：Test listing unread notifications only  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.list_notifications()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-009**

**測試目標**：Test getting unread count  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.get_unread_count()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-010**

**測試目標**：Test marking notification as read  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.mark_as_read()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-011**

**測試目標**：Test marking non-existent notification  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `NotificationService.mark_as_read()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-012**

**測試目標**：Test permission denied when marking others notification  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `NotificationService.mark_as_read()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-013**

**測試目標**：Test marking all notifications as read  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.mark_all_as_read()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-014**

**測試目標**：Test successfully deleting notification  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.delete_notification()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-015**

**測試目標**：Test deleting non-existent notification  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 呼叫 `NotificationService.delete_notification()` 方法
2. 驗證結果符合預期
3. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-016**

**測試目標**：Test notifying animal owner of status change  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.notify_animal_status_changed()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-017**

**測試目標**：Test notifying shelter of animal status change  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.notify_animal_status_changed()` 方法
3. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-018**

**測試目標**：Test notifying job creator of completion  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.notify_job_completed()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-019**

**測試目標**：Test no notification when job has no creator  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.notify_job_completed()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-020**

**測試目標**：Test sending system notification  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.notify_system()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-NOTIFICATIONSERVICE-021**

**測試目標**：Test notifying applicant that application is under review  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `NotificationService.notify_application_under_review()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

