"""
Notification Service unit tests
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from app.services.notification_service import NotificationService
from app.exceptions import NotFoundError, PermissionDeniedError


class TestCreate(unittest.TestCase):
    """Test create method"""
    
    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_create_notification_success(self, mock_notification, mock_db):
        """Test successfully creating notification"""
        mock_db.session.execute.return_value.scalar.return_value = 5
        notification_instance = Mock(notification_id=6)
        mock_notification.return_value = notification_instance
        
        result = NotificationService.create(
            recipient_id=1,
            type='test_notification',
            actor_id=2,
            payload={'message': 'Test'},
            commit=True
        )
        
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        self.assertEqual(result, notification_instance)
    
    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_create_without_commit(self, mock_notification, mock_db):
        """Test creating notification without commit"""
        mock_db.session.execute.return_value.scalar.return_value = 0
        notification_instance = Mock(notification_id=1)
        mock_notification.return_value = notification_instance
        
        result = NotificationService.create(
            recipient_id=1,
            type='test_notification',
            commit=False
        )
        
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_not_called()


class TestNotifyApplicationSubmitted(unittest.TestCase):
    """Test notify_application_submitted method"""
    
    @patch('app.services.notification_service.NotificationService.create')
    @patch('app.models.animal.Animal')
    def test_notify_when_owner_exists(self, mock_animal_model, mock_create):
        """Test notification when animal owner exists"""
        application = Mock(application_id=1, animal_id=1, applicant_id=2, type=Mock(value='ADOPT'))
        animal = Mock(animal_id=1, owner_id=3, shelter_id=None)
        
        mock_animal_model.query.get.return_value = animal
        mock_create.return_value = Mock(notification_id=1)
        
        result = NotificationService.notify_application_submitted(
            application=application,
            applicant_name='John Doe',
            animal_name='Buddy'
        )
        
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs['recipient_id'], 3)
        self.assertEqual(call_kwargs['type'], 'application_submitted')
        self.assertEqual(call_kwargs['actor_id'], 2)
    
    @patch('app.services.notification_service.NotificationService.create')
    @patch('app.models.shelter.Shelter')
    @patch('app.models.animal.Animal')
    def test_notify_when_shelter_animal(self, mock_animal_model, mock_shelter_model, mock_create):
        """Test notification when animal belongs to shelter"""
        shelter = Mock(shelter_id=1, primary_account_user_id=4)
        application = Mock(application_id=1, animal_id=1, applicant_id=2, type=Mock(value='ADOPT'))
        animal = Mock(animal_id=1, owner_id=None, shelter_id=1)
        
        mock_animal_model.query.get.return_value = animal
        mock_shelter_model.query.get.return_value = shelter
        mock_create.return_value = Mock(notification_id=1)
        
        result = NotificationService.notify_application_submitted(
            application=application,
            applicant_name='John Doe',
            animal_name='Buddy'
        )
        
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs['recipient_id'], 4)
    
    @patch('app.models.animal.Animal')
    def test_no_notification_when_animal_not_found(self, mock_animal_model):
        """Test no notification when animal doesn't exist"""
        mock_animal_model.query.get.return_value = None
        application = Mock(application_id=1, animal_id=999)
        
        result = NotificationService.notify_application_submitted(
            application=application,
            applicant_name='John Doe',
            animal_name='Buddy'
        )
        
        self.assertIsNone(result)


class TestNotifyApplicationReviewed(unittest.TestCase):
    """Test notify_application_reviewed method"""
    
    @patch('app.services.notification_service.NotificationService.create')
    @patch('app.models.animal.Animal')
    def test_notify_application_approved(self, mock_animal_model, mock_create):
        """Test notification when application is approved"""
        application = Mock(application_id=1, animal_id=1, applicant_id=2, type=Mock(value='ADOPT'))
        animal = Mock(animal_id=1, name='Buddy')
        
        mock_animal_model.query.get.return_value = animal
        mock_create.return_value = Mock(notification_id=1)
        
        result = NotificationService.notify_application_reviewed(
            application=application,
            reviewer_id=3,
            status='APPROVED',
            review_notes='Looks good'
        )
        
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs['recipient_id'], 2)
        self.assertEqual(call_kwargs['type'], 'application_approved')


