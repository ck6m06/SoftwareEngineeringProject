"""
MinIO Utilities - Object Storage Operations
"""
from minio import Minio
from minio.error import S3Error
from datetime import timedelta
from flask import current_app


def get_minio_client():
    """
    取得 MinIO 客戶端
    
    Returns:
        Minio client instance
    """
    return Minio(
        current_app.config['MINIO_ENDPOINT'],
        access_key=current_app.config['MINIO_ACCESS_KEY'],
        secret_key=current_app.config['MINIO_SECRET_KEY'],
        secure=current_app.config['MINIO_SECURE']
    )


def ensure_bucket_exists(bucket_name: str):
    """
    確保 bucket 存在，不存在則建立
    
    Args:
        bucket_name: Bucket 名稱
    """
    client = get_minio_client()
    
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
    except S3Error as e:
        current_app.logger.error(f'Error creating bucket: {e}')
        raise


def generate_presigned_url(bucket_name: str, object_name: str, expires: int = 900):
    """
    產生預簽名 URL
    
    Args:
        bucket_name: Bucket 名稱
        object_name: 物件名稱
        expires: 過期時間（秒），預設 15 分鐘
    
    Returns:
        預簽名 URL
    """
    client = get_minio_client()
    
    try:
        url = client.presigned_put_object(
            bucket_name,
            object_name,
            expires=timedelta(seconds=expires)
        )
        return url
    except S3Error as e:
        current_app.logger.error(f'Error generating presigned URL: {e}')
        raise


def generate_download_url(bucket_name: str, object_name: str, expires: int = 3600):
    """
    產生下載 URL
    
    Args:
        bucket_name: Bucket 名稱
        object_name: 物件名稱
        expires: 過期時間（秒），預設 1 小時
    
    Returns:
        下載 URL
    """
    client = get_minio_client()
    
    try:
        url = client.presigned_get_object(
            bucket_name,
            object_name,
            expires=timedelta(seconds=expires)
        )
        return url
    except S3Error as e:
        current_app.logger.error(f'Error generating download URL: {e}')
        raise


def delete_object(bucket_name: str, object_name: str):
    """
    刪除物件
    
    Args:
        bucket_name: Bucket 名稱
        object_name: 物件名稱
    """
    client = get_minio_client()
    
    try:
        client.remove_object(bucket_name, object_name)
    except S3Error as e:
        current_app.logger.error(f'Error deleting object: {e}')
        raise
