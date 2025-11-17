"""
Auth Blueprint - 身份驗證相關 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from datetime import datetime, timedelta
from werkzeug.exceptions import HTTPException

auth_bp = Blueprint('auth', __name__, description='身份驗證 API')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    使用者註冊
    ---
    """
    try:
        data = request.get_json()
        
        # 驗證必填欄位
        required_fields = ['email', 'password']
        if not all(field in data for field in required_fields):
            abort(400, message='缺少必填欄位')
        
        # 添加請求上下文資訊
        data['client_ip'] = request.remote_addr
        data['user_agent'] = request.headers.get('User-Agent')
        
        result = AuthService.create_pending_registration(data)
        status_code = 201 if 'pending_id' in result else 200
        return jsonify(result), status_code
        
    except ValueError as e:
        abort(409 if '已被註冊' in str(e) else 400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    使用者登入
    ---
    """
    try:
        data = request.get_json()
        
        # 驗證必填欄位
        if not data.get('email') or not data.get('password'):
            abort(400, message='Email 和密碼為必填')
        
        result = AuthService.login_user(data['email'], data['password'])
        return jsonify(result), 200
        
    except ValueError as e:
        abort(401, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    取得當前使用者資訊
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        user_info = AuthService.get_user_profile(current_user_id)
        return jsonify(user_info), 200
        
    except ValueError as e:
        abort(404, message=str(e))
    except Exception as e:
        abort(500, message='獲取用戶資訊失敗')


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """
    更新當前使用者資訊
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 移除不能更新的欄位
        restricted_fields = ['email', 'password', 'role', 'verified']
        for field in restricted_fields:
            data.pop(field, None)
        
        result = AuthService.update_user_profile(current_user_id, data)
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    使用者登出
    ---
    """
    # 在實際應用中，應該將 token 加入黑名單
    # 這裡簡化處理，僅返回成功訊息
    return jsonify({'message': '登出成功'}), 200


@auth_bp.route('/verify', methods=['GET'])
def verify_email():
    """
    驗證 email
    查詢參數: code (必填)
    ---
    """
    try:
        verification_code = request.args.get('code')
        
        if not verification_code:
            abort(400, message='缺少驗證碼')
        
        result = AuthService.verify_email(verification_code)
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """
    重新發送驗證郵件
    Body: { "email": "user@example.com" }
    ---
    """
    try:
        data = request.get_json()
        
        if not data.get('email'):
            abort(400, message='Email 為必填')
        
        result = AuthService.resend_verification_email(data['email'])
        return jsonify(result), 200
        
    except Exception as e:
        # 為了安全，統一返回成功訊息
        return jsonify({'message': '如果該 Email 存在，驗證郵件已重新發送'}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    忘記密碼 - 發送密碼重置郵件
    Body: { "email": "user@example.com" }
    ---
    """
    try:
        data = request.get_json()
        
        if not data.get('email'):
            abort(400, message='Email 為必填')
        
        result = AuthService.request_password_reset(data['email'])
        return jsonify(result), 200
        
    except Exception as e:
        # 為了安全，統一返回成功訊息
        return jsonify({'message': '如果該 Email 存在，重置連結已發送'}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    重置密碼
    Body: { "token": "...", "new_password": "..." }
    ---
    """
    try:
        data = request.get_json()
        
        # 驗證必填欄位
        if not data.get('token') or not data.get('new_password'):
            abort(400, message='Token 和新密碼為必填')
        
        # 驗證新密碼強度（至少 8 個字符）
        if len(data['new_password']) < 8:
            abort(400, message='密碼長度至少需要 8 個字符')
        
        result = AuthService.reset_password(data['token'], data['new_password'])
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    變更密碼
    Body: { "old_password": "...", "new_password": "..." }
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 驗證必填欄位
        if not data.get('old_password') or not data.get('new_password'):
            abort(400, message='舊密碼和新密碼為必填')
        
        # 驗證新密碼強度
        if len(data['new_password']) < 8:
            abort(400, message='密碼長度至少需要 8 個字符')
        
        result = AuthService.change_password(
            current_user_id, 
            data['old_password'], 
            data['new_password']
        )
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """
    檢查 Email 是否已存在
    Body: { "email": "user@example.com" }
    ---
    """
    try:
        data = request.get_json()
        
        if not data.get('email'):
            abort(400, message='Email 為必填')
        
        exists = AuthService.check_email_exists(data['email'])
        return jsonify({'exists': exists}), 200
        
    except Exception as e:
        abort(500, message='檢查失敗')


# 保留舊的註冊流程 API 以保持向後兼容性
@auth_bp.route('/verify-registration', methods=['POST'])
def verify_registration_code():
    """
    驗證註冊用的一次性數字驗證碼並建立 user
    Body: { "pending_id": 123, "code": "123456" }
    """
    try:
        data = request.get_json() or {}
        pending_id = data.get('pending_id')
        code = data.get('code')

        if not pending_id or not code:
            abort(400, message='pending_id 和 code 為必填')
        
        result = AuthService.verify_registration_code(
            pending_id, code, data.get('role')
        )
        return jsonify(result), 200
        
    except ValueError as e:
        if '已被註冊' in str(e):
            abort(409, message=str(e))
        elif '找不到' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@auth_bp.route('/resend-registration-code', methods=['POST'])
def resend_registration_code():
    """
    重新發送註冊驗證碼
    Body: { "pending_id": 123 }
    """
    try:
        data = request.get_json() or {}
        pending_id = data.get('pending_id')
        if not pending_id:
            abort(400, message='pending_id 為必填')
        
        result = AuthService.resend_registration_code(pending_id)
        return jsonify(result), 200
        
    except ValueError as e:
        if '已達今日重新寄信上限' in str(e):
            abort(429, message=str(e))
        elif '找不到' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))

