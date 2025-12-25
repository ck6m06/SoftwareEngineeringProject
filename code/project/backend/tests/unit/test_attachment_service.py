"""
單元測試：app/services/attachment_service.py

測試附件服務的所有業務邏輯
目標：100% 測試通過率 + 95%+ 覆蓋率
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from app import create_app
from app.services.attachment_service import AttachmentService
from app.models.others import Attachment
from app.models.user import User, UserRole
from app.exceptions import (
    NotFoundError, PermissionDeniedError, ValidationError
)


@pytest.fixture
def app():
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield app


# ==================== create_attachment ====================
class TestCreateAttachment:
    
    def test_create_attachment_successfully(self, app_context, monkeypatch):
        """TC-01: 成功創建附件"""
        mock_minio_client = Mock()
        mock_minio_client.stat_object.return_value = True
        
        mock_attachment = Mock(spec=Attachment)
        mock_attachment.storage_key = 'uploads/test.jpg'
        mock_attachment.filename = 'test.jpg'
        mock_attachment.created_by = 1
        
        def mock_attachment_init(*args, **kwargs):
            return mock_attachment
        
        monkeypatch.setattr('app.services.attachment_service.Attachment', mock_attachment_init)
        
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.attachment_service.db', mock_db)
        
        data = {
            'object_key': 'uploads/test.jpg',
            'filename': 'test.jpg',
            'content_type': 'image/jpeg',
            'size': 1024,
            'entity_type': 'animal',
            'entity_id': 100
        }
        
        result = AttachmentService.create_attachment(
            user_id=1,
            data=data,
            minio_client=mock_minio_client
        )
        
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_missing_required_field_raises_error(self, app_context):
        """TC-02: 缺少必填欄位"""
        mock_minio_client = Mock()
        
        data = {
            'filename': 'test.jpg',
            'content_type': 'image/jpeg',
            # 缺少 object_key
        }
        
        with pytest.raises(ValidationError, match='缺少必填欄位: object_key'):
            AttachmentService.create_attachment(
                user_id=1,
                data=data,
                minio_client=mock_minio_client
            )
    
    def test_file_not_exists_in_minio_raises_error(self, app_context):
        """TC-03: 檔案不存在於 MinIO"""
        mock_minio_client = Mock()
        mock_minio_client.stat_object.side_effect = Exception('File not found')
        
        data = {
            'object_key': 'uploads/test.jpg',
            'filename': 'test.jpg',
            'content_type': 'image/jpeg',
            'size': 1024
        }
        
        with pytest.raises(NotFoundError, match='檔案不存在於儲存系統'):
            AttachmentService.create_attachment(
                user_id=1,
                data=data,
                minio_client=mock_minio_client
            )
    
    def test_create_without_entity(self, app_context, monkeypatch):
        """TC-04: 創建不關聯實體的附件"""
        mock_minio_client = Mock()
        mock_minio_client.stat_object.return_value = True
        
        mock_attachment = Mock(spec=Attachment)
        mock_attachment.entity_type = None
        mock_attachment.entity_id = None
        
        def mock_attachment_init(*args, **kwargs):
            return mock_attachment
        
        monkeypatch.setattr('app.services.attachment_service.Attachment', mock_attachment_init)
        
        mock_db_session = MagicMock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.attachment_service.db', mock_db)
        
        data = {
            'object_key': 'uploads/test.jpg',
            'filename': 'test.jpg',
            'content_type': 'image/jpeg',
            'size': 1024
        }
        
        result = AttachmentService.create_attachment(
            user_id=1,
            data=data,
            minio_client=mock_minio_client
        )
        
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()


# ==================== get_attachment ====================
class TestGetAttachment:
    
    def test_get_attachment_successfully(self, app_context, monkeypatch):
        """TC-05: 成功取得附件"""
        mock_attachment = Mock(spec=Attachment)
        mock_attachment.attachment_id = 1
        mock_attachment.filename = 'test.jpg'
        
        mock_attachment_query = Mock()
        mock_attachment_query.filter_by.return_value.first.return_value = mock_attachment
        monkeypatch.setattr('app.services.attachment_service.Attachment.query', mock_attachment_query)
        
        result = AttachmentService.get_attachment(1)
        
        assert result is not None
        assert result.attachment_id == 1
        assert result.filename == 'test.jpg'
    
    def test_get_nonexistent_attachment_raises_error(self, app_context, monkeypatch):
        """TC-06: 附件不存在"""
        mock_attachment_query = Mock()
        mock_attachment_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.attachment_service.Attachment.query', mock_attachment_query)
        
        with pytest.raises(NotFoundError, match='附件不存在'):
            AttachmentService.get_attachment(999)


# ==================== delete_attachment ====================
class TestDeleteAttachment:
    
    def test_delete_attachment_by_owner(self, app_context, monkeypatch):
        """TC-07: 上傳者刪除自己的附件"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_attachment = Mock(spec=Attachment)
        mock_attachment.attachment_id = 1
        mock_attachment.uploaded_by_id = 1
        
        mock_attachment_query = Mock()
        mock_attachment_query.filter_by.return_value.first.return_value = mock_attachment
        monkeypatch.setattr('app.services.attachment_service.Attachment.query', mock_attachment_query)
        
        mock_db_session = Mock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.attachment_service.db', mock_db)
        
        AttachmentService.delete_attachment(1, mock_user)
        
        assert mock_attachment.deleted_at is not None
        mock_db_session.commit.assert_called_once()
    
    def test_delete_attachment_by_admin(self, app_context, monkeypatch):
        """TC-08: 管理員刪除附件"""
        mock_admin = Mock(spec=User)
        mock_admin.user_id = 2
        mock_admin.role = UserRole.ADMIN
        
        mock_attachment = Mock(spec=Attachment)
        mock_attachment.attachment_id = 1
        mock_attachment.uploaded_by_id = 1  # 不同的上傳者
        
        mock_attachment_query = Mock()
        mock_attachment_query.filter_by.return_value.first.return_value = mock_attachment
        monkeypatch.setattr('app.services.attachment_service.Attachment.query', mock_attachment_query)
        
        mock_db_session = Mock()
        mock_db = Mock()
        mock_db.session = mock_db_session
        monkeypatch.setattr('app.services.attachment_service.db', mock_db)
        
        AttachmentService.delete_attachment(1, mock_admin)
        
        assert mock_attachment.deleted_at is not None
        mock_db_session.commit.assert_called_once()
    
    def test_delete_attachment_without_permission_raises_error(self, app_context, monkeypatch):
        """TC-09: 非上傳者且非管理員不能刪除"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 2
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_attachment = Mock(spec=Attachment)
        mock_attachment.attachment_id = 1
        mock_attachment.uploaded_by_id = 1
        
        mock_attachment_query = Mock()
        mock_attachment_query.filter_by.return_value.first.return_value = mock_attachment
        monkeypatch.setattr('app.services.attachment_service.Attachment.query', mock_attachment_query)
        
        with pytest.raises(PermissionDeniedError, match='無權限刪除此附件'):
            AttachmentService.delete_attachment(1, mock_user)
    
    def test_delete_nonexistent_attachment_raises_error(self, app_context, monkeypatch):
        """TC-10: 刪除不存在的附件"""
        mock_user = Mock(spec=User)
        mock_user.user_id = 1
        mock_user.role = UserRole.GENERAL_MEMBER
        
        mock_attachment_query = Mock()
        mock_attachment_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.services.attachment_service.Attachment.query', mock_attachment_query)
        
        with pytest.raises(NotFoundError, match='附件不存在'):
            AttachmentService.delete_attachment(999, mock_user)


# ==================== generate_public_url ====================
class TestGeneratePublicUrl:
    
    def test_generate_public_url(self, app_context):
        """TC-11: 生成公開 URL"""
        object_key = 'uploads/animals/2024/test.jpg'
        
        url = AttachmentService.generate_public_url(object_key)
        
        assert url.startswith('/minio/')
        assert object_key in url
