"""
Notifications Blueprint - ?�知中�? API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import Notification, User

notifications_bp = Blueprint('notifications', __name__, description='?�知中�? API')


@notifications_bp.route('', methods=['GET'])
@jwt_required()
def list_notifications():
    """
    ?��??�知?�表
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # ?��??�詢?�數
        read = request.args.get('read')  # 'true', 'false', or None (all)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 構建?�詢
        query = Notification.query.filter_by(recipient_id=current_user_id)
        
        # ?�濾已�?/?��?
        if read is not None:
            is_read = read.lower() == 'true'
            query = query.filter_by(read=is_read)
        
        # ?��?並�?�?(?�?��??��?)
        pagination = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'notifications': [n.to_dict() for n in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """
    ?��??��??�知?��?
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        count = Notification.query.filter_by(
            recipient_id=current_user_id,
            read=False
        ).count()
        
        return jsonify({
            'unread_count': count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/<int:notification_id>/mark-read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """
    標�??�知?�已讀
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        notification = Notification.query.filter_by(
            notification_id=notification_id,
            recipient_id=current_user_id
        ).first()
        
        if not notification:
            abort(404, message='通知不存在')
        
        if not notification.read:
            notification.read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify(notification.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_read():
    """
    標�??�?�通知?�已讀
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        updated_count = Notification.query.filter_by(
            recipient_id=current_user_id,
            read=False
        ).update({
            'read': True,
            'read_at': datetime.utcnow()
        })
        
        db.session.commit()
        
        return jsonify({
            'message': f'已�?�?{updated_count} ?�通知?�已讀',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """
    ?�除?�知
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        notification = Notification.query.filter_by(
            notification_id=notification_id,
            recipient_id=current_user_id
        ).first()
        
        if not notification:
            abort(404, message='通知不存在')
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({
            'message': '通知已刪除'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