class TestListNotifications(unittest.TestCase):
    """Test list_notifications method"""
    
    @patch('app.services.notification_service.Notification')
    def test_list_all_notifications(self, mock_notification):
        """Test listing all notifications"""
        notifications = [
            Mock(notification_id=1, read=False, to_dict=lambda: {'notification_id': 1}),
            Mock(notification_id=2, read=True, to_dict=lambda: {'notification_id': 2})
        ]
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = Mock(
            items=notifications,
            total=2,
            page=1,
            pages=1
        )
        mock_notification.query = mock_query
        
        result = NotificationService.list_notifications(user_id=1, page=1, per_page=20)
        
        self.assertEqual(len(result['notifications']), 2)
        self.assertEqual(result['total'], 2)
    
    @patch('app.services.notification_service.Notification')
    def test_list_unread_notifications_only(self, mock_notification):
        """Test listing unread notifications only"""
        notifications = [
            Mock(notification_id=1, read=False, to_dict=lambda: {'notification_id': 1})
        ]
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = Mock(
            items=notifications,
            total=1,
            page=1,
            pages=1
        )
        mock_notification.query = mock_query
        
        result = NotificationService.list_notifications(
            user_id=1,
            read_filter='unread',
            page=1,
            per_page=20
        )
        
        self.assertEqual(len(result['notifications']), 1)


class TestGetUnreadCount(unittest.TestCase):
    """Test get_unread_count method"""
    
    @patch('app.services.notification_service.Notification')
    def test_get_unread_count(self, mock_notification):
        """Test getting unread count"""
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.count.return_value = 5
        mock_notification.query = mock_query
        
        count = NotificationService.get_unread_count(user_id=1)
        
        self.assertEqual(count, 5)


class TestMarkAsRead(unittest.TestCase):
    """Test mark_as_read method"""
    
    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_mark_notification_as_read(self, mock_notification, mock_db):
        """Test marking notification as read"""
        notification = Mock(notification_id=1, recipient_id=1, read=False)
        mock_notification.query.filter_by.return_value.first.return_value = notification
        
        result = NotificationService.mark_as_read(notification_id=1, user_id=1)
        
        self.assertTrue(notification.read)
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.notification_service.Notification')
    def test_mark_as_read_not_found(self, mock_notification):
        """Test marking non-existent notification"""
        mock_notification.query.filter_by.return_value.first.return_value = None
        
        with self.assertRaises(ValueError):
            NotificationService.mark_as_read(notification_id=999, user_id=1)
    
    @patch('app.services.notification_service.Notification')
    def test_mark_as_read_permission_denied(self, mock_notification):
        """Test permission denied when marking others notification"""
        # filter_by with recipient_id already filters by user, so this returns None
        mock_notification.query.filter_by.return_value.first.return_value = None
        
        with self.assertRaises(ValueError):
            NotificationService.mark_as_read(notification_id=1, user_id=1)


class TestMarkAllAsRead(unittest.TestCase):
    """Test mark_all_as_read method"""
    
    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_mark_all_notifications_as_read(self, mock_notification, mock_db):
        """Test marking all notifications as read"""
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.update.return_value = 2  # Returns count of updated rows
        mock_notification.query = mock_query
        
        count = NotificationService.mark_all_as_read(user_id=1)
        
        self.assertEqual(count, 2)
        mock_db.session.commit.assert_called_once()


class TestDeleteNotification(unittest.TestCase):
    """Test delete_notification method"""
    
    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_delete_notification_success(self, mock_notification, mock_db):
        """Test successfully deleting notification"""
        notification = Mock(notification_id=1, recipient_id=1)
        mock_notification.query.filter_by.return_value.first.return_value = notification
        
        NotificationService.delete_notification(notification_id=1, user_id=1)
        
        mock_db.session.delete.assert_called_once_with(notification)
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.notification_service.Notification')
    def test_delete_notification_not_found(self, mock_notification):
        """Test deleting non-existent notification"""
        mock_notification.query.filter_by.return_value.first.return_value = None
        
        with self.assertRaises(ValueError):
            NotificationService.delete_notification(notification_id=999, user_id=1)


