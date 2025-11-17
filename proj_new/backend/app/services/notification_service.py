"""
Notification Service - 通知相關業務邏輯
"""
from datetime import datetime
from flask import current_app
from app import db
from app.models.others import Notification
from app.models.user import User


class NotificationService:
    """通知業務邏輯服務"""

    @staticmethod
    def list_notifications(user_id, filters=None, pagination=None):
        """
        獲取用戶通知列表
        
        Args:
            user_id: 用戶ID
            filters: 篩選條件 {'read': bool}
            pagination: 分頁參數 {'page': int, 'per_page': int}
        
        Returns:
            dict: 通知列表數據
        """
        try:
            # 驗證用戶存在
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            filters = filters or {}
            pagination = pagination or {'page': 1, 'per_page': 20}
            
            # 構建查詢
            query = Notification.query.filter_by(recipient_id=user_id)
            
            # 篩選已讀/未讀
            if 'read' in filters and filters['read'] is not None:
                query = query.filter_by(read=filters['read'])
            
            # 分頁查詢並排序（最新通知在前）
            page = pagination.get('page', 1)
            per_page = pagination.get('per_page', 20)
            
            pagination_result = query.order_by(
                Notification.created_at.desc()
            ).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'notifications': [n.to_dict() for n in pagination_result.items],
                'total': pagination_result.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination_result.pages
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"List notifications error: {str(e)}")
            raise RuntimeError(f"獲取通知列表失敗: {str(e)}")

    @staticmethod
    def get_unread_count(user_id):
        """
        獲取用戶未讀通知數量
        
        Args:
            user_id: 用戶ID
        
        Returns:
            dict: 未讀通知數量
        """
        try:
            # 驗證用戶存在
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            count = Notification.query.filter_by(
                recipient_id=user_id,
                read=False
            ).count()
            
            return {'unread_count': count}
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Get unread count error: {str(e)}")
            raise RuntimeError(f"獲取未讀通知數量失敗: {str(e)}")

    @staticmethod
    def mark_notification_read(user_id, notification_id):
        """
        標記通知為已讀
        
        Args:
            user_id: 用戶ID
            notification_id: 通知ID
        
        Returns:
            dict: 更新後的通知數據
        """
        try:
            notification = Notification.query.filter_by(
                notification_id=notification_id,
                recipient_id=user_id
            ).first()
            
            if not notification:
                raise ValueError('通知不存在或無權限訪問')
            
            # 如果通知尚未讀取，則標記為已讀
            if not notification.read:
                notification.read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()
            
            return {
                'message': '通知已標記為已讀',
                'notification': notification.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Mark notification read error: {str(e)}")
            raise RuntimeError(f"標記通知已讀失敗: {str(e)}")

    @staticmethod
    def mark_all_read(user_id):
        """
        標記所有通知為已讀
        
        Args:
            user_id: 用戶ID
        
        Returns:
            dict: 操作結果
        """
        try:
            # 驗證用戶存在
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            # 批量更新未讀通知
            updated_count = Notification.query.filter_by(
                recipient_id=user_id,
                read=False
            ).update({
                'read': True,
                'read_at': datetime.utcnow()
            })
            
            db.session.commit()
            
            return {
                'message': f'已標記 {updated_count} 條通知為已讀',
                'updated_count': updated_count
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Mark all read error: {str(e)}")
            raise RuntimeError(f"批量標記已讀失敗: {str(e)}")

    @staticmethod
    def delete_notification(user_id, notification_id):
        """
        刪除通知
        
        Args:
            user_id: 用戶ID
            notification_id: 通知ID
        
        Returns:
            dict: 刪除結果
        """
        try:
            notification = Notification.query.filter_by(
                notification_id=notification_id,
                recipient_id=user_id
            ).first()
            
            if not notification:
                raise ValueError('通知不存在或無權限訪問')
            
            db.session.delete(notification)
            db.session.commit()
            
            return {'message': '通知已刪除'}
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Delete notification error: {str(e)}")
            raise RuntimeError(f"刪除通知失敗: {str(e)}")

    @staticmethod
    def create_notification(recipient_id, title, message, notification_type=None, 
                          related_id=None, action_url=None, priority='normal'):
        """
        創建新通知（系統內部使用）
        
        Args:
            recipient_id: 接收者用戶ID
            title: 通知標題
            message: 通知內容
            notification_type: 通知類型
            related_id: 相關對象ID
            action_url: 操作連結
            priority: 優先級 ('low', 'normal', 'high')
        
        Returns:
            Notification: 創建的通知對象
        """
        try:
            # 驗證接收者存在
            recipient = User.query.get(recipient_id)
            if not recipient:
                raise ValueError('接收者不存在')
            
            notification = Notification(
                recipient_id=recipient_id,
                title=title,
                message=message,
                type=notification_type,
                related_id=related_id,
                action_url=action_url,
                priority=priority,
                read=False
            )
            
            db.session.add(notification)
            db.session.flush()  # 獲取通知ID
            
            return notification
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Create notification error: {str(e)}")
            raise RuntimeError(f"創建通知失敗: {str(e)}")

    @staticmethod
    def get_notification_stats(user_id):
        """
        獲取用戶通知統計信息
        
        Args:
            user_id: 用戶ID
        
        Returns:
            dict: 通知統計數據
        """
        try:
            # 驗證用戶存在
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
            
            total_notifications = Notification.query.filter_by(
                recipient_id=user_id
            ).count()
            
            unread_notifications = Notification.query.filter_by(
                recipient_id=user_id,
                read=False
            ).count()
            
            read_notifications = total_notifications - unread_notifications
            
            return {
                'total': total_notifications,
                'unread': unread_notifications,
                'read': read_notifications,
                'read_percentage': round(
                    (read_notifications / total_notifications * 100) if total_notifications > 0 else 0, 
                    2
                )
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Get notification stats error: {str(e)}")
            raise RuntimeError(f"獲取通知統計失敗: {str(e)}")

    # 業務通知創建方法
    @staticmethod
    def notify_application_submitted(application, applicant_name, animal_name):
        """申請提交通知"""
        from app.models.animal import Animal
        
        animal = Animal.query.get(application.animal_id)
        if not animal:
            return None
        
        # 確定接收者
        recipient_id = animal.owner_id
        if not recipient_id and animal.shelter_id:
            from app.models.shelter import Shelter
            shelter = Shelter.query.get(animal.shelter_id)
            if shelter:
                recipient_id = shelter.primary_account_user_id
        
        if not recipient_id:
            return None
        
        return NotificationService.create_notification(
            recipient_id=recipient_id,
            title='新的領養申請',
            message=f'{applicant_name} 申請領養 {animal_name}',
            notification_type='application_submitted',
            related_id=application.application_id,
            action_url=f'/applications/{application.application_id}'
        )

    @staticmethod
    def notify_application_reviewed(application, reviewer_id, status, review_notes=None):
        """申請審核結果通知"""
        from app.models.animal import Animal
        
        animal = Animal.query.get(application.animal_id)
        animal_name = animal.name if animal else '未知動物'
        
        status_text = '通過' if status == 'APPROVED' else '拒絕'
        notification_type = 'application_approved' if status == 'APPROVED' else 'application_rejected'
        
        message = f'您的 {animal_name} 領養申請已{status_text}'
        if review_notes:
            message += f'，備註：{review_notes}'
        
        return NotificationService.create_notification(
            recipient_id=application.applicant_id,
            title=f'領養申請{status_text}',
            message=message,
            notification_type=notification_type,
            related_id=application.application_id,
            action_url=f'/applications/{application.application_id}'
        )
