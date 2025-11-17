"""
Admin Service - 管理員業務邏輯服務
集中管理系統統計、用戶管理、封禁等管理功能
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from app import db
from app.models.user import User, UserRole
from app.models.animal import Animal
from app.models.application import Application
from app.models.shelter import Shelter
from app.models.others import Job, AuditLog
from app.exceptions import (
    NotFoundError, PermissionDeniedError, ValidationError
)
from app.services.audit_service import audit_service
from sqlalchemy import func


class AdminService:
    """管理員服務類"""
    
    @staticmethod
    def get_system_statistics() -> Dict[str, Any]:
        """
        獲取系統統計資料
        
        Returns:
            Dict[str, Any]: 系統統計數據
        """
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
    
    @staticmethod
    def list_all_users(page: int = 1, per_page: int = 20, role: Optional[str] = None, 
                      search: Optional[str] = None) -> Dict[str, Any]:
        """
        列出所有用戶（支援篩選和搜尋）
        
        Args:
            page: 頁碼
            per_page: 每頁數量
            role: 角色篩選
            search: 搜尋關鍵字（username 或 email）
            
        Returns:
            Dict[str, Any]: 包含用戶列表和分頁資訊
        """
        per_page = min(per_page, 100)
        
        query = User.query.filter_by(deleted_at=None)
        
        if role:
            try:
                role_enum = UserRole(role)
                query = query.filter(User.role == role_enum)
            except ValueError:
                raise ValidationError(f'無效的角色: {role}')
        
        if search:
            query = query.filter(
                db.or_(
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
            'users': [user.to_dict() for user in pagination.items]
        }
    
    @staticmethod
    def ban_user(user_id: int, admin_id: int, reason: str = '違反平台規定', 
                days: int = 30) -> User:
        """
        封禁用戶
        
        Args:
            user_id: 要封禁的用戶 ID
            admin_id: 執行封禁的管理員 ID
            reason: 封禁原因
            days: 封禁天數
            
        Returns:
            User: 被封禁的用戶對象
            
        Raises:
            NotFoundError: 用戶不存在
            PermissionDeniedError: 不能封禁管理員
        """
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError('用戶不存在')
        
        if user.role == UserRole.ADMIN:
            raise PermissionDeniedError('不能封禁管理員')
        
        user.locked_until = datetime.utcnow() + timedelta(days=days)
        db.session.commit()
        
        # 記錄審計日誌
        audit_service.log_user_ban(user_id, admin_id, days, reason)
        
        return user
    
    @staticmethod
    def unban_user(user_id: int, admin_id: int) -> User:
        """
        解除用戶封禁
        
        Args:
            user_id: 要解禁的用戶 ID
            admin_id: 執行解禁的管理員 ID
            
        Returns:
            User: 解禁後的用戶對象
            
        Raises:
            NotFoundError: 用戶不存在
        """
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError('用戶不存在')
        
        user.locked_until = None
        user.failed_login_attempts = 0
        db.session.commit()
        
        # 記錄審計日誌
        audit_service.log(
            action='user.unban',
            actor_id=admin_id,
            target_type='user',
            target_id=user_id
        )
        
        return user
    
    @staticmethod
    def list_all_animals(page: int = 1, per_page: int = 20, status: Optional[str] = None,
                        include_deleted: bool = False) -> Dict[str, Any]:
        """
        列出所有動物（管理員視圖）
        
        Args:
            page: 頁碼
            per_page: 每頁數量
            status: 狀態篩選
            include_deleted: 是否包含已刪除
            
        Returns:
            Dict[str, Any]: 包含動物列表和分頁資訊
        """
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
            'animals': [animal.to_dict(include_relations=True) for animal in pagination.items]
        }
    
    @staticmethod
    def list_all_applications(page: int = 1, per_page: int = 20, 
                             status: Optional[str] = None) -> Dict[str, Any]:
        """
        列出所有申請（管理員視圖）
        
        Args:
            page: 頁碼
            per_page: 每頁數量
            status: 狀態篩選
            
        Returns:
            Dict[str, Any]: 包含申請列表和分頁資訊
        """
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
            'applications': [app.to_dict() for app in pagination.items]
        }
    
    @staticmethod
    def list_audit_logs(page: int = 1, per_page: int = 20, 
                       actor_id: Optional[int] = None,
                       action: Optional[str] = None,
                       target_type: Optional[str] = None,
                       target_id: Optional[int] = None,
                       shelter_id: Optional[int] = None,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        取得審計日誌（支援多種篩選）
        
        Args:
            page: 頁碼
            per_page: 每頁數量
            actor_id: 操作者 ID 篩選
            action: 操作類型篩選（部分匹配）
            target_type: 目標類型篩選
            target_id: 目標 ID 篩選
            shelter_id: 收容所 ID 篩選
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)
            
        Returns:
            Dict[str, Any]: 包含審計日誌列表和分頁資訊
        """
        per_page = min(per_page, 100)
        
        query = AuditLog.query
        
        # 篩選條件
        if actor_id:
            query = query.filter(AuditLog.actor_id == actor_id)
        
        if action:
            query = query.filter(AuditLog.action.like(f'%{action}%'))
        
        if target_type:
            query = query.filter(AuditLog.target_type == target_type)
        
        if target_id:
            query = query.filter(AuditLog.target_id == target_id)
        
        if shelter_id:
            query = query.filter(AuditLog.shelter_id == shelter_id)
        
        # 時間範圍篩選
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(AuditLog.timestamp >= start_datetime)
            except ValueError:
                raise ValidationError('start_date格式錯誤,應為YYYY-MM-DD')
        
        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                # 包含整天,加1天
                end_datetime = end_datetime + timedelta(days=1)
                query = query.filter(AuditLog.timestamp < end_datetime)
            except ValueError:
                raise ValidationError('end_date格式錯誤,應為YYYY-MM-DD')
        
        # 排序並分頁
        pagination = query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 準備返回資料，包含 actor 資訊
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
    
    @staticmethod
    def get_reviewers() -> List[Dict[str, Any]]:
        """
        取得所有可以審核申請的使用者（ADMIN + SHELTER_MEMBER）
        
        Returns:
            List[Dict[str, Any]]: 審核員列表
        """
        # 查詢所有管理員和收容所會員（未刪除且未被封禁）
        reviewers = User.query.filter(
            User.role.in_([UserRole.ADMIN, UserRole.SHELTER_MEMBER]),
            User.deleted_at == None,
            db.or_(User.locked_until == None, User.locked_until < datetime.utcnow())
        ).order_by(User.role.desc(), User.username).all()
        
        return [
            {
                'user_id': r.user_id,
                'username': r.username,
                'email': r.email,
                'role': r.role.value,
                'shelter_id': r.primary_shelter_id if r.role == UserRole.SHELTER_MEMBER else None
            } for r in reviewers
        ]


# 創建全局實例
admin_service = AdminService()
