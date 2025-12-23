"""
Admin Blueprint - 管理員 API
"""
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.user import User, UserRole
from app.services.admin_service import admin_service
from app.exceptions import NotFoundError, PermissionDeniedError, ValidationError

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
    stats = admin_service.get_system_statistics()
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
    search = request.args.get('search')
    
    try:
        result = admin_service.list_all_users(
            page=page,
            per_page=per_page,
            role=role,
            search=search
        )
        return jsonify(result), 200
    except ValidationError as e:
        abort(400, message=str(e))


@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@jwt_required()
def ban_user(user_id):
    """
    封禁用戶
    僅管理員可執行
    """
    admin = require_admin()
    
    data = request.get_json() or {}
    reason = data.get('reason', '違反平台規定')
    days = data.get('days', 30)
    
    try:
        user = admin_service.ban_user(
            user_id=user_id,
            admin_id=admin.user_id,
            reason=reason,
            days=days
        )
        
        return jsonify({
            'message': f'用戶已被封禁 {days} 天',
            'user': user.to_dict(),
            'locked_until': user.locked_until.isoformat()
        }), 200
    except NotFoundError as e:
        abort(404, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))


@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@jwt_required()
def unban_user(user_id):
    """
    解除用戶封禁
    僅管理員可執行
    """
    admin = require_admin()
    
    try:
        user = admin_service.unban_user(
            user_id=user_id,
            admin_id=admin.user_id
        )
        
        return jsonify({
            'message': '用戶封禁已解除',
            'user': user.to_dict()
        }), 200
    except NotFoundError as e:
        abort(404, message=str(e))


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
    
    result = admin_service.list_all_animals(
        page=page,
        per_page=per_page,
        status=status,
        include_deleted=include_deleted
    )
    return jsonify(result), 200


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
    
    result = admin_service.list_all_applications(
        page=page,
        per_page=per_page,
        status=status
    )
    return jsonify(result), 200


@admin_bp.route('/audit', methods=['GET'])
@jwt_required()
def list_audit_logs():
    """
    取得審計日誌
    僅管理員可訪問
    支援篩選: actor_id, action, target_type, target_id, shelter_id
    """
    require_admin()
    
    try:
        result = admin_service.list_audit_logs(
            page=request.args.get('page', 1, type=int),
            per_page=request.args.get('per_page', 20, type=int),
            actor_id=request.args.get('actor_id', type=int),
            action=request.args.get('action'),
            target_type=request.args.get('target_type'),
            target_id=request.args.get('target_id', type=int),
            shelter_id=request.args.get('shelter_id', type=int),
            start_date=request.args.get('start_date'),
            end_date=request.args.get('end_date')
        )
        return jsonify(result), 200
    except ValidationError as e:
        abort(400, message=str(e))


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
    
    reviewers = admin_service.get_reviewers()
    return jsonify({'reviewers': reviewers}), 200

