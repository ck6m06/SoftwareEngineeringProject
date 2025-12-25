"""
Test suite for shelter_service module
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app.services.shelter_service import ShelterService
from app.models.shelter import Shelter
from app.models.user import User, UserRole
from app.models.animal import Animal, AnimalStatus, Species, Sex
from app.models.others import Job, JobType, JobStatus
from app.exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, ConflictError
)


class TestCheckShelterPermission(unittest.TestCase):
    """測試收容所權限檢查"""
    
    @patch('app.services.shelter_service.db')
    def test_admin_has_full_permission(self, mock_db):
        """測試管理員有完全權限"""
        mock_user = Mock(user_id=1, role=UserRole.ADMIN)
        mock_db.session.get.return_value = mock_user
        
        result = ShelterService.check_shelter_permission(1, 1)
        
        self.assertTrue(result)
    
    @patch('app.services.shelter_service.db')
    def test_shelter_member_with_primary_shelter(self, mock_db):
        """測試收容所成員對自己收容所有權限"""
        mock_user = Mock(user_id=1, role=UserRole.SHELTER_MEMBER, primary_shelter_id=1)
        mock_shelter = Mock(shelter_id=1, primary_account_user_id=1)
        
        mock_db.session.get.side_effect = lambda model, id: mock_user if model == User else mock_shelter
        
        result = ShelterService.check_shelter_permission(1, 1)
        
        self.assertTrue(result)
    
    @patch('app.services.shelter_service.db')
    def test_shelter_member_without_permission(self, mock_db):
        """測試收容所成員對其他收容所沒有權限"""
        mock_user = Mock(user_id=1, role=UserRole.SHELTER_MEMBER, primary_shelter_id=2)
        mock_shelter = Mock(shelter_id=1, primary_account_user_id=3)
        
        mock_db.session.get.side_effect = lambda model, id: mock_user if model == User else mock_shelter
        
        with self.assertRaises(PermissionDeniedError):
            ShelterService.check_shelter_permission(1, 1)
    
    @patch('app.services.shelter_service.db')
    def test_user_not_found(self, mock_db):
        """測試用戶不存在"""
        mock_db.session.get.return_value = None
        
        with self.assertRaises(NotFoundError):
            ShelterService.check_shelter_permission(1)
    
    @patch('app.services.shelter_service.db')
    def test_regular_user_no_permission(self, mock_db):
        """測試普通用戶沒有權限"""
        mock_user = Mock(user_id=1, role=UserRole.GENERAL_MEMBER)
        mock_db.session.get.return_value = mock_user
        
        with self.assertRaises(PermissionDeniedError):
            ShelterService.check_shelter_permission(1)


class TestCreateShelter(unittest.TestCase):
    """測試創建收容所"""
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.db')
    def test_create_shelter_success(self, mock_db, mock_shelter_model, mock_check_perm):
        """測試成功創建收容所"""
        mock_check_perm.return_value = True
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_shelter_model.query = mock_query
        
        # 創建一個實際的 Mock 對象，不依賴於 mock_shelter_model() 的返回值
        mock_shelter = Mock()
        mock_shelter.name = 'Test Shelter'
        mock_shelter.shelter_id = 1
        mock_shelter_model.return_value = mock_shelter
        
        address = {
            'street': '123 Main St',
            'city': 'City',
            'county': 'County',
            'postal_code': '12345'
        }
        
        result = ShelterService.create_shelter(
            user_id=1,
            name='Test Shelter',
            contact_email='test@example.com',
            contact_phone='0912345678',
            address=address,
            slug='test-shelter',
            region='North'
        )
        
        self.assertEqual(result.shelter_id, 1)
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    def test_create_shelter_invalid_email(self, mock_check_perm):
        """測試無效的 Email 格式"""
        mock_check_perm.return_value = True
        
        address = {
            'street': '123 Main St',
            'city': 'City',
            'county': 'County',
            'postal_code': '12345'
        }
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.create_shelter(
                user_id=1,
                name='Test Shelter',
                contact_email='invalid-email',
                contact_phone='0912345678',
                address=address
            )
        self.assertIn('Email 格式不正確', str(context.exception))
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    def test_create_shelter_missing_address_fields(self, mock_check_perm):
        """測試地址缺少必填欄位"""
        mock_check_perm.return_value = True
        
        address = {
            'street': '123 Main St',
            'city': 'City'
            # 缺少 county 和 postal_code
        }
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.create_shelter(
                user_id=1,
                name='Test Shelter',
                contact_email='test@example.com',
                contact_phone='0912345678',
                address=address
            )
        self.assertIn('地址缺少必填欄位', str(context.exception))
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    def test_create_shelter_duplicate_slug(self, mock_shelter_model, mock_check_perm):
        """測試 Slug 已存在"""
        mock_check_perm.return_value = True
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = Mock(slug='test-shelter')
        mock_shelter_model.query = mock_query
        
        address = {
            'street': '123 Main St',
            'city': 'City',
            'county': 'County',
            'postal_code': '12345'
        }
        
        with self.assertRaises(ConflictError):
            ShelterService.create_shelter(
                user_id=1,
                name='Test Shelter',
                contact_email='test@example.com',
                contact_phone='0912345678',
                address=address,
                slug='test-shelter'
            )
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    def test_create_shelter_invalid_address_type(self, mock_check_perm):
        """測試地址不是字典類型"""
        mock_check_perm.return_value = True
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.create_shelter(
                user_id=1,
                name='Test Shelter',
                contact_email='test@example.com',
                contact_phone='0912345678',
                address='not a dict'
            )
        self.assertIn('地址必須為 JSON 對象', str(context.exception))


class TestUpdateShelter(unittest.TestCase):
    """測試更新收容所"""
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.db')
    def test_update_shelter_success(self, mock_db, mock_shelter_model, mock_check_perm):
        """測試成功更新收容所"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1, name='Old Name')
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_query
        
        result = ShelterService.update_shelter(
            shelter_id=1,
            user_id=1,
            name='New Name',
            contact_phone='0987654321'
        )
        
        self.assertEqual(result.name, 'New Name')
        self.assertEqual(result.contact_phone, '0987654321')
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.shelter_service.Shelter')
    def test_update_shelter_not_found(self, mock_shelter_model):
        """測試收容所不存在"""
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_shelter_model.query = mock_query
        
        with self.assertRaises(NotFoundError):
            ShelterService.update_shelter(1, 1, name='New Name')
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    def test_update_shelter_invalid_email(self, mock_shelter_model, mock_check_perm):
        """測試更新無效的 Email"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_query
        
        with self.assertRaises(ValidationError):
            ShelterService.update_shelter(1, 1, contact_email='invalid')
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    def test_update_shelter_duplicate_slug(self, mock_shelter_model, mock_check_perm):
        """測試更新重複的 Slug"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_existing = Mock(shelter_id=2, slug='taken-slug')
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_shelter
        
        # Mock filter for slug check
        mock_filter_query = Mock()
        mock_filter_query.first.return_value = mock_existing
        mock_query.filter.return_value = mock_filter_query
        
        mock_shelter_model.query = mock_query
        
        with self.assertRaises(ConflictError):
            ShelterService.update_shelter(1, 1, slug='taken-slug')


