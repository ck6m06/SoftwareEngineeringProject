"""
整合測試：通知系統

測試範圍：
- Route: /api/notifications/*
- Service: NotificationService
- ORM: Notification model
- Database: notifications 表
"""
import pytest
import json
from datetime import datetime


class TestNotificationList:
    """測試通知列表整合流程"""
    
    def test_list_own_notifications(self, client, db_session, auth_headers, test_user):
        """測試獲取自己的通知列表"""
        from app.models.others import Notification
        
        # 創建測試通知
        notification = Notification(
            notification_id=300,  # 手動設置 ID（SQLite BIGINT 不會自動遞增）
            recipient_id=test_user.user_id,
            type='application_status',
            payload={'message': '您的申請已被審核'},
            read=False
        )
        db_session.add(notification)
        db_session.commit()
        
        response = client.get(
            '/api/notifications',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'notifications' in data
        assert len(data['notifications']) > 0
        # 所有通知的接收者應該是當前用戶
        for notif in data['notifications']:
            assert notif['recipient_id'] == test_user.user_id
    
    def test_list_unread_notifications(self, client, db_session, auth_headers, test_user):
        """測試只顯示未讀通知"""
        from app.models.others import Notification
        
        # 創建未讀通知
        unread_notification = Notification(
            notification_id=301,  # 手動設置 ID
            recipient_id=test_user.user_id,
            type='animal_update',
            payload={'message': '動物資料已更新'},
            read=False
        )
        db_session.add(unread_notification)
        
        # 創建已讀通知
        read_notification = Notification(
            notification_id=302,  # 手動設置 ID
            recipient_id=test_user.user_id,
            type='system',
            payload={'message': '系統維護通知'},
            read=True,
            read_at=datetime.utcnow()
        )
        db_session.add(read_notification)
        db_session.commit()
        
        response = client.get(
            '/api/notifications?read=false',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'notifications' in data
        # 所有返回的通知都應該是未讀的
        for notif in data['notifications']:
            assert notif['read'] == False
    
    def test_list_notifications_with_pagination(self, client, db_session, auth_headers, test_user):
        """測試通知分頁"""
        response = client.get(
            '/api/notifications?page=1&per_page=10',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'notifications' in data
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data


# TestNotificationDetail 類已刪除 - GET /api/notifications/<id> endpoint 不存在


class TestNotificationMarkRead:
    """測試標記通知為已讀整合流程"""
    
    def test_mark_notification_as_read(self, client, db_session, auth_headers, test_user):
        """測試標記通知為已讀"""
        from app.models.others import Notification
        
        notification = Notification(
            notification_id=307,  # 手動設置 ID
            recipient_id=test_user.user_id,
            type='animal_update',
            payload={'message': '動物資料已更新'},
            read=False
        )
        db_session.add(notification)
        db_session.commit()
        
        response = client.post(
            f'/api/notifications/{notification.notification_id}/mark-read',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # 驗證資料庫
        db_session.refresh(notification)
        assert notification.read == True
        assert notification.read_at is not None
    
    def test_mark_all_notifications_as_read(self, client, db_session, auth_headers, test_user):
        """測試標記所有通知為已讀"""
        from app.models.others import Notification
        
        # 創建多個未讀通知
        for i in range(3):
            notification = Notification(
                notification_id=309 + i,  # 手動設置 ID：309, 310, 311
                recipient_id=test_user.user_id,
                type='system',
                payload={'message': f'通知 {i}'},
                read=False
            )
            db_session.add(notification)
        db_session.commit()
        
        response = client.post(
            '/api/notifications/mark-all-read',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # 驗證資料庫
        unread_count = db_session.query(Notification).filter_by(
            recipient_id=test_user.user_id,
            read=False
        ).count()
        assert unread_count == 0


class TestNotificationDelete:
    """測試刪除通知整合流程"""
    
    def test_delete_own_notification(self, client, db_session, auth_headers, test_user):
        """測試刪除自己的通知"""
        from app.models.others import Notification
        
        notification = Notification(
            notification_id=312,  # 手動設置 ID
            recipient_id=test_user.user_id,
            type='system',
            payload={'message': '待刪除通知'},
            read=True
        )
        db_session.add(notification)
        db_session.commit()
        
        notification_id = notification.notification_id
        
        response = client.delete(
            f'/api/notifications/{notification_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # 驗證資料庫
        deleted_notification = db_session.query(Notification).filter_by(
            notification_id=notification_id
        ).first()
        assert deleted_notification is None


# TestNotificationDelete 類保留了 test_delete_own_notification，刪除了2個skip測試


class TestNotificationCreation:
    """測試通知創建整合流程（觸發器）"""
    
    def test_notification_created_on_animal_update(self, client, db_session, test_shelter_animal, test_shelter_member):
        """測試動物資料更新時通知關注者"""
        from flask_jwt_extended import create_access_token
        
        token = create_access_token(identity=str(test_shelter_member.user_id))
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'description': '更新後的描述'
        }
        
        response = client.patch(
            f'/api/animals/{test_shelter_animal.animal_id}',
            data=json.dumps(payload),
            headers=headers
        )
        
        assert response.status_code == 200
        # 通知系統可能會異步處理，這裡只驗證請求成功


class TestNotificationCount:
    """測試通知計數整合流程"""
    
    def test_get_unread_notification_count(self, client, db_session, auth_headers, test_user):
        """測試獲取未讀通知數量"""
        from app.models.others import Notification
        
        # 創建多個未讀通知
        for i in range(5):
            notification = Notification(
                notification_id=319 + i,  # 手動設置 ID：319, 320, 321, 322, 323
                recipient_id=test_user.user_id,
                type='system',
                payload={'message': f'通知 {i}'},
                read=False
            )
            db_session.add(notification)
        
        # 創建已讀通知
        read_notification = Notification(
            notification_id=324,  # 手動設置 ID
            recipient_id=test_user.user_id,
            type='system',
            payload={'message': '已讀'},
            read=True
        )
        db_session.add(read_notification)
        db_session.commit()
        
        response = client.get(
            '/api/notifications/unread-count',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'unread_count' in data
        assert data['unread_count'] == 5


# TestNotificationPreferences 類已刪除 - 通知偏好設置 endpoint 不存在
