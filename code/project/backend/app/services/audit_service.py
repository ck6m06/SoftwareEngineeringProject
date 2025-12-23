"""
Audit Service - 審計日誌服務
用於記錄系統中的重要操作
"""
from datetime import datetime
from app import db
from app.models.others import AuditLog
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """審計日誌服務類"""
    
    @staticmethod
    def log(
        action: str,
        actor_id: int = None,
        target_type: str = None,
        target_id: int = None,
        before_state: dict = None,
        after_state: dict = None,
        shelter_id: int = None,
        commit: bool = True
    ):
        """
        記錄審計日誌
        
        Args:
            action: 操作類型 (例如: 'user.login', 'application.approve', 'animal.publish')
            actor_id: 執行操作的用戶ID (可為None表示系統操作)
            target_type: 目標資源類型 (例如: 'user', 'animal', 'application')
            target_id: 目標資源ID
            before_state: 操作前的狀態 (JSON)
            after_state: 操作後的狀態 (JSON)
            shelter_id: 相關收容所ID (如果適用)
            commit: 是否立即提交到資料庫 (預設True)
        
        Returns:
            AuditLog: 創建的審計日誌物件
        """
        try:
            audit_log = AuditLog(
                actor_id=actor_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                before_state=before_state,
                after_state=after_state,
                shelter_id=shelter_id,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(audit_log)
            
            if commit:
                db.session.commit()
                logger.info(f"Audit log created: {action} by user {actor_id}")
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            if commit:
                db.session.rollback()
            # 不拋出異常,避免影響主要業務流程
            return None
    
    @staticmethod
    def log_login(user_id: int, success: bool = True):
        """記錄登入事件"""
        action = 'user.login.success' if success else 'user.login.failed'
        return AuditService.log(
            action=action,
            actor_id=user_id if success else None,
            target_type='user',
            target_id=user_id
        )
    
    @staticmethod
    def log_application_review(application_id: int, reviewer_id: int, old_status: str, new_status: str):
        """記錄申請審核"""
        return AuditService.log(
            action='application.review',
            actor_id=reviewer_id,
            target_type='application',
            target_id=application_id,
            before_state={'status': old_status},
            after_state={'status': new_status}
        )
    
    @staticmethod
    def log_animal_publish(animal_id: int, admin_id: int, old_status: str):
        """記錄動物發布"""
        return AuditService.log(
            action='animal.publish',
            actor_id=admin_id,
            target_type='animal',
            target_id=animal_id,
            before_state={'status': old_status},
            after_state={'status': 'PUBLISHED'}
        )
    
    @staticmethod
    def log_shelter_verify(shelter_id: int, admin_id: int, verified: bool):
        """記錄收容所驗證"""
        return AuditService.log(
            action='shelter.verify' if verified else 'shelter.unverify',
            actor_id=admin_id,
            target_type='shelter',
            target_id=shelter_id,
            shelter_id=shelter_id,
            after_state={'verified': verified}
        )
    
    @staticmethod
    def log_user_ban(target_user_id: int, admin_id: int, days: int, reason: str):
        """記錄用戶封禁"""
        return AuditService.log(
            action='user.ban',
            actor_id=admin_id,
            target_type='user',
            target_id=target_user_id,
            after_state={'days': days, 'reason': reason}
        )
    
    @staticmethod
    def log_data_export(user_id: int, requester_id: int):
        """記錄資料匯出請求"""
        return AuditService.log(
            action='user.data.export',
            actor_id=requester_id,
            target_type='user',
            target_id=user_id
        )
    
    @staticmethod
    def log_data_deletion(user_id: int, requester_id: int):
        """記錄資料刪除請求"""
        return AuditService.log(
            action='user.data.delete',
            actor_id=requester_id,
            target_type='user',
            target_id=user_id
        )


# 創建全局實例
audit_service = AuditService()
