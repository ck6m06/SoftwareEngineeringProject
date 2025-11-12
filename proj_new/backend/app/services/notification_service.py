"""
Notification Service
處理通知的建立與發送
"""
from datetime import datetime
from app import db
from app.models.others import Notification


class NotificationService:
    """通知服務類別"""
    
    @staticmethod
    def create(recipient_id: int, type: str, actor_id: int = None, payload: dict = None, commit: bool = True):
        """
        建立通知
        
        Args:
            recipient_id: 接收者 user_id
            type: 通知類型 (例如 'application_submitted')
            actor_id: 執行動作的 user_id (可為 None 表示系統通知)
            payload: 通知的額外資料 (JSON)
            commit: 是否立即提交到資料庫
            
        Returns:
            Notification: 建立的通知物件
        """
        try:
            notification = Notification(
                recipient_id=recipient_id,
                actor_id=actor_id,
                type=type,
                payload=payload or {},
                read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
            
            if commit:
                db.session.commit()
            
            return notification
        except Exception as e:
            if commit:
                db.session.rollback()
            raise e
    
    @staticmethod
    def notify_application_submitted(application, applicant_name: str, animal_name: str):
        """
        申請提交通知 - 發送給動物擁有者
        
        Args:
            application: Application 物件
            applicant_name: 申請人姓名
            animal_name: 動物名稱
        """
        from app.models.animal import Animal
        
        animal = Animal.query.get(application.animal_id)
        if not animal:
            return None
        
        # 確定接收者 (優先 owner_id, 其次 shelter 的 primaryAccountUserId)
        recipient_id = animal.owner_id
        if not recipient_id and animal.shelter_id:
            from app.models.shelter import Shelter
            shelter = Shelter.query.get(animal.shelter_id)
            if shelter:
                recipient_id = shelter.primary_account_user_id
        
        if not recipient_id:
            return None
        
        payload = {
            'application_id': application.application_id,
            'animal_id': application.animal_id,
            'animal_name': animal_name,
            'applicant_name': applicant_name,
            'type': application.type.value if hasattr(application.type, 'value') else application.type
        }
        
        return NotificationService.create(
            recipient_id=recipient_id,
            type='application_submitted',
            actor_id=application.applicant_id,
            payload=payload
        )
    
    @staticmethod
    def notify_application_reviewed(application, reviewer_id: int, status: str, review_notes: str = None):
        """
        申請審核結果通知 - 發送給申請人
        
        Args:
            application: Application 物件
            reviewer_id: 審核者 user_id
            status: 審核結果 ('APPROVED' 或 'REJECTED')
            review_notes: 審核備註
        """
        from app.models.animal import Animal
        
        animal = Animal.query.get(application.animal_id)
        animal_name = animal.name if animal else '未知動物'
        
        # 根據狀態選擇通知類型
        notification_type = 'application_approved' if status == 'APPROVED' else 'application_rejected'
        
        payload = {
            'application_id': application.application_id,
            'animal_id': application.animal_id,
            'animal_name': animal_name,
            'status': status,
            'review_notes': review_notes
        }
        
        return NotificationService.create(
            recipient_id=application.applicant_id,
            type=notification_type,
            actor_id=reviewer_id,
            payload=payload
        )
    
    @staticmethod
    def notify_application_under_review(application, assignee_id: int, assignee_name: str):
        """
        申請進入審核通知 - 發送給申請人
        
        Args:
            application: Application 物件
            assignee_id: 指派審核者 user_id
            assignee_name: 審核者姓名
        """
        from app.models.animal import Animal
        
        animal = Animal.query.get(application.animal_id)
        animal_name = animal.name if animal else '未知動物'
        
        payload = {
            'application_id': application.application_id,
            'animal_id': application.animal_id,
            'animal_name': animal_name,
            'assignee_name': assignee_name
        }
        
        return NotificationService.create(
            recipient_id=application.applicant_id,
            type='application_under_review',
            actor_id=assignee_id,
            payload=payload
        )
    
    @staticmethod
    def notify_animal_status_changed(animal, old_status: str, new_status: str, changed_by_id: int = None):
        """
        動物狀態變更通知 - 發送給擁有者
        
        Args:
            animal: Animal 物件
            old_status: 舊狀態
            new_status: 新狀態
            changed_by_id: 變更者 user_id
        """
        # 確定接收者
        recipient_id = animal.owner_id
        if not recipient_id and animal.shelter_id:
            from app.models.shelter import Shelter
            shelter = Shelter.query.get(animal.shelter_id)
            if shelter:
                recipient_id = shelter.primary_account_user_id
        
        if not recipient_id:
            return None
        
        payload = {
            'animal_id': animal.animal_id,
            'animal_name': animal.name,
            'old_status': old_status,
            'new_status': new_status
        }
        
        return NotificationService.create(
            recipient_id=recipient_id,
            type='animal_status_changed',
            actor_id=changed_by_id,
            payload=payload
        )
    
    @staticmethod
    def notify_job_completed(job, status: str):
        """
        Job 完成通知 - 發送給建立者
        
        Args:
            job: Job 物件
            status: 完成狀態 ('SUCCEEDED' 或 'FAILED')
        """
        if not job.created_by:
            return None
        
        payload = {
            'job_id': job.job_id,
            'job_type': job.type,
            'status': status,
            'result_summary': job.result_summary
        }
        
        return NotificationService.create(
            recipient_id=job.created_by,
            type='job_completed',
            actor_id=None,  # 系統通知
            payload=payload
        )
    
    @staticmethod
    def notify_system(recipient_id: int, title: str, message: str, priority: str = 'NORMAL'):
        """
        系統通知
        
        Args:
            recipient_id: 接收者 user_id
            title: 通知標題
            message: 通知訊息
            priority: 優先級 ('LOW', 'NORMAL', 'HIGH')
        """
        payload = {
            'title': title,
            'message': message,
            'priority': priority
        }
        
        return NotificationService.create(
            recipient_id=recipient_id,
            type='system_notification',
            actor_id=None,  # 系統通知
            payload=payload
        )


# 建立全域實例
notification_service = NotificationService()
