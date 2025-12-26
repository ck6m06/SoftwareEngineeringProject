# Attachment Service 單元測試計劃

## 文件說明
本文件記錄 AttachmentService 的所有單元測試案例，共計 11 個測試案例。

---

**測試編號：UT-ATTACHMENTSERVICE-001**

**測試目標**：TC-01: 成功創建附件  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `AttachmentService.create_attachment()` 方法
4. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 提供測試數據
- 執行 AttachmentService.create_attachment()

**測試結果**：✅ 通過

---

**測試編號：UT-ATTACHMENTSERVICE-002**

**測試目標**：TC-02: 缺少必填欄位  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `AttachmentService.create_attachment()` 方法
4. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ATTACHMENTSERVICE-003**

**測試目標**：TC-03: 檔案不存在於 MinIO  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `AttachmentService.create_attachment()` 方法
4. 確認拋出預期的異常

**測試角色**：一般用戶  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ATTACHMENTSERVICE-004**

**測試目標**：TC-04: 創建不關聯實體的附件  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 提供測試數據
3. 呼叫 `AttachmentService.create_attachment()` 方法
4. 驗證結果符合預期

**測試角色**：一般用戶  
**測試流程**：
- 提供測試數據
- 執行 AttachmentService.create_attachment()

**測試結果**：✅ 通過

---

**測試編號：UT-ATTACHMENTSERVICE-005**

**測試目標**：TC-05: 成功取得附件  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AttachmentService.get_attachment()` 方法
3. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 執行 AttachmentService.get_attachment()
- 驗證結果值正確

**測試結果**：✅ 通過

---

**測試編號：UT-ATTACHMENTSERVICE-006**

**測試目標**：TC-06: 附件不存在  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AttachmentService.get_attachment()` 方法
3. 確認拋出預期的異常

**測試角色**：系統  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ATTACHMENTSERVICE-007**

**測試目標**：TC-07: 上傳者刪除自己的附件  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AttachmentService.delete_attachment()` 方法
3. 驗證結果符合預期

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ATTACHMENTSERVICE-008**

**測試目標**：TC-08: 管理員刪除附件  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AttachmentService.delete_attachment()` 方法
3. 驗證結果符合預期

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ATTACHMENTSERVICE-009**

**測試目標**：TC-09: 非上傳者且非管理員不能刪除  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AttachmentService.delete_attachment()` 方法
3. 確認拋出預期的異常

**測試角色**：平台管理員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ATTACHMENTSERVICE-010**

**測試目標**：TC-10: 刪除不存在的附件  
**測試方法**：錯誤推測 (Error Guessing)  
**測試步驟**：
1. 準備測試環境（Mock 必要的依賴對象）
2. 呼叫 `AttachmentService.delete_attachment()` 方法
3. 確認拋出預期的異常

**測試角色**：一般會員  
**測試流程**：
- 準備測試環境和測試數據
- 執行被測試的服務方法
- 驗證返回結果符合預期

**測試結果**：✅ 通過

---

**測試編號：UT-ATTACHMENTSERVICE-011**

**測試目標**：TC-11: 生成公開 URL  
**測試方法**：等價劃分 (Equivalence Partitioning)  
**測試步驟**：
1. 呼叫 `AttachmentService.generate_public_url()` 方法
2. 驗證結果符合預期

**測試角色**：系統  
**測試流程**：
- 準備測試數據
- 執行被測試的服務方法
- 驗證返回結果或異常

**測試結果**：✅ 通過

---

