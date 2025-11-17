"""
Upload Service - 檔案上傳相關業務邏輯
"""
import uuid
import json
from datetime import datetime
from flask import current_app
from app import db
from app.models.others import Attachment
from app.models.user import User, UserRole
from config import Config

# MinIO 客戶端初始化
from minio import Minio


class UploadService:
    """檔案上傳業務邏輯服務"""
    
    _minio_client = None
    _minio_available = False
    
    @classmethod
    def _init_minio(cls):
        """初始化 MinIO 客戶端"""
        if cls._minio_client is not None:
            return  # 已初始化
        
        try:
            if Config.MINIO_ENDPOINT:
                cls._minio_client = Minio(
                    Config.MINIO_ENDPOINT,
                    access_key=Config.MINIO_ACCESS_KEY,
                    secret_key=Config.MINIO_SECRET_KEY,
                    secure=False
                )
                
                # 確保 bucket 存在
                if not cls._minio_client.bucket_exists(Config.MINIO_BUCKET):
                    cls._minio_client.make_bucket(Config.MINIO_BUCKET)
                    current_app.logger.info(f"Created MinIO bucket: {Config.MINIO_BUCKET}")
                
                # 設置 bucket 策略為公開讀寫
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject", "s3:PutObject"],
                        "Resource": [f"arn:aws:s3:::{Config.MINIO_BUCKET}/*"]
                    }]
                }
                cls._minio_client.set_bucket_policy(Config.MINIO_BUCKET, json.dumps(policy))
                cls._minio_available = True
                current_app.logger.info("MinIO initialized successfully")
            else:
                current_app.logger.warning("MinIO disabled (MINIO_ENDPOINT not configured)")
        except Exception as e:
            current_app.logger.error(f"MinIO initialization error: {e}")
            cls._minio_client = None
            cls._minio_available = False
    
    @classmethod
    def get_minio_client(cls):
        """獲取 MinIO 客戶端"""
        cls._init_minio()
        if not cls._minio_available:
            raise RuntimeError("MinIO 服務不可用")
        return cls._minio_client

    @staticmethod
    def upload_direct(user_id, file_data):
        """
        直接上傳檔案到 MinIO
        
        Args:
            user_id: 用戶ID
            file_data: 檔案數據對象
        
        Returns:
            dict: 上傳結果
        """
        try:
            # 驗證用戶存在
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            # 驗證檔案
            if not file_data or not hasattr(file_data, 'filename'):
                raise ValueError('缺少檔案')
            
            if not file_data.filename or file_data.filename == '':
                raise ValueError('檔案名稱為空')
            
            # 產生唯一 object key
            ext = file_data.filename.split('.')[-1] if '.' in file_data.filename else ''
            object_key = f"uploads/{user_id}/{uuid.uuid4()}.{ext}"
            
            # 獲取檔案大小
            file_data.seek(0, 2)  # 移到檔案末尾
            file_size = file_data.tell()
            file_data.seek(0)  # 回到開頭
            
            # 上傳到 MinIO
            minio_client = UploadService.get_minio_client()
            minio_client.put_object(
                bucket_name=Config.MINIO_BUCKET,
                object_name=object_key,
                data=file_data,
                length=file_size,
                content_type=file_data.content_type or 'application/octet-stream'
            )
            
            # 產生公開 URL
            public_url = UploadService._generate_public_url(object_key)
            
            return {
                'upload_id': str(uuid.uuid4()),
                'storage_key': object_key,
                'filename': file_data.filename,
                'size': file_size,
                'content_type': file_data.content_type or 'application/octet-stream',
                'url': public_url
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Direct upload error: {str(e)}")
            raise RuntimeError(f"檔案上傳失敗: {str(e)}")

    @staticmethod
    def create_attachment(user_id, data):
        """
        建立附件記錄
        
        Args:
            user_id: 用戶ID
            data: 附件數據
        
        Returns:
            dict: 建立結果
        """
        try:
            # 驗證用戶存在
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            # 驗證必填欄位
            required_fields = ['object_key', 'filename', 'content_type', 'size']
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f'缺少必填欄位: {field}')
            
            # 驗證檔案是否存在於 MinIO
            try:
                minio_client = UploadService.get_minio_client()
                stat = minio_client.stat_object(
                    bucket_name=Config.MINIO_BUCKET,
                    object_name=data['object_key']
                )
            except Exception:
                raise ValueError('檔案不存在於儲存系統')
            
            # 建立附件記錄
            attachment = Attachment(
                object_key=data['object_key'],
                filename=data['filename'],
                content_type=data['content_type'],
                size=data['size'],
                uploaded_by_id=user_id,
                entity_type=data.get('entity_type'),  # 'animal', 'application', etc.
                entity_id=data.get('entity_id')
            )
            
            db.session.add(attachment)
            db.session.commit()
            
            # 產生公開 URL
            public_url = UploadService._generate_public_url(data['object_key'])
            
            return {
                'message': '附件已建立',
                'attachment': attachment.to_dict(),
                'download_url': public_url
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Create attachment error: {str(e)}")
            raise RuntimeError(f"建立附件記錄失敗: {str(e)}")

    @staticmethod
    def get_attachment(user_id, attachment_id):
        """
        獲取附件資訊及下載 URL
        
        Args:
            user_id: 用戶ID
            attachment_id: 附件ID
        
        Returns:
            dict: 附件資訊及下載連結
        """
        try:
            # 驗證用戶存在
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            # 查找附件
            attachment = Attachment.query.filter_by(
                attachment_id=attachment_id,
                deleted_at=None
            ).first()
            
            if not attachment:
                raise ValueError('附件不存在')
            
            # 權限檢查：上傳者或管理員可以查看
            if (attachment.uploaded_by_id != user_id and 
                user.role != UserRole.ADMIN):
                # 如果是公開附件（例如動物圖片），允許查看
                if attachment.entity_type not in ['animal', 'public']:
                    raise ValueError('無權限訪問此附件')
            
            # 產生公開 URL
            public_url = UploadService._generate_public_url(attachment.object_key)
            
            return {
                'attachment': attachment.to_dict(),
                'download_url': public_url
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Get attachment error: {str(e)}")
            raise RuntimeError(f"獲取附件資訊失敗: {str(e)}")

    @staticmethod
    def delete_attachment(user_id, attachment_id):
        """
        刪除附件
        
        Args:
            user_id: 用戶ID
            attachment_id: 附件ID
        
        Returns:
            dict: 刪除結果
        """
        try:
            # 驗證用戶存在
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            # 查找附件
            attachment = Attachment.query.filter_by(
                attachment_id=attachment_id,
                deleted_at=None
            ).first()
            
            if not attachment:
                raise ValueError('附件不存在')
            
            # 權限檢查：上傳者本人或管理員
            if (attachment.uploaded_by_id != user_id and 
                user.role != UserRole.ADMIN):
                raise ValueError('無權限刪除此附件')
            
            # 軟刪除（實際檔案保留在 MinIO）
            attachment.deleted_at = datetime.utcnow()
            db.session.commit()
            
            return {'message': '附件已刪除'}
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Delete attachment error: {str(e)}")
            raise RuntimeError(f"刪除附件失敗: {str(e)}")

    @staticmethod
    def list_user_attachments(user_id, filters=None):
        """
        獲取用戶附件列表
        
        Args:
            user_id: 用戶ID
            filters: 篩選條件 {'entity_type': str, 'entity_id': int}
        
        Returns:
            dict: 附件列表
        """
        try:
            # 驗證用戶存在
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            filters = filters or {}
            
            # 基本查詢
            query = Attachment.query.filter_by(
                uploaded_by_id=user_id,
                deleted_at=None
            )
            
            # 篩選條件
            if 'entity_type' in filters and filters['entity_type']:
                query = query.filter_by(entity_type=filters['entity_type'])
            
            if 'entity_id' in filters and filters['entity_id']:
                query = query.filter_by(entity_id=filters['entity_id'])
            
            # 排序（最新上傳在前）
            attachments = query.order_by(Attachment.created_at.desc()).all()
            
            # 為每個附件產生 URL
            result = []
            for attachment in attachments:
                attachment_dict = attachment.to_dict()
                attachment_dict['download_url'] = UploadService._generate_public_url(attachment.object_key)
                result.append(attachment_dict)
            
            return {
                'attachments': result,
                'total': len(result)
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"List user attachments error: {str(e)}")
            raise RuntimeError(f"獲取附件列表失敗: {str(e)}")

    @staticmethod
    def _generate_public_url(object_key):
        """產生公開 URL"""
        external_endpoint = Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'
        return f"http://{external_endpoint}/{Config.MINIO_BUCKET}/{object_key}"

    @staticmethod
    def get_upload_stats(user_id):
        """
        獲取用戶上傳統計
        
        Args:
            user_id: 用戶ID
        
        Returns:
            dict: 上傳統計數據
        """
        try:
            # 驗證用戶存在
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            # 統計查詢
            from sqlalchemy import func
            
            total_files = Attachment.query.filter_by(
                uploaded_by_id=user_id,
                deleted_at=None
            ).count()
            
            total_size = db.session.query(
                func.sum(Attachment.size)
            ).filter_by(
                uploaded_by_id=user_id,
                deleted_at=None
            ).scalar() or 0
            
            # 按類型統計
            type_stats = db.session.query(
                Attachment.entity_type,
                func.count(Attachment.attachment_id).label('count'),
                func.sum(Attachment.size).label('size')
            ).filter_by(
                uploaded_by_id=user_id,
                deleted_at=None
            ).group_by(Attachment.entity_type).all()
            
            type_breakdown = {}
            for stat in type_stats:
                type_breakdown[stat.entity_type or 'unspecified'] = {
                    'count': stat.count,
                    'size': stat.size or 0
                }
            
            return {
                'total_files': total_files,
                'total_size_bytes': int(total_size),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'type_breakdown': type_breakdown
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Get upload stats error: {str(e)}")
            raise RuntimeError(f"獲取上傳統計失敗: {str(e)}")