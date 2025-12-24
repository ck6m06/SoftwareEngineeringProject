# 📁 Docs 資料夾結構說明

## 資料夾分類

### 📊 api-tests/ (8 個檔案)
API 測試相關檔案
- `api_medical_*.json` - 醫療紀錄 API 測試資料
- `api_token*.txt` - API Token 檔案
- `API_TEST_REPORT.md` - API 測試報告
- `API_VALIDATION_REPORT.md` - API 驗證報告

### 📝 logs/ (7 個檔案)
系統運行日誌檔案
- `backend_logs*.txt` - 後端日誌
- `frontend_logs*.txt` - 前端日誌

### 📖 guides/ (4 個檔案)
操作指南和說明文件
- `CELERY_WORKER_GUIDE.md` - Celery Worker 使用指南
- `CREATE_TEST_ACCOUNTS_GUIDE.md` - 測試帳號創建指南
- `JOB_APPROVAL_GUIDE.md` - 工作審核指南
- `NOTIFICATION_TRIGGERS_GUIDE.md` - 通知觸發指南

### 🧪 test-plans/ (12 個檔案)
測試計畫和清單
- `PHASE1-9_TEST_GUIDE.md` - 各階段測試指南（9 個檔案）
- `TEST_ACCOUNTS.md` - 測試帳號列表
- `TEST_READY_REPORT.md` - 測試準備報告
- `FRONTEND_TEST_CHECKLIST.md` - 前端測試清單

### 📋 reports/ (9 個檔案)
各類報告文件
- `ARCHITECTURE_REVIEW.md` - 架構審查報告
- `DEPLOYMENT_SUCCESS.md` - 部署成功報告
- `IMPLEMENTATION_PLAN.md` - 實作計畫
- `*_REPORT.md` - 各類專案報告

### 🔧 fixes/ (4 個檔案)
修復和問題解決文件
- `FIXES.md` - 修復記錄
- `*_FIX.md` - 特定問題修復文件
- `ISSUES_AND_SOLUTIONS.md` - 問題與解決方案

### 🔄 refactoring/ (4 個檔案)
重構相關文件
- `REFACTORING_GUIDE.md` - 重構指南
- `REFACTORING_COMPLETE.md` - 重構完成報告
- `REFACTORING_EXAMPLE.md` - 重構範例
- `REFACTORING_PROGRESS.md` - 重構進度
- `migrate-data.ps1` - 資料遷移腳本
- `test-all-endpoints.ps1` - 全端點測試腳本
- `test-api.ps1` - API 測試腳本
- `test-audit.ps1` - 審計測試腳本
- `test-email-verify.ps1` - Email 驗證測試腳本
- `test_batch_upload.py` - 批次上傳測試腳本
### 🎨 components/ (2 個檔案)
Vue 組件檔案（臨時存放）
- `MedicalRecords_*.vue` - 醫療紀錄相關組件

## 根目錄保留檔案

- `README.md` - 專案說明文件
- `development.md` - 開發文件
- `SEQUENCE_DIAGRAMS_README.md` - 序列圖說明
- `FOLDER_STRUCTURE.md` - 本文件（資料夾結構說明）
使用建議

1. **查找 API 測試資料** → 前往 `api-tests/`
2. **查看系統日誌** → 前往 `logs/`
3. **閱讀操作指南** → 前往 `guides/`
4. **查看測試計畫** → 前往 `test-plans/`
5. **查閱專案報告** → 前往 `reports/`
6. **查看修復記錄** → 前往 `fixes/`
7. **了解重構進度** → 前往 `refactoring/`
8. **執行腳本** → 前往 `scripts/`

---
*最後更新: 2025-12-25*