class TestNotifyAnimalStatusChanged(unittest.TestCase):
    """Test notify_animal_status_changed method"""
    
    @patch('app.services.notification_service.NotificationService.create')
    def test_notify_owner_of_status_change(self, mock_create):
        """Test notifying animal owner of status change"""
        animal = Mock(animal_id=1, owner_id=3, shelter_id=None, name='Buddy')
        mock_create.return_value = Mock(notification_id=1)
        
        result = NotificationService.notify_animal_status_changed(
            animal=animal,
            old_status='DRAFT',
            new_status='PUBLISHED',
            changed_by_id=2
        )
        
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs['recipient_id'], 3)
        self.assertEqual(call_kwargs['type'], 'animal_status_changed')
    
    @patch('app.services.notification_service.NotificationService.create')
    @patch('app.models.shelter.Shelter')
    def test_notify_shelter_of_status_change(self, mock_shelter_model, mock_create):
        """Test notifying shelter of animal status change"""
        shelter = Mock(shelter_id=1, primary_account_user_id=4)
        animal = Mock(animal_id=1, owner_id=None, shelter_id=1, name='Max')
        
        mock_shelter_model.query.get.return_value = shelter
        mock_create.return_value = Mock(notification_id=1)
        
        result = NotificationService.notify_animal_status_changed(
            animal=animal,
            old_status='DRAFT',
            new_status='PUBLISHED',
            changed_by_id=2
        )
        
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs['recipient_id'], 4)


class TestNotifyJobCompleted(unittest.TestCase):
    """Test notify_job_completed method"""
    
    @patch('app.services.notification_service.NotificationService.create')
    def test_notify_job_creator_of_completion(self, mock_create):
        """Test notifying job creator of completion"""
        job = Mock(job_id=1, created_by=2, type='data_export', result_summary='Success')
        mock_create.return_value = Mock(notification_id=1)
        
        result = NotificationService.notify_job_completed(job=job, status='SUCCEEDED')
        
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs['recipient_id'], 2)
        self.assertEqual(call_kwargs['type'], 'job_completed')
    
    @patch('app.services.notification_service.NotificationService.create')
    def test_no_notification_when_no_creator(self, mock_create):
        """Test no notification when job has no creator"""
        job = Mock(job_id=1, created_by=None, type='system_job')
        
        result = NotificationService.notify_job_completed(job=job, status='SUCCEEDED')
        
        self.assertIsNone(result)
        mock_create.assert_not_called()


class TestNotifySystem(unittest.TestCase):
    """Test notify_system method"""
    
    @patch('app.services.notification_service.NotificationService.create')
    def test_send_system_notification(self, mock_create):
        """Test sending system notification"""
        mock_create.return_value = Mock(notification_id=1)
        
        result = NotificationService.notify_system(
            recipient_id=1,
            title='System Update',
            message='System will be down for maintenance',
            priority='HIGH'
        )
        
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs['recipient_id'], 1)
        self.assertEqual(call_kwargs['type'], 'system_notification')
        self.assertEqual(call_kwargs['actor_id'], None)
        self.assertEqual(call_kwargs['payload']['priority'], 'HIGH')


class TestNotifyApplicationUnderReview(unittest.TestCase):
    """Test notify_application_under_review method"""
    
    @patch('app.services.notification_service.NotificationService.create')
    @patch('app.models.animal.Animal')
    def test_notify_applicant_under_review(self, mock_animal_model, mock_create):
        """Test notifying applicant that application is under review"""
        application = Mock(application_id=1, animal_id=1, applicant_id=2)
        animal = Mock(animal_id=1, name='Buddy')
        
        mock_animal_model.query.get.return_value = animal
        mock_create.return_value = Mock(notification_id=1)
        
        result = NotificationService.notify_application_under_review(
            application=application,
            assignee_id=3,
            assignee_name='John Reviewer'
        )
        
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs['recipient_id'], 2)
        self.assertEqual(call_kwargs['type'], 'application_under_review')


if __name__ == '__main__':
    unittest.main()
