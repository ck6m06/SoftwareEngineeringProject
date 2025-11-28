"""
Notifications Blueprint - 通知中心 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import notification_service

notifications_bp = Blueprint('notifications', __name__, description='通知中心 API')


@notifications_bp.route('', methods=['GET'])
@jwt_required()
def list_notifications():
    """
    獲取通知列表
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 獲取查詢參數
        read = request.args.get('read')  # 'true', 'false', or None (all)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = notification_service.list_notifications(
            user_id=current_user_id,
            read_filter=read,
            page=page,
            per_page=per_page
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """
    獲取未讀通知數量
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        count = notification_service.get_unread_count(current_user_id)
        
        return jsonify({'unread_count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/<int:notification_id>/mark-read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """
    標記通知為已讀
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        notification = notification_service.mark_as_read(notification_id, current_user_id)
        
        return jsonify(notification.to_dict()), 200
    except ValueError as e:
        abort(404, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_read():
    """
    標記所有通知為已讀
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        updated_count = notification_service.mark_all_as_read(current_user_id)
        
        return jsonify({
            'message': f'已標記 {updated_count} 個通知為已讀',
            'updated_count': updated_count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """
    刪除通知
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        notification_service.delete_notification(notification_id, current_user_id)
        
        return jsonify({'message': '通知已刪除'}), 200
    except ValueError as e:
        abort(404, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
