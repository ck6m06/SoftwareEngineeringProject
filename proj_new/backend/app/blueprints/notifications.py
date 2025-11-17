"""
Notifications Blueprint - 通知中心 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import NotificationService

notifications_bp = Blueprint('notifications', __name__, description='通知中心 API')


@notifications_bp.route('', methods=['GET'])
@jwt_required()
def list_notifications():
    """
    獲取通知列表
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 獲取查詢參數
        read_param = request.args.get('read')  # 'true', 'false', or None (all)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 處理讀取狀態篩選
        filters = {}
        if read_param is not None:
            filters['read'] = read_param.lower() == 'true'
        
        # 分頁參數
        pagination = {
            'page': page,
            'per_page': per_page
        }
        
        result = NotificationService.list_notifications(
            user_id=current_user_id,
            filters=filters,
            pagination=pagination
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """
    獲取未讀通知數量
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = NotificationService.get_unread_count(current_user_id)
        
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@notifications_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_notification_stats():
    """
    獲取通知統計信息
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = NotificationService.get_notification_stats(current_user_id)
        
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@notifications_bp.route('/<int:notification_id>/mark-read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """
    標記通知為已讀
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = NotificationService.mark_notification_read(
            user_id=current_user_id,
            notification_id=notification_id
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '通知不存在' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_read():
    """
    標記所有通知為已讀
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = NotificationService.mark_all_read(current_user_id)
        
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """
    刪除通知
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = NotificationService.delete_notification(
            user_id=current_user_id,
            notification_id=notification_id
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '通知不存在' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))
