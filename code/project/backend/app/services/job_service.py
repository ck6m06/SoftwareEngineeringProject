"""
Job Service - 背景任務業務邏輯服務
集中管理所有任務相關的業務邏輯
"""
from datetime import datetime
from app.utils.datetime_helper import get_naive_taipei_now
from typing import Optional, Dict, Any
from sqlalchemy.orm import defer
from app import db
from app.models.others import Job, JobStatus
from app.models.user import User, UserRole
from app.exceptions import (
    PermissionDeniedError, NotFoundError, ValidationError
)


class JobService:
    """任務業務邏輯服務類"""
    
    @staticmethod
    def list_jobs(user_id: int, filters: Dict[str, Any]) -> Dict:
        """
        獲取任務列表
        
        Args:
            user_id: 當前使用者 ID
            filters: 篩選條件
                - page: 頁碼
                - per_page: 每頁數量
                - type: 任務類型
                - status: 任務狀態
                - created_by: 創建者 ID (僅管理員可用)
                
        Returns:
            dict: 包含任務列表和分頁資訊
        """
        user = db.session.get(User, user_id)
        
        page = filters.get('page', 1)
        per_page = min(filters.get('per_page', 20), 100)
        job_type = filters.get('type')
        status = filters.get('status')
        created_by = filters.get('created_by')
        
        # 構建查詢 (延遲載入 payload)
        query = Job.query.options(defer(Job.payload))
        
        # 過濾條件
        if job_type:
            query = query.filter(Job.type == job_type)
        
        if status:
            try:
                status_enum = JobStatus(status)
                query = query.filter(Job.status == status_enum)
            except ValueError:
                raise ValidationError(f'無效的狀態: {status}')
        
        # 權限過濾
        if user and user.role != UserRole.ADMIN:
            # 普通用戶只能看到自己的任務
            query = query.filter(Job.created_by == user_id)
        elif created_by:
            # 管理員可以篩選特定用戶的任務
            query = query.filter(Job.created_by == created_by)
        
        # 排序並分頁
        query = query.order_by(Job.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'jobs': [job.to_dict() for job in pagination.items]
        }
    
    @staticmethod
    def get_job(job_id: int, user_id: int) -> Job:
        """
        獲取任務詳情
        
        Args:
            job_id: 任務 ID
            user_id: 當前使用者 ID
            
        Returns:
            Job: 任務物件
            
        Raises:
            NotFoundError: 任務不存在
            PermissionDeniedError: 無權限
        """
        job = db.session.get(Job, job_id)
        
        if not job:
            raise NotFoundError('任務不存在')
        
        # 檢查權限
        user = db.session.get(User, user_id)
        if user and user.role != UserRole.ADMIN:
            if job.created_by != user_id:
                raise PermissionDeniedError('無權限查看此任務')
        
        return job
    
    @staticmethod
    def retry_job(job_id: int, user_id: int) -> Job:
        """
        重試失敗的任務
        
        Args:
            job_id: 任務 ID
            user_id: 當前使用者 ID
            
        Returns:
            Job: 更新後的任務物件
            
        Raises:
            NotFoundError: 任務不存在
            PermissionDeniedError: 無權限
            ValidationError: 任務狀態不允許重試
        """
        job = db.session.get(Job, job_id)
        
        if not job:
            raise NotFoundError('任務不存在')
        
        # 檢查權限
        user = db.session.get(User, user_id)
        if user and user.role != UserRole.ADMIN:
            if job.created_by != user_id:
                raise PermissionDeniedError('無權限操作此任務')
        
        # 只能重試失敗的任務
        if job.status != JobStatus.FAILED:
            raise ValidationError('只能重試失敗的任務')
        
        # 更新任務狀態
        job.status = JobStatus.PENDING
        job.attempts += 1
        job.result_summary = None
        job.finished_at = None
        db.session.commit()
        
        # TODO: 重新加入 Celery 隊列
        # from app.tasks import retry_job_task
        # retry_job_task.delay(job_id)
        
        return job
    
    @staticmethod
    def cancel_job(job_id: int, user_id: int) -> Job:
        """
        取消任務
        
        Args:
            job_id: 任務 ID
            user_id: 當前使用者 ID
            
        Returns:
            Job: 更新後的任務物件
            
        Raises:
            NotFoundError: 任務不存在
            PermissionDeniedError: 無權限
            ValidationError: 任務狀態不允許取消
        """
        job = db.session.get(Job, job_id)
        
        if not job:
            raise NotFoundError('任務不存在')
        
        # 檢查權限
        user = db.session.get(User, user_id)
        if user and user.role != UserRole.ADMIN:
            if job.created_by != user_id:
                raise PermissionDeniedError('無權限操作此任務')
        
        # 只能取消待處理或運行中的任務
        if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
            raise ValidationError('只能取消待處理或運行中的任務')
        
        # 更新任務狀態
        job.status = JobStatus.FAILED
        job.finished_at = get_naive_taipei_now()
        job.result_summary = {'error': '任務已被用戶取消'}
        db.session.commit()
        
        # TODO: 通知 Celery Worker 取消任務
        # from app.tasks import cancel_job_task
        # cancel_job_task.delay(job_id)
        
        return job
    
    @staticmethod
    def approve_job(job_id: int, admin_id: int, notes: str = '') -> Job:
        """
        核准任務 (僅管理員)
        
        Args:
            job_id: 任務 ID
            admin_id: 管理員 ID
            notes: 審核備註
            
        Returns:
            Job: 更新後的任務物件
            
        Raises:
            NotFoundError: 任務不存在
            PermissionDeniedError: 非管理員
            ValidationError: 任務狀態不允許核准
        """
        user = db.session.get(User, admin_id)
        
        # 檢查管理員權限
        if not user or user.role != UserRole.ADMIN:
            raise PermissionDeniedError('僅管理員可執行此操作')
        
        job = db.session.get(Job, job_id)
        
        if not job:
            raise NotFoundError('任務不存在')
        
        # 只能核准待處理的任務
        if job.status != JobStatus.PENDING:
            raise ValidationError('只能核准待處理的任務')
        
        # 根據任務類型執行相應操作
        if job.type == 'user_data_deletion':
            # 帳號刪除請求
            user_id = job.payload.get('user_id')
            if user_id:
                target_user = db.session.get(User, user_id)
                if target_user:
                    # 軟刪除用戶
                    target_user.deleted_at = get_naive_taipei_now()
                    
                    # 記錄審計日誌
                    from app.services.audit_service import audit_service
                    audit_service.log(
                        action='user.deleted.approved',
                        actor_id=admin_id,
                        target_type='user',
                        target_id=user_id,
                        after_state={'approved_by': admin_id, 'notes': notes}
                    )
        
        # 更新任務狀態
        job.status = JobStatus.SUCCEEDED
        job.finished_at = get_naive_taipei_now()
        job.result_summary = {
            'approved_by': admin_id,
            'approved_at': get_naive_taipei_now().isoformat(),
            'notes': notes
        }
        
        db.session.commit()
        
        # 發送通知
        try:
            from app.services.notification_service import notification_service
            notification_service.notify_job_completed(job, 'SUCCEEDED')
        except Exception as e:
            print(f'通知發送失敗: {e}')
        
        return job
    
    @staticmethod
    def reject_job(job_id: int, admin_id: int, reason: str = '管理員拒絕') -> Job:
        """
        拒絕任務 (僅管理員)
        
        Args:
            job_id: 任務 ID
            admin_id: 管理員 ID
            reason: 拒絕原因
            
        Returns:
            Job: 更新後的任務物件
            
        Raises:
            NotFoundError: 任務不存在
            PermissionDeniedError: 非管理員
            ValidationError: 任務狀態不允許拒絕
        """
        user = db.session.get(User, admin_id)
        
        # 檢查管理員權限
        if not user or user.role != UserRole.ADMIN:
            raise PermissionDeniedError('僅管理員可執行此操作')
        
        job = db.session.get(Job, job_id)
        
        if not job:
            raise NotFoundError('任務不存在')
        
        # 只能拒絕待處理的任務
        if job.status != JobStatus.PENDING:
            raise ValidationError('只能拒絕待處理的任務')
        
        # 更新任務狀態
        job.status = JobStatus.FAILED
        job.finished_at = get_naive_taipei_now()
        job.result_summary = {
            'rejected_by': admin_id,
            'rejected_at': get_naive_taipei_now().isoformat(),
            'reason': reason
        }
        
        db.session.commit()
        
        # 記錄審計日誌
        from app.services.audit_service import audit_service
        audit_service.log(
            action='job.rejected',
            actor_id=admin_id,
            target_type='job',
            target_id=job_id,
            after_state={'reason': reason}
        )
        
        # 發送通知
        try:
            from app.services.notification_service import notification_service
            notification_service.notify_job_completed(job, 'FAILED')
        except Exception as e:
            print(f'通知發送失敗: {e}')
        
        return job


# 創建全局實例
job_service = JobService()
