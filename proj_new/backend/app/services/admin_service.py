"""
Admin Service - 管理員相關業務邏輯
"""
from datetime import datetime, timedelta
from flask import current_app
from app import db
from app.models.user import User, UserRole
from app.models.animal import Animal
from app.models.application import Application
from app.models.shelter import Shelter
from app.models.others import Job, JobStatus, Notification, AuditLog
from app.services.audit_service import AuditService
from sqlalchemy import func, or_


class AdminService:
    """管理員業務邏輯服務"""

    @staticmethod
    def get_system_statistics():
        """
        獲取系統統計資料
        
        Returns:
            dict: 系統統計數據
        """
        try:
            stats = {
                'users': {
                    'total': User.query.filter_by(deleted_at=None).count(),
                    'by_role': {
                        'general': User.query.filter_by(role=UserRole.GENERAL_MEMBER, deleted_at=None).count(),
                        'shelter_member': User.query.filter_by(role=UserRole.SHELTER_MEMBER, deleted_at=None).count(),
                        'admin': User.query.filter_by(role=UserRole.ADMIN, deleted_at=None).count(),
                    }
                },
                'animals': {
                    'total': Animal.query.filter_by(deleted_at=None).count(),
                    'published': Animal.query.filter_by(status='PUBLISHED', deleted_at=None).count(),
                },
                'applications': {
                    'total': Application.query.filter_by(deleted_at=None).count(),
                    'pending': Application.query.filter_by(status='PENDING', deleted_at=None).count(),
                    'approved': Application.query.filter_by(status='APPROVED', deleted_at=None).count(),
                },
                'shelters': {
                    'total': Shelter.query.filter_by(deleted_at=None).count(),
                    'verified': Shelter.query.filter_by(verified=True, deleted_at=None).count(),
                },
                'jobs': {
                    'total': Job.query.count(),
                    'pending': Job.query.filter_by(status='PENDING').count(),
                    'running': Job.query.filter_by(status='RUNNING').count(),
                    'failed': Job.query.filter_by(status='FAILED').count(),
                }
            }
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f"Get system statistics error: {str(e)}")
            raise RuntimeError(f"獲取系統統計失敗: {str(e)}")

    @staticmethod
    def list_users(page=1, per_page=20, role=None, search=None):
        """
        列出所有用戶
        
        Args:
            page: 頁碼
            per_page: 每頁數量
            role: 角色篩選
            search: 搜尋關鍵字
        
        Returns:
            dict: 分頁用戶資料
        """
        try:
            per_page = min(per_page, 100)
            
            query = User.query.filter_by(deleted_at=None)
            
            if role:
                try:
                    role_enum = UserRole(role)
                    query = query.filter(User.role == role_enum)
                except ValueError:
                    raise ValueError(f'無效的角色: {role}')
            
            if search:
                query = query.filter(
                    or_(
                        User.username.ilike(f'%{search}%'),
                        User.email.ilike(f'%{search}%')
                    )
                )
            
            pagination = query.order_by(User.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages,
                'users': [user.to_dict() for user in pagination.items]
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"List users error: {str(e)}")
            raise RuntimeError(f"獲取用戶列表失敗: {str(e)}")

    @staticmethod
    def ban_user(admin_id, user_id, days=30, reason='違反平台規定'):
        """
        封禁用戶
        
        Args:
            admin_id: 執行操作的管理員ID
            user_id: 被封禁的用戶ID
            days: 封禁天數
            reason: 封禁原因
        
        Returns:
            dict: 封禁結果
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            if user.role == UserRole.ADMIN:
                raise ValueError('不能封禁管理員')
            
            user.locked_until = datetime.utcnow() + timedelta(days=days)
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='user.ban',
                actor_id=admin_id,
                target_type='user',
                target_id=user_id,
                before_state=None,
                after_state={
                    'locked_until': user.locked_until.isoformat(),
                    'days': days,
                    'reason': reason
                }
            )
            
            return {
                'message': f'用戶已被封禁 {days} 天',
                'user': user.to_dict(),
                'locked_until': user.locked_until.isoformat()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Ban user error: {str(e)}")
            raise RuntimeError(f"封禁用戶失敗: {str(e)}")

    @staticmethod
    def unban_user(admin_id, user_id):
        """
        解除用戶封禁
        
        Args:
            admin_id: 執行操作的管理員ID
            user_id: 用戶ID
        
        Returns:
            dict: 解封結果
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            user.locked_until = None
            user.failed_login_attempts = 0
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='user.unban',
                actor_id=admin_id,
                target_type='user',
                target_id=user_id
            )
            
            return {
                'message': '用戶封禁已解除',
                'user': user.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unban user error: {str(e)}")
            raise RuntimeError(f"解封用戶失敗: {str(e)}")

    @staticmethod
    def list_animals(page=1, per_page=20, status=None, include_deleted=False):
        """
        列出所有動物
        
        Args:
            page: 頁碼
            per_page: 每頁數量
            status: 狀態篩選
            include_deleted: 是否包含已刪除
        
        Returns:
            dict: 分頁動物資料
        """
        try:
            per_page = min(per_page, 100)
            
            query = Animal.query
            
            if not include_deleted:
                query = query.filter_by(deleted_at=None)
            
            if status:
                query = query.filter(Animal.status == status)
            
            pagination = query.order_by(Animal.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages,
                'animals': [animal.to_dict(include_relations=True) for animal in pagination.items]
            }
            
        except Exception as e:
            current_app.logger.error(f"List animals error: {str(e)}")
            raise RuntimeError(f"獲取動物列表失敗: {str(e)}")

    @staticmethod
    def list_applications(page=1, per_page=20, status=None):
        """
        列出所有申請
        
        Args:
            page: 頁碼
            per_page: 每頁數量
            status: 狀態篩選
        
        Returns:
            dict: 分頁申請資料
        """
        try:
            per_page = min(per_page, 100)
            
            query = Application.query.filter_by(deleted_at=None)
            
            if status:
                query = query.filter(Application.status == status)
            
            pagination = query.order_by(Application.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages,
                'applications': [app.to_dict() for app in pagination.items]
            }
            
        except Exception as e:
            current_app.logger.error(f"List applications error: {str(e)}")
            raise RuntimeError(f"獲取申請列表失敗: {str(e)}")

    @staticmethod
    def list_audit_logs(page=1, per_page=20, filters=None):
        """
        列出審計日誌
        
        Args:
            page: 頁碼
            per_page: 每頁數量
            filters: 篩選條件 dict
        
        Returns:
            dict: 分頁審計日誌
        """
        try:
            per_page = min(per_page, 100)
            filters = filters or {}
            
            # 建立查詢
            query = AuditLog.query
            
            # 篩選條件
            if filters.get('actor_id'):
                query = query.filter(AuditLog.actor_id == filters['actor_id'])
            
            if filters.get('action'):
                query = query.filter(AuditLog.action.like(f'%{filters["action"]}%'))
            
            if filters.get('target_type'):
                query = query.filter(AuditLog.target_type == filters['target_type'])
            
            if filters.get('target_id'):
                query = query.filter(AuditLog.target_id == filters['target_id'])
            
            if filters.get('shelter_id'):
                query = query.filter(AuditLog.shelter_id == filters['shelter_id'])
            
            # 時間範圍篩選
            if filters.get('start_date'):
                try:
                    start_datetime = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                    query = query.filter(AuditLog.timestamp >= start_datetime)
                except ValueError:
                    raise ValueError('start_date格式錯誤,應為YYYY-MM-DD')
            
            if filters.get('end_date'):
                try:
                    end_datetime = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                    # 包含整天,加1天
                    end_datetime = end_datetime + timedelta(days=1)
                    query = query.filter(AuditLog.timestamp < end_datetime)
                except ValueError:
                    raise ValueError('end_date格式錯誤,應為YYYY-MM-DD')
            
            # 排序並分頁 (最新的在前)
            pagination = query.order_by(AuditLog.timestamp.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 準備返回資料,包含actor資訊
            logs_with_actor = []
            for log in pagination.items:
                log_dict = log.to_dict()
                if log.actor:
                    log_dict['actor'] = {
                        'user_id': log.actor.user_id,
                        'username': log.actor.username,
                        'email': log.actor.email,
                        'role': log.actor.role.value if log.actor.role else None
                    }
                logs_with_actor.append(log_dict)
            
            return {
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages,
                'audit_logs': logs_with_actor
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"List audit logs error: {str(e)}")
            raise RuntimeError(f"獲取審計日誌失敗: {str(e)}")

    @staticmethod
    def get_reviewers():
        """
        取得所有可以審核申請的使用者 (ADMIN + SHELTER_MEMBER)
        
        Returns:
            dict: 審核員列表
        """
        try:
            # 查詢所有管理員和收容所會員 (未刪除且未被封禁)
            reviewers = User.query.filter(
                User.role.in_([UserRole.ADMIN, UserRole.SHELTER_MEMBER]),
                User.deleted_at == None,
                or_(User.locked_until == None, User.locked_until < datetime.utcnow())
            ).order_by(User.role.desc(), User.username).all()
            
            return {
                'reviewers': [
                    {
                        'user_id': r.user_id,
                        'username': r.username,
                        'email': r.email,
                        'role': r.role.value,
                        'shelter_id': r.primary_shelter_id if r.role == UserRole.SHELTER_MEMBER else None
                    } for r in reviewers
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"Get reviewers error: {str(e)}")
            raise RuntimeError(f"獲取審核員列表失敗: {str(e)}")

    @staticmethod
    def verify_admin_permission(user_id):
        """
        驗證管理員權限
        
        Args:
            user_id: 用戶ID
        
        Returns:
            User: 管理員用戶對象
        
        Raises:
            ValueError: 非管理員用戶
        """
        user = User.query.get(user_id)
        
        if not user or user.role != UserRole.ADMIN:
            raise ValueError('僅管理員可執行此操作')
        
        return user

    @staticmethod
    def verify_reviewer_permission(user_id):
        """
        驗證審核員權限 (管理員或收容所會員)
        
        Args:
            user_id: 用戶ID
        
        Returns:
            User: 用戶對象
        
        Raises:
            ValueError: 無權限用戶
        """
        user = User.query.get(user_id)
        
        if not user or user.role not in [UserRole.ADMIN, UserRole.SHELTER_MEMBER]:
            raise ValueError('僅管理員和收容所會員可執行此操作')
        
        return user
