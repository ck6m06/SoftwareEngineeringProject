# 通知系統觸發條件文檔

## 📋 概述

根據架構文件,系統設計了通知模組來處理各種事件的通知。本文檔說明各類通知的觸發條件與實作狀態。

## 🔔 通知類型與觸發條件

### 1. 申請相關通知 (Application Notifications)

#### 1.1 application_submitted
- **觸發時機**: 當一般會員提交動物領養/送養申請時
- **接收者**: 動物擁有者 (owner_id) 或收容所主要帳號 (primaryAccountUserId)
- **Actor**: 申請人 (applicant_id)
- **Payload 範例**:
```json
{
  "application_id": 123,
  "animal_id": 456,
  "animal_name": "小花",
  "applicant_name": "張三",
  "type": "ADOPTION"
}
```
- **實作位置**: POST /applications 端點
- **當前狀態**: ❌ 未實作

#### 1.2 application_approved
- **觸發時機**: 當審核者核准申請時
- **接收者**: 申請人 (applicant_id)
- **Actor**: 審核者 (reviewer_id)
- **Payload 範例**:
```json
{
  "application_id": 123,
  "animal_id": 456,
  "animal_name": "小花",
  "review_notes": "恭喜!您的申請已通過審核"
}
```
- **實作位置**: POST /applications/{id}/review 端點 (status  APPROVED)
- **當前狀態**: ❌ 未實作

#### 1.3 application_rejected
- **觸發時機**: 當審核者拒絕申請時
- **接收者**: 申請人 (applicant_id)
- **Actor**: 審核者 (reviewer_id)
- **Payload 範例**:
```json
{
  "application_id": 123,
  "animal_id": 456,
  "animal_name": "小花",
  "review_notes": "很抱歉,您的申請未通過審核",
  "reason": "不符合領養條件"
}
```
- **實作位置**: POST /applications/{id}/review 端點 (status  REJECTED)
- **當前狀態**: ❌ 未實作

#### 1.4 application_under_review
- **觸發時機**: 當申請被指派給審核者時
- **接收者**: 申請人 (applicant_id)
- **Actor**: 指派者或系統
- **Payload 範例**:
```json
{
  "application_id": 123,
  "animal_id": 456,
  "assignee_name": "李四"
}
```
- **實作位置**: POST /applications/{id}/assign 端點或審核流程
- **當前狀態**: ❌ 未實作

#### 1.5 rehome_application_received
- **觸發時機**: 當收容所或擁有者收到新的送養申請時
- **接收者**: 動物擁有者 (owner_id)
- **Actor**: 申請人 (applicant_id)
- **Payload 範例**:
```json
{
  "application_id": 123,
  "animal_id": 456,
  "animal_name": "小花",
  "applicant_name": "張三"
}
```
- **實作位置**: POST /applications 端點 (type=REHOME)
- **當前狀態**: ❌ 未實作

### 2. 動物狀態通知 (Animal Status Notifications)

#### 2.1 animal_status_changed
- **觸發時機**: 當動物狀態改變時 (DRAFT  PUBLISHED, PUBLISHED  RETIRED 等)
- **接收者**: 
  - 動物擁有者 (owner_id)
  - 收容所主要帳號 (如果 shelter_id 存在)
- **Actor**: 執行狀態變更的管理員或系統
- **Payload 範例**:
```json
{
  "animal_id": 456,
  "animal_name": "小花",
  "old_status": "SUBMITTED",
  "new_status": "PUBLISHED",
  "changed_by": "管理員"
}
```
- **實作位置**: 
  - PATCH /animals/{id} 端點
  - PATCH /rehomes/{id} 端點
  - Admin 審核端點
- **當前狀態**: ❌ 未實作

### 3. 系統通知 (System Notifications)

