"""
User Service - 用戶相關業務邏輯
"""
from datetime import datetime
from flask import current_app
from app import db
from app.models.user import User, UserRole
from app.models.others import Job, JobStatus


class UserService:
    """用戶業務邏輯服務"""

    @staticmethod
    def get_user_profile(current_user_id, target_user_id):
        """
        獲取用戶資訊
        
        Args:
            current_user_id: 當前用戶ID
            target_user_id: 目標用戶ID
        
        Returns:
            dict: 用戶資訊
        """
        try:
            current_user = User.query.get(current_user_id)
            if not current_user:
                raise ValueError('當前用戶不存在')
            
            target_user = User.query.filter_by(
                user_id=target_user_id, 
                deleted_at=None
            ).first()
            
            if not target_user:
                raise ValueError('使用者不存在')
            
            # 檢查權限 - 只有本人或管理員可以查看完整資訊
            include_sensitive = (
                current_user_id == target_user_id or 
                current_user.role == UserRole.ADMIN
            )
            
            return {
                'user': target_user.to_dict(include_sensitive=include_sensitive)
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Get user profile error: {str(e)}")
            raise RuntimeError(f"獲取用戶資訊失敗: {str(e)}")

    @staticmethod
    def update_user_profile(current_user_id, target_user_id, data):
        """
        更新用戶資訊
        
        Args:
            current_user_id: 當前用戶ID
            target_user_id: 目標用戶ID
            data: 更新數據
        
        Returns:
            dict: 更新後的用戶資訊
        """
        try:
            current_user = User.query.get(current_user_id)
            if not current_user:
                raise ValueError('當前用戶不存在')
            
            target_user = User.query.filter_by(
                user_id=target_user_id, 
                deleted_at=None
            ).first()
            
            if not target_user:
                raise ValueError('使用者不存在')
            
            # 檢查權限 - 只有本人或管理員可以更新
            if current_user_id != target_user_id and current_user.role != UserRole.ADMIN:
                raise ValueError('沒有權限修改此使用者資訊')
            
            # 可更新的欄位
            allowed_fields = [
                'username', 'phone_number', 'first_name', 'last_name', 
                'profile_photo_url', 'settings', 'region', 'address'
            ]
            
            # 管理員可以更新額外欄位
            if current_user.role == UserRole.ADMIN:
                allowed_fields.extend(['role', 'verified', 'primary_shelter_id'])
            
            # 更新一般欄位
            for field in allowed_fields:
                if field in data:
                    setattr(target_user, field, data[field])
            
            # 特殊處理 email 更新 (需要重新驗證)
            if 'email' in data and data['email'] != target_user.email:
                UserService._validate_email_unique(data['email'], target_user_id)
                target_user.email = data['email']
                target_user.verified = False  # 需要重新驗證
            
            target_user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'message': '用戶資訊更新成功',
                'user': target_user.to_dict(include_sensitive=True)
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update user profile error: {str(e)}")
            raise RuntimeError(f"更新用戶資訊失敗: {str(e)}")

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        修改密碼
        
        Args:
            user_id: 用戶ID
            old_password: 舊密碼
            new_password: 新密碼
        
        Returns:
            dict: 操作結果
        """
        try:
            user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
            if not user:
                raise ValueError('使用者不存在')
            
            # 驗證參數
            if not old_password or not new_password:
                raise ValueError('old_password 和 new_password 為必填欄位')
            
            # 驗證新密碼長度
            if len(new_password) < 8:
                raise ValueError('新密碼長度至少需要 8 個字元')
            
            # 驗證舊密碼
            from app.utils.security import verify_password, hash_password
            if not verify_password(old_password, user.password_hash):
                raise ValueError('舊密碼錯誤')
            
            # 更新密碼
            user.password_hash = hash_password(new_password)
            
            # 更新密碼變更時間 (如果欄位存在)
            if hasattr(user, 'password_changed_at'):
                user.password_changed_at = datetime.utcnow()
            
            # 重置失敗登入次數
            if hasattr(user, 'failed_login_attempts'):
                user.failed_login_attempts = 0
            if hasattr(user, 'locked_until'):
                user.locked_until = None
            
            db.session.commit()
            
            return {'message': '密碼修改成功'}
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Change password error: {str(e)}")
            raise RuntimeError(f"密碼修改失敗: {str(e)}")

    @staticmethod
    def request_data_export(user_id):
        """
        請求個人資料匯出 (GDPR)
        
        Args:
            user_id: 用戶ID
        
        Returns:
            dict: 作業資訊
        """
        try:
            user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
            if not user:
                raise ValueError('使用者不存在')
            
            # 創建匯出作業
            job = Job(
                type='user_data_export',
                status=JobStatus.PENDING,
                payload={'user_id': user_id},
                created_by=user_id
            )
            
            db.session.add(job)
            db.session.commit()
            
            # TODO: 將作業加入 Celery 佇列
            # export_user_data.delay(job.job_id, user_id)
            
            return {
                'message': '資料匯出請求已提交',
                'job_id': job.job_id
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Request data export error: {str(e)}")
            raise RuntimeError(f"資料匯出請求失敗: {str(e)}")

    @staticmethod
    def request_data_deletion(current_user_id, target_user_id):
        """
        請求個人資料刪除 (GDPR)
        
        Args:
            current_user_id: 當前用戶ID
            target_user_id: 目標用戶ID
        
        Returns:
            dict: 作業資訊
        """
        try:
            current_user = User.query.get(current_user_id)
            if not current_user:
                raise ValueError('當前用戶不存在')
            
            target_user = User.query.filter_by(
                user_id=target_user_id, 
                deleted_at=None
            ).first()
            
            if not target_user:
                raise ValueError('使用者不存在')
            
            # 只有本人或管理員可以刪除
            if current_user_id != target_user_id and current_user.role != UserRole.ADMIN:
                raise ValueError('沒有權限刪除此使用者資料')
            
            # 創建刪除作業
            job = Job(
                type='user_data_deletion',
                status=JobStatus.PENDING,
                payload={'user_id': target_user_id},
                created_by=current_user_id
            )
            
            db.session.add(job)
            db.session.commit()
            
            # TODO: 將作業加入 Celery 佇列
            # delete_user_data.delay(job.job_id, target_user_id)
            
            return {
                'message': '資料刪除請求已提交,需要管理員審核',
                'job_id': job.job_id
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Request data deletion error: {str(e)}")
            raise RuntimeError(f"資料刪除請求失敗: {str(e)}")

    @staticmethod
    def list_users(current_user_id, filters=None, pagination=None):
        """
        獲取用戶列表 (仅管理員)
        
        Args:
            current_user_id: 當前用戶ID
            filters: 篩選條件 {'role': str, 'verified': bool, 'region': str}
            pagination: 分頁參數 {'page': int, 'per_page': int}
        
        Returns:
            dict: 用戶列表數據
        """
        try:
            current_user = User.query.get(current_user_id)
            if not current_user or current_user.role != UserRole.ADMIN:
                raise ValueError('只有管理員可以查看用戶列表')
            
            filters = filters or {}
            pagination = pagination or {'page': 1, 'per_page': 20}
            
            # 基本查詢
            query = User.query.filter_by(deleted_at=None)
            
            # 篩選條件
            if 'role' in filters and filters['role']:
                try:
                    role = UserRole(filters['role'])
                    query = query.filter_by(role=role)
                except ValueError:
                    pass  # 忽略無效角色
            
            if 'verified' in filters and filters['verified'] is not None:
                query = query.filter_by(verified=filters['verified'])
            
            if 'region' in filters and filters['region']:
                query = query.filter(User.region.ilike(f"%{filters['region']}%"))
            
            if 'search' in filters and filters['search']:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    db.or_(
                        User.username.ilike(search_term),
                        User.email.ilike(search_term),
                        User.first_name.ilike(search_term),
                        User.last_name.ilike(search_term)
                    )
                )
            
            # 分頁查詢
            page = pagination.get('page', 1)
            per_page = pagination.get('per_page', 20)
            
            pagination_result = query.order_by(
                User.created_at.desc()
            ).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'users': [user.to_dict(include_sensitive=False) for user in pagination_result.items],
                'total': pagination_result.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination_result.pages
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"List users error: {str(e)}")
            raise RuntimeError(f"獲取用戶列表失敗: {str(e)}")

    @staticmethod
    def get_user_statistics(user_id):
        """
        獲取用戶統計資訊 (用戶自己或管理員)
        
        Args:
            user_id: 用戶ID
        
        Returns:
            dict: 統計數據
        """
        try:
            user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
            if not user:
                raise ValueError('使用者不存在')
            
            from sqlalchemy import func
            
            # 動物統計
            from app.models.animal import Animal
            animal_count = Animal.query.filter_by(
                owner_id=user_id, 
                deleted_at=None
            ).count()
            
            # 領養申請統計
            from app.models.application import Application
            application_count = Application.query.filter_by(
                applicant_id=user_id, 
                deleted_at=None
            ).count()
            
            # 上傳文件統計
            from app.models.others import Attachment
            attachment_count = Attachment.query.filter_by(
                uploaded_by_id=user_id, 
                deleted_at=None
            ).count()
            
            total_upload_size = db.session.query(
                func.sum(Attachment.size)
            ).filter_by(
                uploaded_by_id=user_id,
                deleted_at=None
            ).scalar() or 0
            
            return {
                'user_info': {
                    'user_id': user_id,
                    'member_since': user.created_at.isoformat() if user.created_at else None,
                    'last_active': user.updated_at.isoformat() if user.updated_at else None
                },
                'animals': {'total': animal_count},
                'applications': {'total': application_count},
                'uploads': {
                    'total_files': attachment_count,
                    'total_size_bytes': int(total_upload_size),
                    'total_size_mb': round(total_upload_size / (1024 * 1024), 2)
                }
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Get user statistics error: {str(e)}")
            raise RuntimeError(f"獲取用戶統計失敗: {str(e)}")

    @staticmethod
    def _validate_email_unique(email, exclude_user_id=None):
        """驗證 Email 是否唯一"""
        query = User.query.filter_by(email=email, deleted_at=None)
        if exclude_user_id:
            query = query.filter(User.user_id != exclude_user_id)
        
        existing_user = query.first()
        if existing_user:
            raise ValueError('該電子郵件已被使用')