class TestVerifyShelter(unittest.TestCase):
    """測試驗證收容所"""
    
    @patch('app.services.shelter_service.audit_service')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.db')
    def test_verify_shelter_success(self, mock_db, mock_shelter_model, mock_audit):
        """測試管理員成功驗證收容所"""
        mock_admin = Mock(user_id=1, role=UserRole.ADMIN)
        mock_shelter = Mock(shelter_id=1, verified=False)
        
        mock_db.session.get.return_value = mock_admin
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_query
        
        result = ShelterService.verify_shelter(1, 1, True)
        
        self.assertTrue(result.verified)
        mock_db.session.commit.assert_called_once()
        mock_audit.log_shelter_verify.assert_called_once_with(1, 1, True)
    
    @patch('app.services.shelter_service.db')
    def test_verify_shelter_not_admin(self, mock_db):
        """測試非管理員無法驗證"""
        mock_user = Mock(user_id=1, role=UserRole.SHELTER_MEMBER)
        mock_db.session.get.return_value = mock_user
        
        with self.assertRaises(PermissionDeniedError):
            ShelterService.verify_shelter(1, 1)
    
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.db')
    def test_verify_shelter_not_found(self, mock_db, mock_shelter_model):
        """測試收容所不存在"""
        mock_admin = Mock(user_id=1, role=UserRole.ADMIN)
        mock_db.session.get.return_value = mock_admin
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_shelter_model.query = mock_query
        
        with self.assertRaises(NotFoundError):
            ShelterService.verify_shelter(1, 1)


