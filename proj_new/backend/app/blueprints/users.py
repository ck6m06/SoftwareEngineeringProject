"""
Users Blueprint - 使用者管理 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from datetime import datetime
from app import db
from app.models import User, UserRole

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
        current_user = User.query.get(current_user_id)
        
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        
        if not user:
            abort(404, message='使用者不存在')
        
        # 檢查權限 - 只有本人或管理員可以查看完整資訊
        include_sensitive = (
            current_user_id == user_id or 
            current_user.role == UserRole.ADMIN
        )
        
        return jsonify(user.to_dict(include_sensitive=include_sensitive)), 200
        
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
        current_user = User.query.get(current_user_id)
        
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        
        if not user:
            abort(404, message='使用者不存在')
        
        # 檢查權限 - 只有本人或管理員可以更新
        if current_user_id != user_id and current_user.role != UserRole.ADMIN:
            abort(403, message='沒有權限修改此使用者資訊')
        
        data = request.get_json()
        
        # 可更新的欄位
        allowed_fields = ['username', 'phone_number', 'first_name', 'last_name', 
                         'profile_photo_url', 'settings', 'region', 'address']
        
        # 管理員可以更新額外欄位
        if current_user.role == UserRole.ADMIN:
            allowed_fields.extend(['role', 'verified', 'primary_shelter_id'])
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # 特殊處理 email 更新 (需要重新驗證)
        if 'email' in data and data['email'] != user.email:
            # 檢查新 email 是否已被使用
            existing_user = User.query.filter_by(email=data['email'], deleted_at=None).first()
            if existing_user and existing_user.user_id != user_id:
                abort(409, message='該電子郵件已被使用')
            
            user.email = data['email']
            user.verified = False  # 需要重新驗證
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(user.to_dict(include_sensitive=True)), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:user_id>/password', methods=['PATCH'])
@jwt_required()
def change_password(user_id):
    """
    修改密碼
    ---
    """
    current_user_id = int(get_jwt_identity())
    
    # 只能修改自己的密碼
    if current_user_id != user_id:
        abort(403, message='只能修改自己的密碼')
    
    user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
    
    if not user:
        abort(404, message='使用者不存在')
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        abort(400, message='old_password 和 new_password 為必填欄位')
    
    # 驗證舊密碼
    from app.utils.security import verify_password, hash_password
    if not verify_password(old_password, user.password_hash):
        abort(401, message='舊密碼錯誤')
    
    # 驗證新密碼長度
    if len(new_password) < 8:
        abort(400, message='新密碼長度至少需要 8 個字元')
    
    try:
        # 更新密碼
        user.password_hash = hash_password(new_password)
        
        # 更新密碼變更時間 (如果欄位存在)
        if hasattr(user, 'password_changed_at'):
            user.password_changed_at = datetime.utcnow()
        
        # 重置失敗登入次數
        if hasattr(user, 'failed_login_attempts'):
            user.failed_login_attempts = 0
        if hasattr(user, 'locked_until'):
            user.locked_until = None
        
        db.session.commit()
        
        return jsonify({
            'message': '密碼修改成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f'Password change error: {str(e)}')
        import traceback
        traceback.print_exc()
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
        
        # 只能匯出自己的資料
        if current_user_id != user_id:
            abort(403, message='只能匯出自己的資料')
        
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        
        if not user:
            abort(404, message='使用者不存在')
        
        # 創建匯出任務
        from app.models import Job, JobStatus
        
        job = Job(
            type='user_data_export',
            status=JobStatus.PENDING,
            payload={'user_id': user_id},
            created_by=user_id
        )
        
        db.session.add(job)
        db.session.commit()
        
        # TODO: 將任務加入 Celery 隊列
        # export_user_data.delay(job.job_id, user_id)
        
        return jsonify({
            'message': '資料匯出請求已提交',
            'job_id': job.job_id
        }), 202
        
    except Exception as e:
        db.session.rollback()
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
        current_user = User.query.get(current_user_id)
        
        # 只有本人或管理員可以刪除
        if current_user_id != user_id and current_user.role != UserRole.ADMIN:
            abort(403, message='沒有權限刪除此使用者資料')
        
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        
        if not user:
            abort(404, message='使用者不存在')
        
        # 創建刪除任務
        from app.models import Job, JobStatus
        
        job = Job(
            type='user_data_deletion',
            status=JobStatus.PENDING,
            payload={'user_id': user_id},
            created_by=current_user_id
        )
        
        db.session.add(job)
        db.session.commit()
        
        # TODO: 將任務加入 Celery 隊列
        # delete_user_data.delay(job.job_id, user_id)
        
        return jsonify({
            'message': '資料刪除請求已提交,需要管理員審核',
            'job_id': job.job_id
        }), 202
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
