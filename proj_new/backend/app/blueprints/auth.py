"""
Auth Blueprint - 身份驗證相關 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, UserRole
from app.utils.security import hash_password, verify_password, generate_verification_token, verify_token
from app.services.audit_service import audit_service
from app.services.email_service import email_service
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
    
    # 檢查 email 是否已存在
    if User.query.filter_by(email=data['email']).first():
        abort(409, message='此 email 已被註冊')
    
    # 設置用戶角色(可選參數,預設為GENERAL_MEMBER)
    user_role = UserRole.GENERAL_MEMBER
    if 'role' in data:
        try:
            user_role = UserRole(data['role'])
        except ValueError:
            abort(400, message=f'無效的角色: {data["role"]}')
    
    # 建立新使用者
    # 預設不自動標為已驗證，需透過 Email 驗證流程完成
    user = User(
        email=data['email'],
        password_hash=hash_password(data['password']),
        username=data.get('username'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone_number=data.get('phone_number'),
        role=user_role,
        verified=False
    )
    
    db.session.add(user)
    db.session.commit()
    
    # 產生驗證 token 並發送驗證郵件（非自動登入）
    token = generate_verification_token(user.user_id, purpose='email-verify')
    email_service.send_verification_email(
        user_email=user.email,
        username=user.username or user.email,
        token=token
    )

    return jsonify({
        'message': '註冊成功，驗證郵件已發送，請前往收件匣點選連結以啟用帳號',
        'user': user.to_dict(),
    }), 201


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
    
    # 查詢使用者 (排除已刪除帳號)
    user = User.query.filter_by(email=data['email'], deleted_at=None).first()
    
    if not user:
        abort(401, message='Email 或密碼錯誤')
    
    # 檢查 Email 是否已驗證
    if not user.verified:
        abort(403, message='請先驗證 Email，或使用重新發送驗證郵件功能')
    
    # 檢查帳號是否被鎖定
    if user.is_locked:
        abort(403, message=f'帳號已被鎖定至 {user.locked_until}')
    
    # 驗證密碼
    if not verify_password(data['password'], user.password_hash):
        # 增加失敗次數
        user.failed_login_attempts += 1
        
        # 如果失敗次數超過 5 次，鎖定帳號 30 分鐘
        if user.failed_login_attempts >= 5:
            from datetime import timedelta
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        db.session.commit()
        abort(401, message='Email 或密碼錯誤')
    
    # 登入成功,重置失敗次數
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    db.session.commit()
    
    # 建立 token (identity必須是字符串)
    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))
    
    # 記錄登入審計日誌
    audit_service.log_login(user.user_id, success=True)
    
    return jsonify({
        'message': '登入成功',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


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
    
    # 驗證 token (24 小時有效)
    user_id = verify_token(token, purpose='email-verify', max_age=86400)
    
    if not user_id:
        abort(400, message='驗證 token 無效或已過期')
    
    # 查找用戶
    user = User.query.get(user_id)
    
    if not user:
        abort(404, message='使用者不存在')
    
    if user.verified:
        return jsonify({
            'message': 'Email 已經驗證過了',
            'verified': True
        }), 200
    
    # 標記為已驗證
    user.verified = True
    db.session.commit()
    
    # 記錄審計日誌
    audit_service.log(
        action='user.email.verify',
        actor_id=user_id,
        target_type='user',
        target_id=user_id,
        before_state={'verified': False},
        after_state={'verified': True},
        shelter_id=None
    )
    
    return jsonify({
        'message': 'Email 驗證成功',
        'verified': True,
        'user': user.to_dict()
    }), 200


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
    
    # 查找用戶
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        # 為了安全考量，不透露用戶是否存在
        return jsonify({
            'message': '如果該 email 存在，驗證郵件已發送'
        }), 200
    
    if user.verified:
        return jsonify({
            'message': 'Email 已經驗證過了',
            'verified': True
        }), 200
    
    # 生成新 token 並發送
    token = generate_verification_token(user.user_id, purpose='email-verify')
    email_service.send_verification_email(
        user_email=user.email,
        username=user.username or user.email,
        token=token
    )
    
    return jsonify({
        'message': '驗證郵件已重新發送，請查看您的郵箱'
    }), 200


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
    
    # 查找用戶
    user = User.query.filter_by(email=data['email']).first()
    
    # 為了安全考量，不透露用戶是否存在
    # 即使用戶不存在，也返回相同訊息
    if not user:
        return jsonify({
            'message': '如果該 email 存在，密碼重置郵件已發送'
        }), 200
    
    # 生成密碼重置 token (有效期 1 小時)
    token = generate_verification_token(user.user_id, purpose='password-reset')
    
    # 發送密碼重置郵件
    email_service.send_password_reset_email(
        user_email=user.email,
        username=user.username or user.email,
        token=token
    )
    
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
    
    # 驗證 token (1 小時有效期)
    user_id = verify_token(data['token'], purpose='password-reset', max_age=3600)
    
    if not user_id:
        abort(400, message='重置 token 無效或已過期')
    
    # 查找用戶
    user = User.query.get(user_id)
    
    if not user:
        abort(404, message='使用者不存在')
    
    # 驗證新密碼強度（至少 8 個字符）
    if len(data['new_password']) < 8:
        abort(400, message='密碼長度至少需要 8 個字符')
    
    # 更新密碼
    old_password_hash = user.password_hash
    user.password_hash = hash_password(data['new_password'])
    user.password_changed_at = datetime.utcnow()
    
    # 重置失敗登入次數
    user.failed_login_attempts = 0
    user.locked_until = None
    
    db.session.commit()
    
    # 記錄審計日誌
    audit_service.log(
        action='user.password.reset',
        actor_id=user_id,
        target_type='user',
        target_id=user_id,
        before_state={'password_hash': old_password_hash[:20] + '...'},
        after_state={'password_hash': user.password_hash[:20] + '...'},
        shelter_id=None
    )
    
    return jsonify({
        'message': '密碼重置成功，請使用新密碼登入',
        'success': True
    }), 200

