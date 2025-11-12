"""
Admin Blueprint - 管理員 API
"""
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.user import User, UserRole
from app.models.animal import Animal
from app.models.application import Application
from app.models.shelter import Shelter
from app.models.others import Job, AuditLog
from app.services.audit_service import audit_service
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, description='管理員 API')


def require_admin():
    """檢查管理員權限的裝飾器功能"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user or user.role != UserRole.ADMIN:
        abort(403, message='僅管理員可執行此操作')
    
    return user


@admin_bp.route('/stats', methods=['GET'])
@admin_bp.route('/statistics', methods=['GET'])  # 別名支援
@jwt_required()
def get_system_stats():
    """
    獲取系統統計資料
    僅管理員可訪問
    """
    require_admin()
    
    # 統計各種資源數量
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
    
    return jsonify(stats), 200


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_all_users():
    """
    列出所有用戶 (含篩選)
    僅管理員可訪問
    """
    require_admin()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')
    search = request.args.get('search')  # 搜尋 username 或 email
    
    per_page = min(per_page, 100)
    
    query = User.query.filter_by(deleted_at=None)
    
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            abort(400, message=f'無效的角色: {role}')
    
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
    
    return jsonify({
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'users': [user.to_dict() for user in pagination.items]
    }), 200


@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@jwt_required()
def ban_user(user_id):
    """
    封禁用戶
    僅管理員可執行
    """
    admin = require_admin()
    
    user = User.query.get(user_id)
    if not user:
        abort(404, message='用戶不存在')
    
    if user.role == UserRole.ADMIN:
        abort(403, message='不能封禁管理員')
    
    data = request.get_json() or {}
    reason = data.get('reason', '違反平台規定')
    days = data.get('days', 30)  # 預設封禁30天
    
    user.locked_until = datetime.utcnow() + timedelta(days=days)
    db.session.commit()
    
    # 記錄審計日誌
    audit_service.log_user_ban(user_id, admin.user_id, days, reason)
    
    return jsonify({
        'message': f'用戶已被封禁 {days} 天',
        'user': user.to_dict(),
        'locked_until': user.locked_until.isoformat()
    }), 200


@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@jwt_required()
def unban_user(user_id):
    """
    解除用戶封禁
    僅管理員可執行
    """
    require_admin()
    
    user = User.query.get(user_id)
    if not user:
        abort(404, message='用戶不存在')
    
    user.locked_until = None
    user.failed_login_attempts = 0
    db.session.commit()
    
    # 記錄審計日誌
    audit_service.log(
        action='user.unban',
        actor_id=require_admin().user_id,
        target_type='user',
        target_id=user_id
    )
    
    return jsonify({
        'message': '用戶封禁已解除',
        'user': user.to_dict()
    }), 200


@admin_bp.route('/animals', methods=['GET'])
@jwt_required()
def list_all_animals():
    """
    列出所有動物 (含已刪除)
    僅管理員可訪問
    """
    require_admin()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    
    per_page = min(per_page, 100)
    
    query = Animal.query
    
    if not include_deleted:
        query = query.filter_by(deleted_at=None)
    
    if status:
        query = query.filter(Animal.status == status)
    
    pagination = query.order_by(Animal.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'animals': [animal.to_dict(include_relations=True) for animal in pagination.items]
    }), 200


@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
def list_all_applications():
    """
    列出所有申請
    僅管理員可訪問
    """
    require_admin()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    per_page = min(per_page, 100)
    
    query = Application.query.filter_by(deleted_at=None)
    
    if status:
        query = query.filter(Application.status == status)
    
    pagination = query.order_by(Application.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'applications': [app.to_dict() for app in pagination.items]
    }), 200


@admin_bp.route('/audit', methods=['GET'])
@jwt_required()
def list_audit_logs():
    """
    取得審計日誌
    僅管理員可訪問
    支援篩選: actor_id, action, target_type, target_id, shelter_id
    """
    require_admin()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)
    
    # 建立查詢
    query = AuditLog.query
    
    # 篩選條件
    actor_id = request.args.get('actor_id', type=int)
    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)
    
    action = request.args.get('action')
    if action:
        query = query.filter(AuditLog.action.like(f'%{action}%'))
    
    target_type = request.args.get('target_type')
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)
    
    target_id = request.args.get('target_id', type=int)
    if target_id:
        query = query.filter(AuditLog.target_id == target_id)
    
    shelter_id = request.args.get('shelter_id', type=int)
    if shelter_id:
        query = query.filter(AuditLog.shelter_id == shelter_id)
    
    # 時間範圍篩選
    start_date = request.args.get('start_date')
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(AuditLog.timestamp >= start_datetime)
        except ValueError:
            abort(400, message='start_date格式錯誤,應為YYYY-MM-DD')
    
    end_date = request.args.get('end_date')
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            # 包含整天,加1天
            from datetime import timedelta
            end_datetime = end_datetime + timedelta(days=1)
            query = query.filter(AuditLog.timestamp < end_datetime)
        except ValueError:
            abort(400, message='end_date格式錯誤,應為YYYY-MM-DD')
    
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
    
    return jsonify({
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
        'audit_logs': logs_with_actor
    }), 200


@admin_bp.route('/reviewers', methods=['GET'])
@jwt_required()
def get_reviewers():
    """
    取得所有可以審核申請的使用者 (ADMIN + SHELTER_MEMBER)
    僅管理員和收容所會員可訪問
    """
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user or user.role not in [UserRole.ADMIN, UserRole.SHELTER_MEMBER]:
        abort(403, message='僅管理員和收容所會員可訪問')
    
    # 查詢所有管理員和收容所會員 (未刪除且未被封禁)
    reviewers = User.query.filter(
        User.role.in_([UserRole.ADMIN, UserRole.SHELTER_MEMBER]),
        User.deleted_at == None,
        db.or_(User.locked_until == None, User.locked_until < datetime.utcnow())
    ).order_by(User.role.desc(), User.username).all()
    
    return jsonify({
        'reviewers': [
            {
                'user_id': r.user_id,
                'username': r.username,
                'email': r.email,
                'role': r.role.value,
                'shelter_id': r.primary_shelter_id if r.role == UserRole.SHELTER_MEMBER else None
            } for r in reviewers
        ]
    }), 200