#### 3.1 system_notification
- **觸發時機**: 系統廣播或重要訊息
- **接收者**: 指定的使用者或所有使用者
- **Actor**: NULL (系統自動)
- **Payload 範例**:
```json
{
  "title": "系統維護通知",
  "message": "系統將於今晚 23:00 進行維護",
  "priority": "HIGH"
}
```
- **實作位置**: Admin 後台或 Celery 排程任務
- **當前狀態**: ❌ 未實作

### 4. Job 完成通知 (Job Completion Notifications)

#### 4.1 job_completed
- **觸發時機**: 長時間任務完成時 (成功或失敗)
- **接收者**: 任務建立者 (created_by)
- **Actor**: NULL (系統)
- **Payload 範例**:
```json
{
  "job_id": 789,
  "job_type": "shelter_batch_import",
  "status": "SUCCEEDED",
  "result_summary": {
    "total": 100,
    "success": 95,
    "failed": 5
  }
}
```
- **實作位置**: Celery Worker 任務完成回調
- **當前狀態**: ❌ 未實作

### 5. 帳號相關通知

#### 5.1 account_verified
- **觸發時機**: 電子郵件驗證完成
- **接收者**: 使用者本人
- **Actor**: NULL (系統)
- **實作位置**: GET /auth/verify 端點
- **當前狀態**: ❌ 未實作

#### 5.2 password_changed
- **觸發時機**: 密碼變更成功
- **接收者**: 使用者本人
- **Actor**: 使用者本人
- **實作位置**: POST /auth/reset-password 端點
- **當前狀態**: ❌ 未實作

## 📊 實作狀態總覽

| 通知類型 | 優先級 | 當前狀態 |
|---------|--------|---------|
| application_submitted | P1 | ❌ 未實作 |
| application_approved | P1 | ❌ 未實作 |
| application_rejected | P1 | ❌ 未實作 |
| application_under_review | P2 | ❌ 未實作 |
| rehome_application_received | P1 | ❌ 未實作 |
| animal_status_changed | P2 | ❌ 未實作 |
| system_notification | P2 | ❌ 未實作 |
| job_completed | P3 | ❌ 未實作 |
| account_verified | P2 | ❌ 未實作 |
| password_changed | P3 | ❌ 未實作 |

## 🔧 實作建議

### 1. 建立 NotificationService

建議建立 `backend/app/services/notification_service.py`:

```python
from app.models.others import Notification
from app import db

class NotificationService:
    @staticmethod
    def create(recipient_id, type, actor_id=None, payload=None):
        \"\"\"建立通知\"\"\"
        notification = Notification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            type=type,
            payload=payload
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def notify_application_submitted(application):
        \"\"\"申請提交通知\"\"\"
        # 發送給動物擁有者
        pass
    
    @staticmethod
    def notify_application_reviewed(application, review_notes):
        \"\"\"申請審核結果通知\"\"\"
        # 發送給申請人
        pass

notification_service = NotificationService()
```

### 2. 整合到現有端點

在以下位置加入通知觸發:

1. **applications.py**:
   - POST /applications  notify_application_submitted
   - POST /applications/{id}/review  notify_application_reviewed

2. **animals.py / rehomes.py**:
   - PATCH status  notify_animal_status_changed

3. **Celery workers**:
   - Job 完成回調  notify_job_completed

### 3. 前端輪詢或 WebSocket

前端已實作 `NotificationBell.vue` 組件,會定期呼叫:
- GET /notifications?recipient_id={user_id}&read=false

## 📚 相關檔案

- 後端模型: `backend/app/models/others.py` (Notification class)
- 後端 API: `backend/app/blueprints/notifications.py`
- 前端組件: `frontend/src/components/NotificationBell.vue`
- 前端 Store: `frontend/src/stores/notification.ts` (如果有)

## ⚠️ 注意事項

1. **隱私**: 不要在 payload 中包含敏感資訊
2. **效能**: 考慮使用 Redis 快取未讀通知數量
3. **擴充性**: 未來可整合 Email/SMS/Push notification
4. **清理**: 建議定期清理舊通知 (例如 90 天前的已讀通知)

---

最後更新: 2025-10-26
建立者: James (Developer Agent)
