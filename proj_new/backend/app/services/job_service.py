"""
Job Service - 背景任務相關業務邏輯
"""
from datetime import datetime
from flask import current_app
from app import db
from app.models.others import Job, JobStatus
from app.models.application import Application
from app.models.user import User, UserRole
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from sqlalchemy.orm import defer


class JobService:
    """背景任務業務邏輯服務"""

    @staticmethod
    def check_job_permission(user_id, job, operation='view'):
        """
        檢查用戶對任務的權限
        
        Args:
            user_id: 用戶ID
            job: 任務對象
            operation: 操作類型 ('view', 'modify', 'admin')
        
        Returns:
            User: 用戶對象
            
        Raises:
            ValueError: 無權限或用戶不存在
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用戶不存在')
        
        # 管理員有完全權限
        if user.role == UserRole.ADMIN:
            return user
            
        # 如果只要求管理員權限
        if operation == 'admin':
            raise ValueError('僅管理員可執行此操作')
        
        # 普通用戶只能操作自己的任務
        if job.created_by != user_id:
            raise ValueError('無權限查看此任務')
        
        return user

    @staticmethod
    def list_jobs(user_id, page=1, per_page=20, filters=None):
        """
        查詢任務列表
        
        Args:
            user_id: 用戶ID
            page: 頁碼
            per_page: 每頁數量
            filters: 篩選條件
        
        Returns:
            dict: 分頁任務數據
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
                
            filters = filters or {}
            per_page = min(per_page, 100)  # 限制最大每頁數量
            
            # 構建查詢 (保留result_summary以支援前端錯誤顯示)
            query = Job.query.options(defer(Job.payload))  # 只延遲載入payload
            
            # 過濾條件
            job_type = filters.get('type')
            if job_type:
                query = query.filter(Job.type == job_type)
            
            status = filters.get('status')
            if status:
                try:
                    status_enum = JobStatus(status)
                    query = query.filter(Job.status == status_enum)
                except ValueError:
                    raise ValueError(f'無效的狀態: {status}')
            
            # 普通用戶只能看到自己的任務
            created_by = filters.get('created_by')
            if user.role != UserRole.ADMIN:
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
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"List jobs error: {str(e)}")
            raise RuntimeError(f"獲取任務列表失敗: {str(e)}")

    @staticmethod
    def get_job(user_id, job_id):
        """
        取得任務狀態
        
        Args:
            user_id: 用戶ID
            job_id: 任務ID
        
        Returns:
            dict: 任務資料
        """
        try:
            job = Job.query.get(job_id)
            if not job:
                raise ValueError('任務不存在')
            
            # 檢查權限
            JobService.check_job_permission(user_id, job, 'view')
            
            return job.to_dict()
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Get job error: {str(e)}")
            raise RuntimeError(f"獲取任務狀態失敗: {str(e)}")

    @staticmethod
    def retry_job(user_id, job_id):
        """
        重試失敗的任務
        
        Args:
            user_id: 用戶ID
            job_id: 任務ID
        
        Returns:
            dict: 重試結果
        """
        try:
            job = Job.query.get(job_id)
            if not job:
                raise ValueError('任務不存在')
            
            # 檢查權限
            JobService.check_job_permission(user_id, job, 'modify')
            
            # 只能重試失敗的任務
            if job.status != JobStatus.FAILED:
                raise ValueError('只能重試失敗的任務')
            
            # 更新任務狀態
            job.status = JobStatus.PENDING
            job.attempts += 1
            job.result_summary = None
            job.finished_at = None
            db.session.commit()
            
            # TODO: 重新加入 Celery 隊列
            # from app.tasks import retry_job_task
            # retry_job_task.delay(job_id)
            
            return {
                'message': '任務已重新加入隊列',
                'job': job.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Retry job error: {str(e)}")
            raise RuntimeError(f"重試任務失敗: {str(e)}")

    @staticmethod
    def cancel_job(user_id, job_id):
        """
        取消待處理或運行中的任務
        
        Args:
            user_id: 用戶ID
            job_id: 任務ID
        
        Returns:
            dict: 取消結果
        """
        try:
            job = Job.query.get(job_id)
            if not job:
                raise ValueError('任務不存在')
            
            # 檢查權限
            JobService.check_job_permission(user_id, job, 'modify')
            
            # 只能取消待處理或運行中的任務
            if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
                raise ValueError('只能取消待處理或運行中的任務')
            
            # 更新任務狀態
            job.status = JobStatus.FAILED
            job.finished_at = datetime.utcnow()
            job.result_summary = {'error': '任務已被用戶取消'}
            db.session.commit()
            
            # TODO: 通知 Celery Worker 取消任務
            # from app.tasks import cancel_job_task
            # cancel_job_task.delay(job_id)
            
            return {
                'message': '任務已取消',
                'job': job.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Cancel job error: {str(e)}")
            raise RuntimeError(f"取消任務失敗: {str(e)}")

    @staticmethod
    def approve_job(admin_id, job_id, notes=''):
        """
        核准任務
        
        Args:
            admin_id: 管理員ID
            job_id: 任務ID
            notes: 備註
        
        Returns:
            dict: 核准結果
        """
        try:
            job = Job.query.get(job_id)
            if not job:
                raise ValueError('任務不存在')
            
            # 檢查管理員權限
            JobService.check_job_permission(admin_id, job, 'admin')
            
            # 只能核准待處理的任務
            if job.status != JobStatus.PENDING:
                raise ValueError('只能核准待處理的任務')
            
            # 根據任務類型執行相應操作
            if job.type == 'user_data_deletion':
                # 帳號刪除請求
                user_id = job.payload.get('user_id')
                if user_id:
                    target_user = User.query.get(user_id)
                    if target_user:
                        # 軟刪除用戶
                        target_user.deleted_at = datetime.utcnow()
                        
                        # 記錄審計日誌
                        AuditService.log(
                            action='user.deleted.approved',
                            actor_id=admin_id,
                            target_type='user',
                            target_id=user_id,
                            after_state={'approved_by': admin_id, 'notes': notes}
                        )
            
            # 更新任務狀態
            job.status = JobStatus.SUCCEEDED
            job.finished_at = datetime.utcnow()
            job.result_summary = {
                'approved_by': admin_id,
                'approved_at': datetime.utcnow().isoformat(),
                'notes': notes
            }
            
            db.session.commit()
            
            # 發送任務完成通知
            try:
                NotificationService.notify_job_completed(job, 'SUCCEEDED')
            except Exception as notify_error:
                current_app.logger.warning(f'通知發送失敗: {notify_error}')
            
            return {
                'message': '任務已核准',
                'job': job.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Approve job error: {str(e)}")
            raise RuntimeError(f"核准任務失敗: {str(e)}")

    @staticmethod
    def reject_job(admin_id, job_id, reason='管理員拒絕'):
        """
        拒絕任務
        
        Args:
            admin_id: 管理員ID
            job_id: 任務ID
            reason: 拒絕原因
        
        Returns:
            dict: 拒絕結果
        """
        try:
            job = Job.query.get(job_id)
            if not job:
                raise ValueError('任務不存在')
            
            # 檢查管理員權限
            JobService.check_job_permission(admin_id, job, 'admin')
            
            # 只能拒絕待處理的任務
            if job.status != JobStatus.PENDING:
                raise ValueError('只能拒絕待處理的任務')
            
            # 更新任務狀態
            job.status = JobStatus.FAILED
            job.finished_at = datetime.utcnow()
            job.result_summary = {
                'rejected_by': admin_id,
                'rejected_at': datetime.utcnow().isoformat(),
                'reason': reason
            }
            
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='job.rejected',
                actor_id=admin_id,
                target_type='job',
                target_id=job_id,
                after_state={'reason': reason}
            )
            
            # 發送任務失敗通知
            try:
                NotificationService.notify_job_completed(job, 'FAILED')
            except Exception as notify_error:
                current_app.logger.warning(f'通知發送失敗: {notify_error}')
            
            return {
                'message': '任務已拒絕',
                'job': job.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Reject job error: {str(e)}")
            raise RuntimeError(f"拒絕任務失敗: {str(e)}")