class TestValidateCsvFile(unittest.TestCase):
    """測試 CSV 檔案驗證"""
    
    def test_validate_csv_success(self):
        """測試成功驗證 CSV"""
        csv_content = b"name,age\nBuddy,3\nMax,5\n"
        file = FileStorage(
            stream=BytesIO(csv_content),
            filename='animals.csv',
            content_type='text/csv'
        )
        
        content, info = ShelterService.validate_csv_file(file)
        
        self.assertIn('Buddy', content)
        self.assertEqual(info['filename'], 'animals.csv')
        self.assertLess(info['size'], 100)
    
    def test_validate_csv_no_file(self):
        """測試未選擇檔案"""
        with self.assertRaises(ValidationError) as context:
            ShelterService.validate_csv_file(None)
        self.assertIn('未選擇檔案', str(context.exception))
    
    def test_validate_csv_wrong_extension(self):
        """測試錯誤的檔案格式"""
        file = FileStorage(
            stream=BytesIO(b"test"),
            filename='test.txt',
            content_type='text/plain'
        )
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.validate_csv_file(file)
        self.assertIn('檔案必須為 CSV 格式', str(context.exception))
    
    def test_validate_csv_file_too_large(self):
        """測試檔案過大"""
        large_content = b"a" * (11 * 1024 * 1024)  # 11MB
        file = FileStorage(
            stream=BytesIO(large_content),
            filename='large.csv',
            content_type='text/csv'
        )
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.validate_csv_file(file)
        self.assertIn('檔案不能超過', str(context.exception))
    
    def test_validate_csv_empty_file(self):
        """測試空的 CSV 檔案"""
        file = FileStorage(
            stream=BytesIO(b""),
            filename='empty.csv',
            content_type='text/csv'
        )
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.validate_csv_file(file)
        self.assertIn('CSV 檔案為空', str(context.exception))
    
    def test_validate_csv_invalid_encoding(self):
        """測試無效的編碼"""
        # 使用無法解碼的字節
        invalid_content = b'\xff\xfe'
        file = FileStorage(
            stream=BytesIO(invalid_content),
            filename='invalid.csv',
            content_type='text/csv'
        )
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.validate_csv_file(file)
        self.assertIn('CSV 編碼錯誤', str(context.exception))


