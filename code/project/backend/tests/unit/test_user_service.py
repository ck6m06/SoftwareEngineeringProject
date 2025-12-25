"""
User Service unit tests
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from app.services.user_service import UserService
from app.models.user import UserRole
from app.exceptions import NotFoundError, PermissionDeniedError, ValidationError, ConflictError


class TestGetUser(unittest.TestCase):
    """Test get_user method"""
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_get_own_user_includes_sensitive_info(self, mock_user, mock_db):
        """Test getting own user includes sensitive info"""
        user = Mock(user_id=1, email='test@example.com', deleted_at=None)
        
        mock_db.session.get.return_value = user
        mock_user.query.filter_by.return_value.first.return_value = user
        
        result_user, include_sensitive = UserService.get_user(user_id=1, current_user_id=1)
        
        self.assertEqual(result_user, user)
        self.assertTrue(include_sensitive)
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_admin_can_view_sensitive_info(self, mock_user, mock_db):
        """Test admin can view others sensitive info"""
        admin = Mock(user_id=1, role=UserRole.ADMIN)
        target_user = Mock(user_id=2, email='user@example.com', deleted_at=None)
        
        mock_db.session.get.return_value = admin
        mock_user.query.filter_by.return_value.first.return_value = target_user
        
        result_user, include_sensitive = UserService.get_user(user_id=2, current_user_id=1)
        
        self.assertEqual(result_user, target_user)
        self.assertTrue(include_sensitive)
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_regular_user_cannot_view_others_sensitive_info(self, mock_user, mock_db):
        """Test regular user cannot view others sensitive info"""
        current_user = Mock(user_id=1, role=UserRole.GENERAL_MEMBER)
        target_user = Mock(user_id=2, email='user@example.com', deleted_at=None)
        
        mock_db.session.get.return_value = current_user
        mock_user.query.filter_by.return_value.first.return_value = target_user
        
        result_user, include_sensitive = UserService.get_user(user_id=2, current_user_id=1)
        
        self.assertEqual(result_user, target_user)
        self.assertFalse(include_sensitive)
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_user_not_found(self, mock_user, mock_db):
        """Test user not found raises exception"""
        mock_db.session.get.return_value = None  # current_user
        mock_user.query.filter_by.return_value.first.return_value = None
        
        with self.assertRaises(NotFoundError):
            UserService.get_user(user_id=999, current_user_id=1)


class TestUpdateUser(unittest.TestCase):
    """Test update_user method"""
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_user_can_update_own_info(self, mock_user, mock_db):
        """Test user can update own info"""
        user = Mock(user_id=1, username='oldname', email='test@example.com', deleted_at=None)
        
        mock_db.session.get.return_value = user
        mock_user.query.filter_by.return_value.first.return_value = user
        
        data = {'username': 'newname', 'phone_number': '1234567890'}
        result = UserService.update_user(user_id=1, current_user_id=1, data=data)
        
        self.assertEqual(user.username, 'newname')
        self.assertEqual(user.phone_number, '1234567890')
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_admin_can_update_user_role(self, mock_user, mock_db):
        """Test admin can update user role"""
        admin = Mock(user_id=1, role=UserRole.ADMIN)
        target_user = Mock(user_id=2, role=UserRole.GENERAL_MEMBER, deleted_at=None)
        
        mock_db.session.get.return_value = admin
        mock_user.query.filter_by.return_value.first.return_value = target_user
        
        data = {'role': UserRole.SHELTER_MEMBER}
        result = UserService.update_user(user_id=2, current_user_id=1, data=data)
        
        self.assertEqual(target_user.role, UserRole.SHELTER_MEMBER)
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_regular_user_cannot_update_role(self, mock_user, mock_db):
        """Test regular user cannot update role"""
        user = Mock(user_id=1, role=UserRole.GENERAL_MEMBER, deleted_at=None)
        
        mock_db.session.get.return_value = user
        mock_user.query.filter_by.return_value.first.return_value = user
        
        data = {'role': UserRole.ADMIN}
        result = UserService.update_user(user_id=1, current_user_id=1, data=data)
        
        # role not in allowed_fields, should be ignored
        self.assertEqual(user.role, UserRole.GENERAL_MEMBER)
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_update_email_requires_reverification(self, mock_user, mock_db):
        """Test updating email requires reverification"""
        user = Mock(user_id=1, email='old@example.com', verified=True, deleted_at=None)
        
        mock_db.session.get.return_value = user
        mock_user.query.filter_by.return_value.first.side_effect = [user, None]
        
        data = {'email': 'new@example.com'}
        result = UserService.update_user(user_id=1, current_user_id=1, data=data)
        
        self.assertEqual(user.email, 'new@example.com')
        self.assertFalse(user.verified)
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_duplicate_email_raises_conflict(self, mock_user, mock_db):
        """Test duplicate email raises conflict"""
        user = Mock(user_id=1, email='test@example.com', deleted_at=None)
        existing_user = Mock(user_id=2, email='existing@example.com', deleted_at=None)
        
        mock_db.session.get.return_value = user
        mock_user.query.filter_by.side_effect = [
            Mock(first=lambda: user),
            Mock(first=lambda: existing_user)
        ]
        
        data = {'email': 'existing@example.com'}
        
        with self.assertRaises(ConflictError):
            UserService.update_user(user_id=1, current_user_id=1, data=data)
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_unauthorized_update_raises_permission_denied(self, mock_user, mock_db):
        """Test unauthorized update raises permission denied"""
        current_user = Mock(user_id=1, role=UserRole.GENERAL_MEMBER)
        target_user = Mock(user_id=2, deleted_at=None)
        
        mock_db.session.get.return_value = current_user
        mock_user.query.filter_by.return_value.first.return_value = target_user
        
        data = {'username': 'newname'}
        
        with self.assertRaises(PermissionDeniedError):
            UserService.update_user(user_id=2, current_user_id=1, data=data)


class TestChangePassword(unittest.TestCase):
    """Test change_password method"""
    
    @patch('app.services.user_service.verify_password')
    @patch('app.services.user_service.hash_password')
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_change_password_success(self, mock_user, mock_db, mock_hash, mock_verify):
        """Test successfully changing password"""
        user = Mock(
            user_id=1,
            password_hash='old_hash',
            deleted_at=None,
            failed_login_attempts=3
        )
        user.locked_until = None
        
        mock_user.query.filter_by.return_value.first.return_value = user
        mock_verify.return_value = True
        mock_hash.return_value = 'new_hash'
        
        UserService.change_password(
            user_id=1,
            current_user_id=1,
            old_password='old_password',
            new_password='new_password123'
        )
        
        self.assertEqual(user.password_hash, 'new_hash')
        self.assertEqual(user.failed_login_attempts, 0)
        mock_db.session.commit.assert_called_once()
    
    def test_cannot_change_others_password(self):
        """Test cannot change others password"""
        with self.assertRaises(PermissionDeniedError):
            UserService.change_password(
                user_id=2,
                current_user_id=1,
                old_password='old',
                new_password='new'
            )
    
    @patch('app.services.user_service.verify_password')
    @patch('app.services.user_service.User')
    def test_wrong_old_password_raises_validation_error(self, mock_user, mock_verify):
        """Test wrong old password raises validation error"""
        user = Mock(user_id=1, password_hash='old_hash', deleted_at=None)
        
        mock_user.query.filter_by.return_value.first.return_value = user
        mock_verify.return_value = False
        
        with self.assertRaises(ValidationError):
            UserService.change_password(
                user_id=1,
                current_user_id=1,
                old_password='wrong_password',
                new_password='new_password123'
            )
    
    @patch('app.services.user_service.verify_password')
    @patch('app.services.user_service.User')
    def test_short_new_password_raises_validation_error(self, mock_user, mock_verify):
        """Test short new password raises validation error"""
        user = Mock(user_id=1, password_hash='old_hash', deleted_at=None)
        
        mock_user.query.filter_by.return_value.first.return_value = user
        mock_verify.return_value = True
        
        with self.assertRaises(ValidationError):
            UserService.change_password(
                user_id=1,
                current_user_id=1,
                old_password='old_password',
                new_password='short'
            )


class TestRequestDataExport(unittest.TestCase):
    """Test request_data_export method"""
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    @patch('app.services.user_service.Job')
    def test_request_data_export_success(self, mock_job_model, mock_user, mock_db):
        """Test successfully requesting data export"""
        user = Mock(user_id=1, deleted_at=None)
        job = Mock(job_id=100)
        
        mock_user.query.filter_by.return_value.first.return_value = user
        mock_job_model.return_value = job
        
        job_id = UserService.request_data_export(user_id=1, current_user_id=1)
        
        self.assertEqual(job_id, 100)
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.user_service.User')
    def test_cannot_export_others_data(self, mock_user):
        """Test cannot export others data"""
        with self.assertRaises(PermissionDeniedError):
            UserService.request_data_export(user_id=2, current_user_id=1)
    
    @patch('app.services.user_service.User')
    def test_export_user_not_found(self, mock_user):
        """Test export fails when user not found"""
        mock_user.query.filter_by.return_value.first.return_value = None
        
        with self.assertRaises(NotFoundError):
            UserService.request_data_export(user_id=1, current_user_id=1)


class TestRequestDataDeletion(unittest.TestCase):
    """Test request_data_deletion method"""
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    @patch('app.services.user_service.Job')
    def test_user_can_request_own_deletion(self, mock_job_model, mock_user, mock_db):
        """Test user can request own data deletion"""
        user = Mock(user_id=1, deleted_at=None)
        job = Mock(job_id=101)
        
        mock_db.session.get.return_value = user
        mock_user.query.filter_by.return_value.first.return_value = user
        mock_job_model.return_value = job
        
        job_id = UserService.request_data_deletion(user_id=1, current_user_id=1)
        
        self.assertEqual(job_id, 101)
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    @patch('app.services.user_service.Job')
    def test_admin_can_delete_user_data(self, mock_job_model, mock_user, mock_db):
        """Test admin can delete user data"""
        admin = Mock(user_id=1, role=UserRole.ADMIN)
        target_user = Mock(user_id=2, deleted_at=None)
        job = Mock(job_id=102)
        
        mock_db.session.get.return_value = admin
        mock_user.query.filter_by.return_value.first.return_value = target_user
        mock_job_model.return_value = job
        
        job_id = UserService.request_data_deletion(user_id=2, current_user_id=1)
        
        self.assertEqual(job_id, 102)
    
    @patch('app.services.user_service.db')
    def test_cannot_delete_others_data(self, mock_db):
        """Test regular user cannot delete others data"""
        regular_user = Mock(user_id=1, role=UserRole.GENERAL_MEMBER)
        mock_db.session.get.return_value = regular_user
        
        with self.assertRaises(PermissionDeniedError):
            UserService.request_data_deletion(user_id=2, current_user_id=1)
    
    @patch('app.services.user_service.db')
    @patch('app.services.user_service.User')
    def test_deletion_user_not_found(self, mock_user, mock_db):
        """Test deletion fails when user not found"""
        admin = Mock(user_id=1, role=UserRole.ADMIN)
        mock_db.session.get.return_value = admin
        mock_user.query.filter_by.return_value.first.return_value = None
        
        with self.assertRaises(NotFoundError):
            UserService.request_data_deletion(user_id=999, current_user_id=1)


class TestChangePasswordEdgeCases(unittest.TestCase):
    """Test change_password edge cases"""
    
    @patch('app.services.user_service.User')
    def test_missing_old_password(self, mock_user):
        """Test missing old password raises validation error"""
        user = Mock(user_id=1, deleted_at=None)
        mock_user.query.filter_by.return_value.first.return_value = user
        
        with self.assertRaises(ValidationError):
            UserService.change_password(
                user_id=1,
                current_user_id=1,
                old_password='',
                new_password='newpass123'
            )
    
    @patch('app.services.user_service.User')
    def test_missing_new_password(self, mock_user):
        """Test missing new password raises validation error"""
        user = Mock(user_id=1, deleted_at=None)
        mock_user.query.filter_by.return_value.first.return_value = user
        
        with self.assertRaises(ValidationError):
            UserService.change_password(
                user_id=1,
                current_user_id=1,
                old_password='oldpass',
                new_password=''
            )
    
    @patch('app.services.user_service.User')
    def test_change_password_user_not_found(self, mock_user):
        """Test change password fails when user not found"""
        mock_user.query.filter_by.return_value.first.return_value = None
        
        with self.assertRaises(NotFoundError):
            UserService.change_password(
                user_id=999,
                current_user_id=999,
                old_password='old',
                new_password='new12345'
            )


if __name__ == '__main__':
    unittest.main()
