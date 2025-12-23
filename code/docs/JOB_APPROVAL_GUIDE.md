# Job 審核功能使用說明

## 功能概述
管理員可以審核用戶提交的帳號刪除請求,包括核准或拒絕操作。

## 使用流程

### 1. 用戶提交刪除請求
用戶在個人設定頁面點擊「刪除帳號」按鈕,系統會建立一個 Job:
`
POST /api/users/{user_id}/data/delete
回應: { "job_id": 5, "message": "資料刪除請求已提交,需要管理員審核" }
`

### 2. 管理員查看待審核任務
1. 登入管理員帳號
2. 前往「任務狀態」頁面 (/jobs)
3. 點擊「待處理」標籤,查看所有 PENDING 狀態的任務
4. 「帳號刪除請求」類型的任務會顯示「核准」和「拒絕」按鈕

### 3. 核准刪除請求
1. 點擊「核准」按鈕
2. 在彈出的模態框中可選填備註
3. 點擊「確認核准」
4. 系統會:
   - 執行用戶軟刪除 (設定 deleted_at 時間戳)
   - 更新 Job 狀態為 SUCCEEDED
   - 記錄審計日誌
5. 任務列表自動刷新,該任務移至「已完成」標籤

### 4. 拒絕刪除請求
1. 點擊「拒絕」按鈕
2. 在彈出的模態框中**必須填寫**拒絕理由
3. 點擊「確認拒絕」
4. 系統會:
   - 更新 Job 狀態為 FAILED
   - 記錄拒絕原因和審計日誌
   - 用戶帳號不會被刪除
5. 任務列表自動刷新,該任務移至「失敗」標籤

## API 端點

### 核准任務
`
POST /api/jobs/{job_id}/approve
Headers: Authorization: Bearer <admin_token>
Body: { "notes": "備註內容" }  // 選填

回應:
{
  "message": "任務已核准",
  "job": {
    "job_id": 5,
    "status": "SUCCEEDED",
    "result_summary": {
      "approved_by": 24,
      "approved_at": "2025-10-26T11:09:53",
      "notes": "備註內容"
    }
  }
}
`

### 拒絕任務
`
POST /api/jobs/{job_id}/reject
Headers: Authorization: Bearer <admin_token>
Body: { "reason": "拒絕原因" }  // 必填

回應:
{
  "message": "任務已拒絕",
  "job": {
    "job_id": 6,
    "status": "FAILED",
    "result_summary": {
      "rejected_by": 24,
      "rejected_at": "2025-10-26T11:10:30",
      "reason": "拒絕原因"
    }
  }
}
`

## 權限要求
- 只有 **ADMIN** 角色的用戶可以執行核准/拒絕操作
- 其他角色訪問會返回 403 Forbidden

## 需要審核的任務類型
目前需要管理員審核的任務包括:
- user_data_deletion - 帳號刪除請求
- data_export - 資料匯出請求 (未來功能)
- atch_update - 批次更新操作 (未來功能)

## 測試帳號
- 管理員: admin@test.com / Admin123