class TestListShelters(unittest.TestCase):
    """測試列出收容所"""
    
    @patch('app.services.shelter_service.Shelter')
    def test_list_shelters_success(self, mock_shelter_model):
        """測試成功列出收容所"""
        mock_shelters = [
            Mock(shelter_id=1, name='Shelter 1', to_dict=lambda: {'shelter_id': 1}),
            Mock(shelter_id=2, name='Shelter 2', to_dict=lambda: {'shelter_id': 2}),
        ]
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_paginate = Mock()
        mock_paginate.items = mock_shelters
        mock_paginate.total = 2
        mock_paginate.pages = 1
        mock_query.paginate.return_value = mock_paginate
        
        mock_shelter_model.query = mock_query
        
        result = ShelterService.list_shelters(page=1, per_page=10)
        
        self.assertEqual(len(result['shelters']), 2)
        self.assertEqual(result['total'], 2)
        self.assertEqual(result['pages'], 1)
    
    @patch('app.services.shelter_service.db')
    @patch('app.services.shelter_service.Shelter')
    def test_list_shelters_with_search(self, mock_shelter_model, mock_db):
        """測試搜尋收容所"""
        mock_shelters = [Mock(shelter_id=1, name='Test Shelter', to_dict=lambda: {'shelter_id': 1})]
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_paginate = Mock()
        mock_paginate.items = mock_shelters
        mock_paginate.total = 1
        mock_paginate.pages = 1
        mock_query.paginate.return_value = mock_paginate
        
        mock_shelter_model.query = mock_query
        
        # Mock db.or_ to avoid SQLAlchemy errors
        mock_db.or_ = Mock(return_value=Mock())
        
        result = ShelterService.list_shelters(search='Test')
        
        self.assertEqual(len(result['shelters']), 1)
    
    @patch('app.services.shelter_service.Shelter')
    def test_list_shelters_verified_only(self, mock_shelter_model):
        """測試只列出已驗證的收容所"""
        mock_shelters = [Mock(shelter_id=1, verified=True, to_dict=lambda: {'shelter_id': 1})]
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_paginate = Mock()
        mock_paginate.items = mock_shelters
        mock_paginate.total = 1
        mock_paginate.pages = 1
        mock_query.paginate.return_value = mock_paginate
        
        mock_shelter_model.query = mock_query
        
        result = ShelterService.list_shelters(verified_only=True)
        
        self.assertEqual(len(result['shelters']), 1)


class TestGetShelter(unittest.TestCase):
    """測試獲取單個收容所"""
    
    @patch('app.services.shelter_service.Shelter')
    def test_get_shelter_success(self, mock_shelter_model):
        """測試成功獲取收容所"""
        mock_shelter = Mock()
        mock_shelter.shelter_id = 1
        mock_shelter.name = 'Test Shelter'
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_query
        
        result = ShelterService.get_shelter(1)
        
        self.assertEqual(result.shelter_id, 1)
        self.assertEqual(result.name, 'Test Shelter')
    
    @patch('app.services.shelter_service.Shelter')
    def test_get_shelter_not_found(self, mock_shelter_model):
        """測試收容所不存在"""
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_shelter_model.query = mock_query
        
        with self.assertRaises(NotFoundError):
            ShelterService.get_shelter(999)


