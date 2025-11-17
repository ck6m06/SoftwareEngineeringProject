"""
Application Service - 申請相關業務邏輯
"""
from flask import current_app
from sqlalchemy import or_, and_, exists
from app import db
from app.models.animal import Animal, AnimalStatus
from app.models.application import Application, ApplicationStatus
from app.models.user import User, UserRole
from app.models.shelter import Shelter
from app.services.audit_service import AuditService
from datetime import datetime


class ApplicationService:
    """申請業務邏輯服務"""

    @staticmethod
    def search_applications(filters, current_user_id):
        """
        搜尋申請列表
        
        Args:
            filters: dict 包含篩選條件
            current_user_id: 當前用戶ID
        
        Returns:
            dict: 分頁結果
        """
        try:
            # 建立基礎查詢
            query = Application.query.filter_by(deleted_at=None)
            
            # 權限過濾邏輯
            query = ApplicationService._apply_permission_filter(query, current_user_id, filters.get('mode'))
            
            # 應用篩選條件
            query = ApplicationService._apply_filters(query, filters)
            
            # 分頁
            page = filters.get('page', 1)
            per_page = min(filters.get('per_page', 20), 100)
            
            pagination = query.order_by(Application.created_at.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'items': [app.to_dict(include_relations=True) for app in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }
            
        except Exception as e:
            current_app.logger.error(f"Application search error: {str(e)}")
            raise

    @staticmethod
    def _apply_permission_filter(query, current_user_id, mode=None):
        """應用權限過濾"""
        user = User.query.get(current_user_id)
        
        if not user:
            raise ValueError('用戶不存在')
        
        # 如果是 mode=my，只返回用戶自己提交的申請
        if mode == 'my':
            return query.filter(Application.applicant_id == current_user_id)
        
        if user.role == UserRole.ADMIN:
            # 管理員可以看到所有申請
            return query
        elif user.role == UserRole.SHELTER_MEMBER and user.primary_shelter_id:
            # 收容所成員可以看到：
            # 1. 自己提交的申請
            # 2. 針對所屬收容所動物的申請
            owned_animals_condition = exists().where(
                Application.animal_id == Animal.animal_id,
                Animal.shelter_id == user.primary_shelter_id
            )
            
            query = query.filter(
                or_(
                    Application.applicant_id == current_user_id,
                    owned_animals_condition
                )
            )
        else:
            # 一般用戶只能看到：
            # 1. 自己提交的申請
            # 2. 針對自己動物的申請
            owned_animals_condition = exists().where(
                Application.animal_id == Animal.animal_id,
                Animal.owner_id == current_user_id
            )
            
            query = query.filter(
                or_(
                    Application.applicant_id == current_user_id,
                    owned_animals_condition
                )
            )
        
        return query

    @staticmethod
    def _apply_filters(query, filters):
        """應用各種篩選條件"""
        # 狀態篩選
        if filters.get('status'):
            try:
                query = query.filter_by(status=ApplicationStatus(filters['status']))
            except ValueError:
                raise ValueError('無效的狀態值')
        
        # 申請者篩選
        if filters.get('applicant_id'):
            query = query.filter_by(applicant_id=filters['applicant_id'])
        
        # 動物篩選
        if filters.get('animal_id'):
            query = query.filter_by(animal_id=filters['animal_id'])
        
        # 收容所篩選
        if filters.get('shelter_id'):
            query = query.join(Animal).filter(Animal.shelter_id == filters['shelter_id'])
        
        # 日期範圍篩選
        if filters.get('start_date'):
            try:
                start_date = datetime.fromisoformat(filters['start_date'])
                query = query.filter(Application.created_at >= start_date)
            except ValueError:
                raise ValueError('無效的開始日期格式')
        
        if filters.get('end_date'):
            try:
                end_date = datetime.fromisoformat(filters['end_date'])
                query = query.filter(Application.created_at <= end_date)
            except ValueError:
                raise ValueError('無效的結束日期格式')
        
        return query

    @staticmethod
    def get_application_by_id(application_id):
        """
        根據ID取得申請
        
        Args:
            application_id: 申請ID
        
        Returns:
            dict: 申請資料
        
        Raises:
            ValueError: 申請不存在
        """
        application = Application.query.filter_by(
            application_id=application_id,
            deleted_at=None
        ).first()
        
        if not application:
            raise ValueError('申請不存在')
        
        return application.to_dict(include_relations=True)

    @staticmethod
    def create_application(data, user_id):
        """
        創建新申請
        
        Args:
            data: 申請資料
            user_id: 申請者ID
        
        Returns:
            dict: 創建的申請資料
        """
        try:
            # 資料驗證
            ApplicationService._validate_application_data(data)
            
            # 檢查動物是否可申請
            animal = ApplicationService._check_animal_available(data['animal_id'])
            
            # 檢查是否已有待處理申請
            ApplicationService._check_duplicate_application(data['animal_id'], user_id)
            
            # 創建申請記錄
            application = Application(
                animal_id=data['animal_id'],
                applicant_id=user_id,
                type=data.get('type', 'ADOPTION'),
                status=ApplicationStatus.PENDING,
                attachments=data.get('attachments'),
                # 申請人詳細資料
                contact_phone=data.get('contact_phone'),
                contact_address=data.get('contact_address'),
                occupation=data.get('occupation'),
                housing_type=data.get('housing_type'),
                has_experience=data.get('has_experience', False),
                reason=data.get('reason'),
                notes=data.get('notes')
            )
            
            db.session.add(application)
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='application.create',
                actor_id=user_id,
                target_type='application',
                target_id=application.application_id,
                after_state=application.to_dict()
            )
            
            return application.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Create application error: {str(e)}")
            raise

    @staticmethod
    def update_application_status(application_id, status, user_id, notes=None):
        """
        更新申請狀態
        
        Args:
            application_id: 申請ID
            status: 新狀態
            user_id: 操作者ID
            notes: 備註
        
        Returns:
            dict: 更新後的申請資料
        """
        try:
            application = Application.query.filter_by(
                application_id=application_id,
                deleted_at=None
            ).first()
            
            if not application:
                raise ValueError('申請不存在')
            
            # 權限檢查
            ApplicationService._check_approval_permission(application, user_id)
            
            # 狀態驗證
            try:
                new_status = ApplicationStatus(status)
            except ValueError:
                raise ValueError('無效的狀態值')
            
            # 記錄修改前狀態
            before_state = application.to_dict()
            
            # 更新狀態
            application.status = new_status
            if notes:
                application.admin_notes = notes
            application.updated_at = datetime.utcnow()
            
            # 如果是批准申請，需要更新動物狀態
            if new_status == ApplicationStatus.APPROVED:
                animal = Animal.query.get(application.animal_id)
                if animal:
                    animal.status = AnimalStatus.ADOPTED
                    animal.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='application.status_update',
                actor_id=user_id,
                target_type='application',
                target_id=application.application_id,
                before_state=before_state,
                after_state=application.to_dict()
            )
            
            return application.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update application status error: {str(e)}")
            raise

    @staticmethod
    def cancel_application(application_id, user_id):
        """
        取消申請
        
        Args:
            application_id: 申請ID
            user_id: 操作者ID
        """
        try:
            application = Application.query.filter_by(
                application_id=application_id,
                deleted_at=None
            ).first()
            
            if not application:
                raise ValueError('申請不存在')
            
            # 權限檢查 - 只有申請者可以取消
            if application.applicant_id != user_id:
                raise PermissionError('只有申請者可以取消申請')
            
            # 狀態檢查 - 只有待處理的申請可以取消
            if application.status != ApplicationStatus.PENDING:
                raise ValueError('只能取消待處理的申請')
            
            # 記錄修改前狀態
            before_state = application.to_dict()
            
            # 更新狀態
            application.status = ApplicationStatus.CANCELED
            application.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='application.cancel',
                actor_id=user_id,
                target_type='application',
                target_id=application.application_id,
                before_state=before_state,
                after_state=application.to_dict()
            )
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Cancel application error: {str(e)}")
            raise

    @staticmethod
    def assign_application(application_id, assignee_id, user_id):
        """
        指派申請給處理人員
        
        Args:
            application_id: 申請ID
            assignee_id: 被指派人員ID
            user_id: 操作者ID
        
        Returns:
            dict: 更新後的申請資料
        """
        try:
            application = Application.query.filter_by(
                application_id=application_id,
                deleted_at=None
            ).first()
            
            if not application:
                raise ValueError('申請不存在')
            
            # 權限檢查 - 只有管理員可以指派
            user = User.query.get(user_id)
            if not user or user.role != UserRole.ADMIN:
                raise PermissionError('只有管理員可以指派申請')
            
            # 檢查被指派用戶是否存在
            assignee = User.query.get(assignee_id)
            if not assignee:
                raise ValueError('被指派人員不存在')
            
            # 記錄修改前狀態
            before_state = application.to_dict()
            
            # 更新申請
            application.assigned_to_id = assignee_id
            if application.status == ApplicationStatus.PENDING:
                application.status = ApplicationStatus.UNDER_REVIEW
            application.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='application.assign',
                actor_id=user_id,
                target_type='application',
                target_id=application.application_id,
                before_state=before_state,
                after_state=application.to_dict()
            )
            
            return application.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Assign application error: {str(e)}")
            raise

    @staticmethod
    def _validate_application_data(data):
        """驗證申請資料"""
        required_fields = ['animal_id']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f'缺少必填欄位: {field}')

    @staticmethod
    def _check_animal_available(animal_id):
        """檢查動物是否可申請"""
        animal = Animal.query.filter_by(
            animal_id=animal_id,
            deleted_at=None
        ).first()
        
        if not animal:
            raise ValueError('動物不存在')
        
        if animal.status != AnimalStatus.PUBLISHED:
            raise ValueError('此動物目前不開放申請')
        
        return animal

    @staticmethod
    def _check_duplicate_application(animal_id, user_id):
        """檢查重複申請"""
        existing = Application.query.filter_by(
            animal_id=animal_id,
            applicant_id=user_id,
            status=ApplicationStatus.PENDING,
            deleted_at=None
        ).first()
        
        if existing:
            raise ValueError('您已對此動物提交申請，請勿重複申請')

    @staticmethod
    def _check_approval_permission(application, user_id):
        """檢查審核權限"""
        user = User.query.get(user_id)
        
        if not user:
            raise ValueError('用戶不存在')
        
        # 管理員有所有權限
        if user.role == UserRole.ADMIN:
            return True
        
        # 動物擁有者有權限
        animal = Animal.query.get(application.animal_id)
        if animal and animal.owner_id == user_id:
            return True
        
        # 收容所成員對所屬收容所動物有權限
        if (user.role == UserRole.SHELTER_MEMBER and 
            user.primary_shelter_id and 
            animal and animal.shelter_id == user.primary_shelter_id):
            return True
        
        raise PermissionError('無權限審核此申請')