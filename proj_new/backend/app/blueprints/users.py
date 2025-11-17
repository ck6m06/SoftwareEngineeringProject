"""
Users Blueprint - 使用者管理 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService

users_bp = Blueprint('users', __name__, description='使用者管理 API')


@users_bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    """
    獲取用戶列表 (僅管理員)
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 獲取篩選參數
        filters = {
            'role': request.args.get('role'),
            'verified': request.args.get('verified'),
            'region': request.args.get('region'),
            'search': request.args.get('search')
        }
        
        # 處理布林值
        if filters['verified'] is not None:
            filters['verified'] = filters['verified'].lower() in ('true', '1', 'yes')
        
        # 移除空值
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # 分頁參數
        pagination = {
            'page': request.args.get('page', 1, type=int),
            'per_page': min(request.args.get('per_page', 20, type=int), 100)
        }
        
        result = UserService.list_users(
            current_user_id=current_user_id,
            filters=filters,
            pagination=pagination
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '只有管理員' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    取得使用者資訊
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = UserService.get_user_profile(
            current_user_id=current_user_id,
            target_user_id=user_id
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '使用者不存在' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@users_bp.route('/<int:user_id>', methods=['PATCH'])
@jwt_required()
def update_user(user_id):
    """
    更新使用者資訊
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            abort(400, message='缺少請求資料')
        
        result = UserService.update_user_profile(
            current_user_id=current_user_id,
            target_user_id=user_id,
            data=data
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '使用者不存在' in str(e):
            abort(404, message=str(e))
        elif '沒有權限' in str(e) or '已被使用' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@users_bp.route('/<int:user_id>/password', methods=['PATCH'])
@jwt_required()
def change_password(user_id):
    """
    修改密碼
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 只能修改自己的密碼
        if current_user_id != user_id:
            abort(403, message='只能修改自己的密碼')
        
        data = request.get_json()
        if not data:
            abort(400, message='缺少請求資料')
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        result = UserService.change_password(
            user_id=user_id,
            old_password=old_password,
            new_password=new_password
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '使用者不存在' in str(e):
            abort(404, message=str(e))
        elif '舊密碼錯誤' in str(e):
            abort(401, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@users_bp.route('/<int:user_id>/statistics', methods=['GET'])
@jwt_required()
def get_user_statistics(user_id):
    """
    獲取用戶統計資訊 (用戶自己或管理員)
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 權限檢查：只有本人可以查看自己的統計
        if current_user_id != user_id:
            abort(403, message='只能查看自己的統計資訊')
        
        result = UserService.get_user_statistics(user_id)
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '使用者不存在' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@users_bp.route('/<int:user_id>/data/export', methods=['POST'])
@jwt_required()
def request_data_export(user_id):
    """
    請求個人資料匯出 (GDPR)
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 只能匯出自己的資料
        if current_user_id != user_id:
            abort(403, message='只能匯出自己的資料')
        
        result = UserService.request_data_export(user_id)
        
        return jsonify(result), 202
        
    except ValueError as e:
        if '使用者不存在' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@users_bp.route('/<int:user_id>/data/delete', methods=['POST'])
@jwt_required()
def request_data_deletion(user_id):
    """
    請求個人資料刪除 (GDPR)
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = UserService.request_data_deletion(
            current_user_id=current_user_id,
            target_user_id=user_id
        )
        
        return jsonify(result), 202
        
    except ValueError as e:
        if '使用者不存在' in str(e):
            abort(404, message=str(e))
        elif '沒有權限' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))
