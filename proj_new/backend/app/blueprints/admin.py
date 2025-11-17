"""
Admin Blueprint - 管理員 API
"""
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.admin_service import AdminService

admin_bp = Blueprint('admin', __name__, description='管理員 API')


@admin_bp.route('/stats', methods=['GET'])
@admin_bp.route('/statistics', methods=['GET'])  # 別名支援
@jwt_required()
def get_system_stats():
    """
    獲取系統統計資料
    僅管理員可訪問
    """
    try:
        current_user_id = int(get_jwt_identity())
        AdminService.verify_admin_permission(current_user_id)
        
        stats = AdminService.get_system_statistics()
        return jsonify(stats), 200
        
    except ValueError as e:
        abort(403, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_all_users():
    """
    列出所有用戶 (含篩選)
    僅管理員可訪問
    """
    try:
        current_user_id = int(get_jwt_identity())
        AdminService.verify_admin_permission(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role')
        search = request.args.get('search')  # 搜尋 username 或 email
        
        result = AdminService.list_users(
            page=page,
            per_page=per_page,
            role=role,
            search=search
        )
        return jsonify(result), 200
        
    except ValueError as e:
        if '僅管理員可執行' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@jwt_required()
def ban_user(user_id):
    """
    封禁用戶
    僅管理員可執行
    """
    try:
        current_user_id = int(get_jwt_identity())
        AdminService.verify_admin_permission(current_user_id)
        
        data = request.get_json() or {}
        reason = data.get('reason', '違反平台規定')
        days = data.get('days', 30)  # 預設封禁30天
        
        result = AdminService.ban_user(
            admin_id=current_user_id,
            user_id=user_id,
            days=days,
            reason=reason
        )
        return jsonify(result), 200
        
    except ValueError as e:
        if '僅管理員可執行' in str(e):
            abort(403, message=str(e))
        elif '用戶不存在' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@jwt_required()
def unban_user(user_id):
    """
    解除用戶封禁
    僅管理員可執行
    """
    try:
        current_user_id = int(get_jwt_identity())
        AdminService.verify_admin_permission(current_user_id)
        
        result = AdminService.unban_user(
            admin_id=current_user_id,
            user_id=user_id
        )
        return jsonify(result), 200
        
    except ValueError as e:
        if '僅管理員可執行' in str(e):
            abort(403, message=str(e))
        elif '用戶不存在' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@admin_bp.route('/animals', methods=['GET'])
@jwt_required()
def list_all_animals():
    """
    列出所有動物 (含已刪除)
    僅管理員可訪問
    """
    try:
        current_user_id = int(get_jwt_identity())
        AdminService.verify_admin_permission(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        result = AdminService.list_animals(
            page=page,
            per_page=per_page,
            status=status,
            include_deleted=include_deleted
        )
        return jsonify(result), 200
        
    except ValueError as e:
        abort(403, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
def list_all_applications():
    """
    列出所有申請
    僅管理員可訪問
    """
    try:
        current_user_id = int(get_jwt_identity())
        AdminService.verify_admin_permission(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        result = AdminService.list_applications(
            page=page,
            per_page=per_page,
            status=status
        )
        return jsonify(result), 200
        
    except ValueError as e:
        abort(403, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@admin_bp.route('/audit', methods=['GET'])
@jwt_required()
def list_audit_logs():
    """
    取得審計日誌
    僅管理員可訪問
    支援篩選: actor_id, action, target_type, target_id, shelter_id
    """
    try:
        current_user_id = int(get_jwt_identity())
        AdminService.verify_admin_permission(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 篩選條件
        filters = {}
        for key in ['actor_id', 'action', 'target_type', 'target_id', 'shelter_id', 'start_date', 'end_date']:
            value = request.args.get(key)
            if value:
                if key in ['actor_id', 'target_id', 'shelter_id']:
                    try:
                        filters[key] = int(value)
                    except ValueError:
                        abort(400, message=f'{key} 必須為數字')
                else:
                    filters[key] = value
        
        result = AdminService.list_audit_logs(
            page=page,
            per_page=per_page,
            filters=filters
        )
        return jsonify(result), 200
        
    except ValueError as e:
        if '僅管理員可執行' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@admin_bp.route('/reviewers', methods=['GET'])
@jwt_required()
def get_reviewers():
    """
    取得所有可以審核申請的使用者 (ADMIN + SHELTER_MEMBER)
    僅管理員和收容所會員可訪問
    """
    try:
        current_user_id = int(get_jwt_identity())
        AdminService.verify_reviewer_permission(current_user_id)
        
        result = AdminService.get_reviewers()
        return jsonify(result), 200
        
    except ValueError as e:
        abort(403, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))