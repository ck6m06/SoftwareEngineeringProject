"""
Auth Blueprint - 身份驗證相關 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, UserRole
from app.services.auth_service import auth_service
from app.exceptions import ValidationError, NotFoundError, ConflictError, UnauthorizedError, PermissionDeniedError
from datetime import datetime

auth_bp = Blueprint('auth', __name__, description='身份驗證 API')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    使用者註冊
    ---
    """
    data = request.get_json()
    
    # 驗證必填欄位
    required_fields = ['email', 'password']
    if not all(field in data for field in required_fields):
        abort(400, message='缺少必填欄位')
    
    try:
        pending = auth_service.register_pending(
            email=data['email'],
            password=data['password'],
            username=data.get('username'),
            phone_number=data.get('phone_number'),
            region=data.get('region'),
            address=data.get('address'),
            client_ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # 遮罩 email
        masked = pending.email
        if '@' in masked:
            local, domain = masked.split('@', 1)
            if len(local) > 3:
                masked = local[:3] + '***@' + domain
            else:
                masked = '***@' + domain
        
        return jsonify({
            'message': '驗證碼已發送至電子郵件',
            'pending_id': pending.pending_id,
            'masked_email': masked,
            'expires_in': 15 * 60
        }), 201
        
    except ConflictError as e:
        abort(409, message=str(e))


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    使用者登入
    ---
    """
    data = request.get_json()
    
    # 驗證必填欄位
    if not data.get('email') or not data.get('password'):
        abort(400, message='Email 和密碼為必填')
    
    try:
        user, access_token, refresh_token = auth_service.login(
            email=data['email'],
            password=data['password']
        )
        
        return jsonify({
            'message': '登入成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except UnauthorizedError as e:
        abort(401, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    刷新 access token
    ---
    """
    current_user_id = int(get_jwt_identity())
    new_access_token = create_access_token(identity=str(current_user_id))
    
    return jsonify({
        'access_token': new_access_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    取得當前使用者資訊
    ---
    """
    current_user_id = int(get_jwt_identity())
    user = User.query.filter_by(user_id=current_user_id, deleted_at=None).first()
    
    if not user:
        abort(404, message='使用者不存在或已刪除')
    
    return jsonify(user.to_dict(include_sensitive=True)), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    使用者登出
    ---
    """
    # 在實際應用中，應該將 token 加入黑名單
    # 這裡簡化處理，僅返回成功訊息
    return jsonify({
        'message': '登出成功'
    }), 200


@auth_bp.route('/verify', methods=['GET'])
def verify_email():
    """
    驗證 email
    查詢參數: token (必填)
    ---
    """
    token = request.args.get('token')
    
    if not token:
        abort(400, message='缺少驗證 token')
    
    try:
        user = auth_service.verify_email(token)
        
        return jsonify({
            'message': 'Email 驗證成功',
            'verified': True,
            'user': user.to_dict()
        }), 200
        
    except ValidationError as e:
        abort(400, message=str(e))
    except NotFoundError as e:
        abort(404, message=str(e))


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """
    重新發送驗證郵件
    Body: { "email": "user@example.com" }
    ---
    """
    data = request.get_json()
    
    if not data.get('email'):
        abort(400, message='Email 為必填')
    
    # 使用 service，總是返回成功（安全考量）
    auth_service.send_verification_email(data['email'])
    
    return jsonify({
        'message': '如果該 email 存在，驗證郵件已發送'
    }), 200


@auth_bp.route('/verify-registration', methods=['POST'])
def verify_registration_code():
    """
    驗證註冊用的一次性數字驗證碼並建立 user
    Body: { "pending_id": 123, "code": "123456", "role": "GENERAL_MEMBER" }
    """
    data = request.get_json() or {}
    pending_id = data.get('pending_id')
    code = data.get('code')
    role = data.get('role')

    if not pending_id or not code:
        abort(400, message='pending_id 和 code 為必填')

    try:
        user = auth_service.verify_registration(
            pending_id=pending_id,
            code=code,
            role=role
        )
        
        return jsonify({'message': '驗證成功，帳號已建立'}), 200
        
    except NotFoundError as e:
        abort(404, message=str(e))
    except ValidationError as e:
        abort(400, message=str(e))
    except ConflictError as e:
        abort(409, message=str(e))


@auth_bp.route('/resend-registration-code', methods=['POST'])
def resend_registration_code():
    """
    重新發送註冊驗證碼
    Body: { "pending_id": 123 }
    """
    data = request.get_json() or {}
    pending_id = data.get('pending_id')
    if not pending_id:
        abort(400, message='pending_id 為必填')

    try:
        auth_service.resend_registration_code(pending_id)
        return jsonify({'message': '驗證碼已重新發送'}), 200
    except NotFoundError as e:
        abort(404, message=str(e))
    except ValidationError as e:
        abort(429, message=str(e))


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    忘記密碼 - 發送密碼重置郵件
    Body: { "email": "user@example.com" }
    ---
    """
    data = request.get_json()
    
    if not data.get('email'):
        abort(400, message='Email 為必填')
    
    # 使用 service，總是返回成功（安全考量）
    auth_service.request_password_reset(data['email'])
    
    return jsonify({
        'message': '如果該 email 存在，密碼重置郵件已發送'
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    重置密碼
    Body: { "token": "...", "new_password": "..." }
    ---
    """
    data = request.get_json()
    
    # 驗證必填欄位
    if not data.get('token') or not data.get('new_password'):
        abort(400, message='Token 和新密碼為必填')
    
    try:
        user = auth_service.reset_password(
            token=data['token'],
            new_password=data['new_password']
        )
        
        return jsonify({
            'message': '密碼重置成功，請使用新密碼登入',
            'success': True
        }), 200
        
    except ValidationError as e:
        abort(400, message=str(e))
    except NotFoundError as e:
        abort(404, message=str(e))


