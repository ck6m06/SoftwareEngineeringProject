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
from app.services.attachment_service import attachment_service
from app.exceptions import BusinessException
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
        
        # 呼叫 Service 層
        attachment = attachment_service.create_attachment(
            user_id=current_user_id,
            data=data,
            minio_client=minio_client
        )
        
        # 生成公開 URL
        public_url = attachment_service.generate_public_url(attachment.object_key)
        
        return jsonify({
            'message': '附件已建立',
            'attachment': attachment.to_dict(),
            'download_url': public_url
        }), 201
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
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
        # 呼叫 Service 層
        attachment = attachment_service.get_attachment(attachment_id)
        
        # 生成公開 URL
        public_url = attachment_service.generate_public_url(attachment.object_key)
        
        return jsonify({
            'attachment': attachment.to_dict(),
            'download_url': public_url
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
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
        current_user = db.session.get(User, current_user_id)
        
        if not current_user:
            return jsonify({'message': '用戶不存在'}), 404
        
        # 呼叫 Service 層
        attachment_service.delete_attachment(attachment_id, current_user)
        
        return jsonify({'message': '附件已刪除'}), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