class TestBatchUpdateAnimalStatus(unittest.TestCase):
    """測試批次更新動物狀態"""
    
    @patch('app.services.shelter_service.NotificationService')
    @patch('app.services.shelter_service.Animal')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.db')
    def test_batch_update_success(self, mock_db, mock_check_perm, mock_shelter_model, mock_animal_model, mock_notif):
        """測試成功批次更新動物狀態"""
        mock_check_perm.return_value = True
        
        # Mock shelter
        mock_shelter = Mock(shelter_id=1)
        mock_shelter_query = Mock()
        mock_shelter_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_shelter_query
        
        mock_animals = [
            Mock(animal_id=1, status=AnimalStatus.DRAFT, shelter_id=1),
            Mock(animal_id=2, status=AnimalStatus.DRAFT, shelter_id=1),
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_animals
        mock_animal_model.query = mock_query
        
        result = ShelterService.batch_update_animal_status(
            shelter_id=1,
            user_id=1,
            animal_ids=[1, 2],
            action='publish'
        )
        
        self.assertEqual(result['success_count'], 2)
        self.assertEqual(result['failed_count'], 0)
        mock_db.session.commit.assert_called()
    
    @patch('app.services.shelter_service.Shelter')
    def test_batch_update_shelter_not_found(self, mock_shelter_model):
        """測試收容所不存在"""
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_shelter_model.query = mock_query
        
        with self.assertRaises(NotFoundError):
            ShelterService.batch_update_animal_status(1, 1, [1, 2], 'publish')
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    def test_batch_update_invalid_action(self, mock_shelter_model, mock_check_perm):
        """測試無效的操作類型"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_query
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.batch_update_animal_status(1, 1, [1, 2], 'invalid_action')
        self.assertIn('無效的操作類型', str(context.exception))
    
    @patch('app.services.shelter_service.Animal')
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    def test_batch_update_animals_not_found(self, mock_shelter_model, mock_check_perm, mock_animal_model):
        """測試動物不存在"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_shelter_query = Mock()
        mock_shelter_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_shelter_query
        
        # 只找到一個動物，但請求了兩個
        mock_animal = Mock(animal_id=1)
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [mock_animal]
        mock_animal_model.query = mock_query
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.batch_update_animal_status(1, 1, [1, 2], 'publish')
        self.assertIn('不存在或不屬於該收容所', str(context.exception))


class TestUploadFileToMinio(unittest.TestCase):
    """測試上傳檔案到 MinIO"""
    
    def test_upload_success(self):
        """測試成功上傳檔案"""
        csv_content = b"name,age\nBuddy,3\n"
        file = FileStorage(
            stream=BytesIO(csv_content),
            filename='test.csv',
            content_type='text/csv'
        )
        
        mock_minio = Mock()
        mock_minio.put_object.return_value = None
        
        result = ShelterService.upload_file_to_minio(
            file=file,
            minio_client=mock_minio,
            bucket='test-bucket',
            object_key_prefix='uploads',
            allowed_types=['text/csv'],
            max_size_mb=10
        )
        
        self.assertEqual(result['filename'], 'test.csv')
        self.assertIn('storage_key', result)
        self.assertIn('url', result)
        self.assertEqual(result['content_type'], 'text/csv')
        mock_minio.put_object.assert_called_once()
    
    def test_upload_invalid_content_type(self):
        """測試不支援的檔案類型"""
        file = FileStorage(
            stream=BytesIO(b"test"),
            filename='test.txt',
            content_type='text/plain'
        )
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.upload_file_to_minio(
                file=file,
                minio_client=Mock(),
                bucket='test',
                object_key_prefix='uploads',
                allowed_types=['text/csv']
            )
        self.assertIn('檔案格式不支援', str(context.exception))
    
    def test_upload_file_too_large(self):
        """測試檔案過大"""
        large_content = b"a" * (11 * 1024 * 1024)  # 11MB
        file = FileStorage(
            stream=BytesIO(large_content),
            filename='large.csv',
            content_type='text/csv'
        )
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.upload_file_to_minio(
                file=file,
                minio_client=Mock(),
                bucket='test',
                object_key_prefix='uploads',
                allowed_types=['text/csv'],
                max_size_mb=10
            )
        self.assertIn('超過', str(context.exception))
    
    def test_upload_minio_error(self):
        """測試 MinIO 上傳失敗"""
        file = FileStorage(
            stream=BytesIO(b"test"),
            filename='test.csv',
            content_type='text/csv'
        )
        
        mock_minio = Mock()
        mock_minio.put_object.side_effect = Exception('Connection error')
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.upload_file_to_minio(
                file=file,
                minio_client=mock_minio,
                bucket='test',
                object_key_prefix='uploads',
                allowed_types=['text/csv']
            )
        self.assertIn('上傳檔案到 MinIO 失敗', str(context.exception))


class TestCreateBatchImportJob(unittest.TestCase):
    """測試創建批次匯入任務"""
    
    @patch('app.tasks.process_animal_batch_import')
    @patch('app.services.shelter_service.Job')
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.db')
    def test_create_batch_import_success(self, mock_db, mock_shelter_model, mock_check_perm, mock_job_model, mock_task):
        """測試成功創建批次匯入任務"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_query
        
        mock_job = Mock(job_id=1)
        mock_job_model.return_value = mock_job
        
        result = ShelterService.create_batch_import_job(
            shelter_id=1,
            user_id=1,
            animal_csv_content='name,age\nBuddy,3',
            animal_csv_filename='animals.csv'
        )
        
        self.assertEqual(result.job_id, 1)
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        mock_task.delay.assert_called_once_with(1)
    
    @patch('app.services.shelter_service.Shelter')
    def test_create_batch_import_shelter_not_found(self, mock_shelter_model):
        """測試收容所不存在"""
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_shelter_model.query = mock_query
        
        with self.assertRaises(NotFoundError):
            ShelterService.create_batch_import_job(1, 1, 'content', 'file.csv')


class TestUpdateShelterEdgeCases(unittest.TestCase):
    """測試更新收容所的邊界情況"""
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.db')
    def test_update_address_missing_fields(self, mock_db, mock_shelter_model, mock_check_perm):
        """測試更新地址時缺少必填欄位"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_query
        
        incomplete_address = {
            'street': '123 Main St',
            'city': 'City'
            # 缺少 county 和 postal_code
        }
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.update_shelter(1, 1, address=incomplete_address)
        self.assertIn('地址缺少必填欄位', str(context.exception))
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.db')
    def test_update_address_invalid_type(self, mock_db, mock_shelter_model, mock_check_perm):
        """測試更新地址時類型錯誤"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_query
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.update_shelter(1, 1, address='not a dict')
        self.assertIn('地址必須為 JSON 對象', str(context.exception))


class TestBatchUpdateAnimalStatusActions(unittest.TestCase):
    """測試批次更新動物狀態的各種操作"""
    
    @patch('app.services.shelter_service.NotificationService')
    @patch('app.services.shelter_service.Animal')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.db')
    def test_batch_update_draft_action(self, mock_db, mock_check_perm, mock_shelter_model, mock_animal_model, mock_notif):
        """測試批次轉為草稿"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_shelter_query = Mock()
        mock_shelter_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_shelter_query
        
        mock_animals = [
            Mock(animal_id=1, name='Animal1', status=AnimalStatus.PUBLISHED, shelter_id=1),
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_animals
        mock_animal_model.query = mock_query
        
        result = ShelterService.batch_update_animal_status(1, 1, [1], 'draft')
        
        self.assertEqual(result['success_count'], 1)
        self.assertEqual(mock_animals[0].status, AnimalStatus.DRAFT)
    
    @patch('app.services.shelter_service.NotificationService')
    @patch('app.services.shelter_service.Animal')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.db')
    def test_batch_update_submit_action(self, mock_db, mock_check_perm, mock_shelter_model, mock_animal_model, mock_notif):
        """測試批次提交審核"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_shelter_query = Mock()
        mock_shelter_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_shelter_query
        
        mock_animals = [
            Mock(animal_id=1, name='Animal1', status=AnimalStatus.DRAFT, shelter_id=1),
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_animals
        mock_animal_model.query = mock_query
        
        result = ShelterService.batch_update_animal_status(1, 1, [1], 'submit')
        
        self.assertEqual(result['success_count'], 1)
        self.assertEqual(mock_animals[0].status, AnimalStatus.SUBMITTED)
    
    @patch('app.services.shelter_service.NotificationService')
    @patch('app.services.shelter_service.Animal')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.db')
    def test_batch_update_retire_action(self, mock_db, mock_check_perm, mock_shelter_model, mock_animal_model, mock_notif):
        """測試批次下架"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_shelter_query = Mock()
        mock_shelter_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_shelter_query
        
        mock_animals = [
            Mock(animal_id=1, name='Animal1', status=AnimalStatus.PUBLISHED, shelter_id=1),
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_animals
        mock_animal_model.query = mock_query
        
        result = ShelterService.batch_update_animal_status(1, 1, [1], 'retire')
        
        self.assertEqual(result['success_count'], 1)
        self.assertEqual(mock_animals[0].status, AnimalStatus.RETIRED)
    
    @patch('app.services.shelter_service.NotificationService')
    @patch('app.services.shelter_service.Animal')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.db')
    def test_batch_update_failed_status_transition(self, mock_db, mock_check_perm, mock_shelter_model, mock_animal_model, mock_notif):
        """測試無效的狀態轉換"""
        mock_check_perm.return_value = True
        mock_shelter = Mock(shelter_id=1)
        mock_shelter_query = Mock()
        mock_shelter_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_shelter_query
        
        # 嘗試提交一個已發布的動物（應該失敗）
        mock_animals = [
            Mock(animal_id=1, name='Animal1', status=AnimalStatus.PUBLISHED, shelter_id=1),
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_animals
        mock_animal_model.query = mock_query
        
        result = ShelterService.batch_update_animal_status(1, 1, [1], 'submit')
        
        self.assertEqual(result['success_count'], 0)
        self.assertEqual(result['failed_count'], 1)
        self.assertIn('必須是草稿狀態才能提交', result['errors'][0])


class TestCheckShelterPermissionEdgeCases(unittest.TestCase):
    """測試權限檢查的邊界情況"""
    
    @patch('app.services.shelter_service.db')
    def test_shelter_member_can_create_new_shelter(self, mock_db):
        """測試收容所成員可以創建新收容所（無 shelter_id）"""
        mock_user = Mock(user_id=1, role=UserRole.SHELTER_MEMBER, primary_shelter_id=None)
        mock_db.session.get.return_value = mock_user
        
        result = ShelterService.check_shelter_permission(1, None)
        
        self.assertTrue(result)
    
    @patch('app.services.shelter_service.db')
    def test_shelter_primary_account_owner(self, mock_db):
        """測試收容所主要負責人有權限"""
        mock_user = Mock(user_id=1, role=UserRole.SHELTER_MEMBER, primary_shelter_id=None)
        mock_shelter = Mock(shelter_id=1, primary_account_user_id=1)
        
        mock_db.session.get.side_effect = lambda model, id: mock_user if model == User else mock_shelter
        
        result = ShelterService.check_shelter_permission(1, 1)
        
        self.assertTrue(result)


class TestUpdateShelterEdgeCases(unittest.TestCase):
    """測試更新收容所的邊界情況"""
    
    @patch('app.services.shelter_service.ShelterService.check_shelter_permission')
    @patch('app.services.shelter_service.Shelter')
    @patch('app.services.shelter_service.db')
    @patch('app.services.shelter_service.get_naive_taipei_now')
    def test_update_shelter_with_invalid_address_missing_fields(self, mock_now, mock_db, mock_shelter_model, mock_check_perm):
        """測試更新時地址缺少必填欄位"""
        mock_check_perm.return_value = True
        mock_now.return_value = datetime.utcnow()
        
        mock_shelter = Mock(shelter_id=1, name='Old Name')
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_shelter
        mock_shelter_model.query = mock_query
        
        address = {
            'street': '123 Main St',
            'city': 'City'
            # 缺少 county 和 postal_code
        }
        
        with self.assertRaises(ValidationError) as context:
            ShelterService.update_shelter(
                shelter_id=1,
                user_id=1,
                address=address
            )
        self.assertIn('地址缺少必填欄位', str(context.exception))


class TestBatchUpdateAnimalStatusEdgeCases(unittest.TestCase):
    """測試批次更新動物狀態的邊界情況"""


if __name__ == '__main__':
    unittest.main()
