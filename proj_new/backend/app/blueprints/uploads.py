"""
Uploads Blueprint - 檔案上傳 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

from app import db
from app.models.others import Attachment
from app.models.user import User
from config import Config

# MinIO 客戶端初始化
from minio import Minio

# 只使用內部客戶端連接 MinIO
minio_client = None
minio_available = False

try:
    if Config.MINIO_ENDPOINT:
        minio_client = Minio(
            Config.MINIO_ENDPOINT,  # minio:9000
            access_key=Config.MINIO_ACCESS_KEY,
            secret_key=Config.MINIO_SECRET_KEY,
            secure=False
        )
        
        # 確保 bucket 存在
        if not minio_client.bucket_exists(Config.MINIO_BUCKET):
            minio_client.make_bucket(Config.MINIO_BUCKET)
            print(f"Created MinIO bucket: {Config.MINIO_BUCKET}")
        else:
            print(f"MinIO bucket exists: {Config.MINIO_BUCKET}")
        
        # 設置 bucket 策略為公開讀寫 (允許前端直接上傳)
        import json
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject", "s3:PutObject"],
                    "Resource": [f"arn:aws:s3:::{Config.MINIO_BUCKET}/*"]
                }
            ]
        }
        minio_client.set_bucket_policy(Config.MINIO_BUCKET, json.dumps(policy))
        print(f"MinIO bucket policy set to public read-write")
        minio_available = True
    else:
        print("MinIO disabled (MINIO_ENDPOINT not configured)")
    
except Exception as e:
    print(f"MinIO initialization error (non-fatal): {e}")
    minio_client = None
    minio_available = False

uploads_bp = Blueprint('uploads', __name__, description='檔案上傳 API')


@uploads_bp.route('/direct', methods=['POST'])
@jwt_required()
def upload_direct():
    """
    直接上傳檔案 (後端代理)
    ---
    解決 presigned URL 的 CORS 和簽名問題
    前端直接將檔案發送到此 endpoint,後端負責上傳到 MinIO
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 檢查是否有檔案
        if 'file' not in request.files:
            abort(400, message='缺少檔案')
        
        file = request.files['file']
        if file.filename == '':
            abort(400, message='檔案名稱為空')
        
        # 生成唯一 object key
        ext = file.filename.split('.')[-1] if '.' in file.filename else ''
        object_key = f"uploads/{current_user_id}/{uuid.uuid4()}.{ext}"
        
        print(f"Direct upload: {file.filename} -> {object_key}")
        
        # 上傳到 MinIO
        file.seek(0, 2)  # 移到檔案末尾
        file_size = file.tell()
        file.seek(0)  # 回到開頭
        
        minio_client.put_object(
            bucket_name=Config.MINIO_BUCKET,
            object_name=object_key,
            data=file,
            length=file_size,
            content_type=file.content_type or 'application/octet-stream'
        )
        
        print(f"Upload successful: {object_key}")
        
        # 生成永久的公開 URL (bucket 已設為 public)
        public_url = f"http://{Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'}/{Config.MINIO_BUCKET}/{object_key}"
        
        return jsonify({
            'upload_id': str(uuid.uuid4()),
            'storage_key': object_key,
            'filename': file.filename,
            'size': file_size,
            'content_type': file.content_type,
            'url': public_url
        }), 200
        
    except Exception as e:
        print(f"Direct upload error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@uploads_bp.route('/attachments', methods=['POST'])
@jwt_required()
def create_attachment():
    """
    建立附件記錄
    ---
    上傳完成後建立元數據
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 驗證必填欄位
        required_fields = ['object_key', 'filename', 'content_type', 'size']
        for field in required_fields:
            if not data.get(field):
                abort(400, message=f'缺少必填欄位: {field}')
        
        # 驗證檔案是否存在於 MinIO
        try:
            stat = minio_client.stat_object(
                bucket_name=Config.MINIO_BUCKET,
                object_name=data['object_key']
            )
        except Exception:
            abort(404, message='檔案不存在於儲存系統')
        
        # 建立附件記錄
        attachment = Attachment(
            object_key=data['object_key'],
            filename=data['filename'],
            content_type=data['content_type'],
            size=data['size'],
            uploaded_by_id=current_user_id,
            entity_type=data.get('entity_type'),  # 'animal', 'application', etc.
            entity_id=data.get('entity_id')
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        # 生成永久的公開 URL
        public_url = f"http://{Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'}/{Config.MINIO_BUCKET}/{data['object_key']}"
        
        return jsonify({
            'message': '附件已建立',
            'attachment': attachment.to_dict(),
            'download_url': public_url
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@uploads_bp.route('/attachments/<int:attachment_id>', methods=['GET'])
@jwt_required()
def get_attachment(attachment_id):
    """
    取得附件資訊及下載 URL
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        attachment = Attachment.query.filter_by(
            attachment_id=attachment_id,
            deleted_at=None
        ).first()
        
        if not attachment:
            abort(404, message='附件不存在')
        
        # 生成永久的公開 URL
        public_url = f"http://{Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'}/{Config.MINIO_BUCKET}/{attachment.object_key}"
        
        return jsonify({
            'attachment': attachment.to_dict(),
            'download_url': public_url
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@uploads_bp.route('/attachments/<int:attachment_id>', methods=['DELETE'])
@jwt_required()
def delete_attachment(attachment_id):
    """
    刪除附件
    ---
    軟刪除，實際檔案保留在 MinIO
    """
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        attachment = Attachment.query.filter_by(
            attachment_id=attachment_id,
            deleted_at=None
        ).first()
        
        if not attachment:
            abort(404, message='附件不存在')
        
        # 權限檢查: 上傳者本人或管理員
        from app.models.user import UserRole
        if attachment.uploaded_by_id != current_user_id and current_user.role != UserRole.ADMIN:
            abort(403, message='無權限刪除此附件')
        
        # 軟刪除
        from datetime import datetime
        attachment.deleted_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': '附件已刪除'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
