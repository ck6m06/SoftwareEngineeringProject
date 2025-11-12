"""
Email-related Celery Tasks
"""
from typing import Dict, Any

from app.celery import celery
from app.services.email_service import email_service
import logging


@celery.task(bind=True, max_retries=3, retry_backoff=True)
def send_verification_email_task(self, user_email: str, token: str) -> Dict[str, Any]:
    """
    非同步發送 Email 驗證信
    
    Args:
        user_email: 用戶 email
        token: 驗證 token
        
    Returns:
        發送結果
    """
    try:
        email_service.send_verification_email(user_email, token)
        return {
            'success': True,
            'recipient': user_email,
            'email_type': 'verification'
        }
    except Exception as exc:
        # 重試機制 (最多3次)
        if self.request.retries < self.max_retries:
            # 指數退避: 60秒, 120秒, 240秒
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        
        # 如果重試失敗，記錄錯誤但不拋出異常 (避免影響主流程)
        return {
            'success': False,
            'recipient': user_email,
            'email_type': 'verification',
            'error': str(exc)
        }


@celery.task(bind=True, max_retries=3, retry_backoff=True)
def send_password_reset_email_task(self, user_email: str, token: str) -> Dict[str, Any]:
    """
    非同步發送密碼重置郵件
    
    Args:
        user_email: 用戶 email
        token: 重置 token
        
    Returns:
        發送結果
    """
    try:
        email_service.send_password_reset_email(user_email, token)
        return {
            'success': True,
            'recipient': user_email,
            'email_type': 'password_reset'
        }
    except Exception as exc:
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        
        return {
            'success': False,
            'recipient': user_email,
            'email_type': 'password_reset',
            'error': str(exc)
        }


@celery.task(bind=True, max_retries=3, retry_backoff=True)
def send_application_notification_email_task(
    self,
    user_email: str,
    animal_name: str,
    status: str,
    message: str = None,
    contact_info: dict = None
) -> Dict[str, Any]:
    """
    非同步發送申請狀態通知郵件
    
    Args:
        user_email: 用戶 email
        animal_name: 動物名稱
        status: 申請狀態 (approved, rejected, under_review)
        message: 附加訊息
        
    Returns:
        發送結果
    """
    try:
        # log contact info for easier verification in worker logs
        logger = logging.getLogger(__name__)
        try:
            logger.info(
                "send_application_notification_email_task: recipient=%s status=%s contact_info=%s",
                user_email,
                status,
                contact_info
            )
        except Exception:
            # don't fail the task because of logging
            logger.exception('Failed logging contact_info')
        # 根據狀態發送不同郵件
        subject_map = {
            'approved': f'您的領養申請已通過 - {animal_name}',
            'rejected': f'關於您的領養申請 - {animal_name}',
            'under_review': f'您的領養申請審核中 - {animal_name}'
        }
        
        email_service.send_email(
            to=user_email,
            subject=subject_map.get(status, '領養申請狀態更新'),
            template='application_notification',
            context={
                'animal_name': animal_name,
                'status': status,
                'message': message,
                'contact_info': contact_info or {}
            }
        )
        
        return {
            'success': True,
            'recipient': user_email,
            'email_type': 'application_notification',
            'status': status
        }
    except Exception as exc:
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        
        return {
            'success': False,
            'recipient': user_email,
            'email_type': 'application_notification',
            'error': str(exc)
        }


@celery.task(bind=True, max_retries=3, retry_backoff=True)
def send_bulk_notification_email_task(
    self,
    recipients: list,
    subject: str,
    template: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    非同步批量發送郵件
    
    Args:
        recipients: 收件人列表
        subject: 郵件主旨
        template: 郵件模板
        context: 模板變數
        
    Returns:
        發送結果統計
    """
    results = {
        'total': len(recipients),
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    for recipient in recipients:
        try:
            email_service.send_email(
                to=recipient,
                subject=subject,
                template=template,
                context=context
            )
            results['success'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'recipient': recipient,
                'error': str(e)
            })
    
    return results
