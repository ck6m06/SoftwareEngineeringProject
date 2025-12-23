"""
Attachment Service - 附件業務邏輯服務
集中管理附件的驗證、創建和權限檢查
"""
from datetime import datetime
from typing import Dict, Any, Optional
from app import db
from app.models.others import Attachment
from app.models.user import User, UserRole
from app.exceptions import (
    NotFoundError, PermissionDeniedError, ValidationError
)
from config import Config


class AttachmentService:
    """附件業務邏輯服務類"""
    
    @staticmethod
    def create_attachment(user_id: int, data: Dict[str, Any], minio_client) -> Attachment:
        """
        創建附件記錄
        
        業務邏輯：
        1. 驗證必填欄位
        2. 驗證檔案是否存在於 MinIO
        3. 創建附件記錄
        
        Args:
            user_id: 上傳者 ID
            data: 附件資料
                - object_key: MinIO 物件鍵值 (必填)
                - filename: 檔案名稱 (必填)
                - content_type: 檔案類型 (必填)
                - size: 檔案大小 (必填)
                - entity_type: 關聯實體類型 (選填)
                - entity_id: 關聯實體 ID (選填)
            minio_client: MinIO 客戶端
            
        Returns:
            Attachment: 創建的附件物件
            
        Raises:
            ValidationError: 缺少必填欄位
            NotFoundError: 檔案不存在於儲存系統
        """
        # 驗證必填欄位
        required_fields = ['object_key', 'filename', 'content_type', 'size']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填欄位: {field}')
        
        # 驗證檔案是否存在於 MinIO
        try:
            minio_client.stat_object(
                bucket_name=Config.MINIO_BUCKET,
                object_name=data['object_key']
            )
        except Exception:
            raise NotFoundError('檔案不存在於儲存系統')
        
        # 建立附件記錄
        attachment = Attachment(
            object_key=data['object_key'],
            filename=data['filename'],
            content_type=data['content_type'],
            size=data['size'],
            uploaded_by_id=user_id,
            entity_type=data.get('entity_type'),
            entity_id=data.get('entity_id')
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return attachment
    
    @staticmethod
    def get_attachment(attachment_id: int) -> Attachment:
        """
        取得附件資訊
        
        Args:
            attachment_id: 附件 ID
            
        Returns:
            Attachment: 附件物件
            
        Raises:
            NotFoundError: 附件不存在
        """
        attachment = Attachment.query.filter_by(
            attachment_id=attachment_id,
            deleted_at=None
        ).first()
        
        if not attachment:
            raise NotFoundError('附件不存在')
        
        return attachment
    
    @staticmethod
    def delete_attachment(attachment_id: int, user: User) -> None:
        """
        刪除附件（軟刪除）
        
        業務邏輯：
        1. 檢查附件是否存在
        2. 權限檢查：上傳者本人或管理員
        3. 軟刪除附件記錄
        
        Args:
            attachment_id: 附件 ID
            user: 當前用戶
            
        Raises:
            NotFoundError: 附件不存在
            PermissionDeniedError: 無權限刪除
        """
        attachment = Attachment.query.filter_by(
            attachment_id=attachment_id,
            deleted_at=None
        ).first()
        
        if not attachment:
            raise NotFoundError('附件不存在')
        
        # 權限檢查: 上傳者本人或管理員
        if attachment.uploaded_by_id != user.user_id and user.role != UserRole.ADMIN:
            raise PermissionDeniedError('無權限刪除此附件')
        
        # 軟刪除
        attachment.deleted_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def generate_public_url(object_key: str) -> str:
        """
        生成附件的公開 URL
        
        Args:
            object_key: MinIO 物件鍵值
            
        Returns:
            str: 公開 URL (使用 Nginx 代理路徑)
        """
        # 使用 /minio/ 代理路徑，讓前端透過 Nginx 訪問 (GCP 部署兼容)
        return f"/minio/{Config.MINIO_BUCKET}/{object_key}"


# 創建全局實例
attachment_service = AttachmentService()
