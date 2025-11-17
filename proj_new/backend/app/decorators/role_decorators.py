"""
Role-based access decorators
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User, UserRole


def role_required(*allowed_roles):
    """
    裝飾器：檢查用戶角色權限
    
    Args:
        allowed_roles: 允許的角色列表
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                if not current_user_id:
                    return jsonify({'error': 'Authentication required'}), 401
                
                user = User.query.filter_by(
                    user_id=current_user_id,
                    deleted_at=None
                ).first()
                
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                if user.role not in allowed_roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': 'Authorization error'}), 500
                
        return decorated_function
    return decorator


def admin_required(f):
    """管理員權限裝飾器"""
    return role_required(UserRole.ADMIN)(f)


def shelter_member_or_admin_required(f):
    """收容所成員或管理員權限裝飾器"""
    return role_required(UserRole.SHELTER_MEMBER, UserRole.ADMIN)(f)