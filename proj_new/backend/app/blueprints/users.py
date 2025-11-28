"""
Users Blueprint - 使用者管理 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import user_service
from app.exceptions import (
    NotFoundError, PermissionDeniedError, ValidationError, ConflictError
)

users_bp = Blueprint('users', __name__, description='使用者管理 API')


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    取得使用者資訊
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        user, include_sensitive = user_service.get_user(user_id, current_user_id)
        return jsonify(user.to_dict(include_sensitive=include_sensitive)), 200
    except NotFoundError as e:
        abort(404, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:user_id>', methods=['PATCH'])
@jwt_required()
def update_user(user_id):
    """
    更新使用者資訊
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        user = user_service.update_user(user_id, current_user_id, data)
        return jsonify(user.to_dict(include_sensitive=True)), 200
    except NotFoundError as e:
        abort(404, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except ConflictError as e:
        abort(409, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:user_id>/password', methods=['PATCH'])
@jwt_required()
def change_password(user_id):
    """
    修改密碼
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        user_service.change_password(user_id, current_user_id, old_password, new_password)
        
        return jsonify({'message': '密碼修改成功'}), 200
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except NotFoundError as e:
        abort(404, message=str(e))
    except ValidationError as e:
        abort(400, message=str(e))
    except Exception as e:
        return jsonify({'error': f'密碼修改失敗: {str(e)}'}), 500


@users_bp.route('/<int:user_id>/data/export', methods=['POST'])
@jwt_required()
def request_data_export(user_id):
    """
    請求個人資料匯出 (GDPR)
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        job_id = user_service.request_data_export(user_id, current_user_id)
        
        return jsonify({
            'message': '資料匯出請求已提交',
            'job_id': job_id
        }), 202
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except NotFoundError as e:
        abort(404, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:user_id>/data/delete', methods=['POST'])
@jwt_required()
def request_data_deletion(user_id):
    """
    請求個人資料刪除 (GDPR)
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        job_id = user_service.request_data_deletion(user_id, current_user_id)
        
        return jsonify({
            'message': '資料刪除請求已提交,需要管理員審核',
            'job_id': job_id
        }), 202
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except NotFoundError as e:
        abort(404, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
