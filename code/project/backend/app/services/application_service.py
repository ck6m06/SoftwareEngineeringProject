"""
Application Service - 申請業務邏輯服務
集中管理所有申請相關的業務邏輯
"""
from datetime import datetime
from app.utils.datetime_helper import get_naive_taipei_now
from typing import Dict, Any, Optional, List
from sqlalchemy import or_
from app import db
from app.models.application import Application, ApplicationStatus, ApplicationType
from app.models.user import User, UserRole
from app.models.animal import Animal, AnimalStatus
from app.exceptions import (
    PermissionDeniedError, NotFoundError, ValidationError, ConflictError
)
from app.services.permission_service import permission_service
from app.services.audit_service import audit_service
from app.services.notification_service import notification_service


class ApplicationService:
    """申請業務邏輯服務類"""
    
    @staticmethod
    def list_applications(current_user: User, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        查詢申請列表
        
        業務邏輯：
        1. 管理員可以看到所有申請
        2. 送養人可以看到針對自己動物的申請
        3. 申請人可以看到自己提交的申請
        4. 支援多種查詢模式 (all/review/my)
        
        Args:
            current_user: 當前用戶
            filters: 過濾條件
                - mode: 查詢模式 ('all', 'review', 'my')
                - status: 申請狀態
                - animal_id: 動物 ID
                - applicant_id: 申請人 ID
                - page: 頁碼
                - per_page: 每頁筆數
                
        Returns:
            Dict: 包含申請列表和分頁資訊
            
        Raises:
            ValidationError: 過濾條件無效
            PermissionDeniedError: 無權限查看指定申請
        """
        # 分頁參數
        page = filters.get('page', 1)
        per_page = filters.get('per_page', 20)
        mode = filters.get('mode', 'all')
        
        # 基礎查詢
        query = Application.query.filter_by(deleted_at=None)
        
        # 權限過濾邏輯
        if current_user.role == UserRole.ADMIN:
            # 管理員可以看到所有申請
            pass
        else:
            # 非管理員: 查詢自己擁有的動物ID列表
            owned_animal_ids = []
            
            # 1. 查詢個人送養動物
            personal_animals = db.session.query(Animal.animal_id).filter_by(
                owner_id=current_user.user_id,
                deleted_at=None
            ).all()
            owned_animal_ids.extend([aid[0] for aid in personal_animals])
            
            # 2. 如果是收容所成員，查詢所屬收容所的動物
            if current_user.role == UserRole.SHELTER_MEMBER and current_user.primary_shelter_id:
                shelter_animals = db.session.query(Animal.animal_id).filter_by(
                    shelter_id=current_user.primary_shelter_id,
                    deleted_at=None
                ).all()
                owned_animal_ids.extend([aid[0] for aid in shelter_animals])
            
            # 根據模式決定過濾條件
            if mode == 'review':
                # 審核模式: 只顯示別人對自己動物的申請
                query = query.filter(Application.animal_id.in_(owned_animal_ids))
            elif mode == 'my':
                # 我的申請模式: 只顯示自己提交的申請
                query = query.filter_by(applicant_id=current_user.user_id)
            else:
                # 默認模式: 自己提交的申請 OR 針對自己動物的申請
                query = query.filter(
                    or_(
                        Application.applicant_id == current_user.user_id,
                        Application.animal_id.in_(owned_animal_ids)
                    )
                )
        
        # 狀態過濾
        if filters.get('status'):
            try:
                status_enum = ApplicationStatus(filters['status'])
                query = query.filter_by(status=status_enum)
            except ValueError:
                raise ValidationError(f'無效的狀態值: {filters["status"]}')
        
        # 動物 ID 過濾
        if filters.get('animal_id'):
            query = query.filter_by(animal_id=filters['animal_id'])
        
        # 申請人 ID 過濾
        if filters.get('applicant_id'):
            requested_applicant_id = filters['applicant_id']
            
            # 非管理員只能查詢自己的申請
            if current_user.role != UserRole.ADMIN:
                if requested_applicant_id != current_user.user_id:
                    raise PermissionDeniedError('無權限查看其他用戶的申請')
                query = query.filter_by(applicant_id=current_user.user_id)
            else:
                # 只有管理員可以查詢指定用戶的申請
                query = query.filter_by(applicant_id=requested_applicant_id)
        
        # 執行分頁查詢
        pagination = query.order_by(Application.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'items': [app.to_dict(include_relations=True) for app in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def create_application(applicant: User, data: Dict[str, Any], 
                          idempotency_key: Optional[str] = None) -> Application:
        """
        創建領養申請
        
        業務邏輯：
        1. 只有一般會員可以提出領養申請
        2. 檢查動物狀態（只能申請已發布的動物）
        3. 申請人不能是刊登者本人
        4. 檢查是否已有進行中的申請
        5. 支援冪等性
        
        Args:
            applicant: 申請人
            data: 申請資料
            idempotency_key: 冪等性鍵值
            
        Returns:
            Application: 創建的申請物件
            
        Raises:
            PermissionDeniedError: 只有一般會員可提出申請
            ValidationError: 缺少必填欄位或動物狀態不符
            NotFoundError: 動物不存在
            ConflictError: 重複申請
        """
        # 權限檢查：只有一般會員可以提出領養申請
        if applicant.role != UserRole.GENERAL_MEMBER:
            raise PermissionDeniedError('只有一般會員可提出領養申請')
        
        # 驗證必填欄位
        if not data.get('animal_id'):
            raise ValidationError('缺少必填欄位: animal_id')
        
        # 檢查動物是否存在且可領養
        animal = Animal.query.filter_by(
            animal_id=data['animal_id'],
            deleted_at=None
        ).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        # 檢查動物狀態
        if animal.status == AnimalStatus.ADOPTED:
            raise ValidationError('此動物已被領養')
        if animal.status != AnimalStatus.PUBLISHED:
            raise ValidationError('此動物目前無法申請領養')
        
        # 檢查申請人不能是刊登者本人
        if animal.owner_id == applicant.user_id or animal.created_by == applicant.user_id:
            raise ValidationError('您不能申請自己刊登的動物')
        
        # 冪等性檢查（優先檢查，避免重複檢查的409錯誤）
        if idempotency_key:
            existing_app = Application.query.filter_by(
                idempotency_key=idempotency_key,
                applicant_id=applicant.user_id
            ).first()
            if existing_app:
                return existing_app
        
        # 檢查當前用戶是否已對此動物提交過申請
        existing = Application.query.filter_by(
            animal_id=data['animal_id'],
            applicant_id=applicant.user_id,
            deleted_at=None
        ).filter(
            Application.status.in_([
                ApplicationStatus.PENDING, 
                ApplicationStatus.UNDER_REVIEW, 
                ApplicationStatus.APPROVED
            ])
        ).first()
        
        if existing:
            raise ConflictError('您已對此動物提交申請')
        
        # 檢查是否已有進行中的申請（任何用戶）
        any_pending = Application.query.filter_by(
            animal_id=data['animal_id'],
            deleted_at=None
        ).filter(
            Application.status.in_([ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW])
        ).first()
        
        if any_pending:
            raise ConflictError('此動物目前有待審核的申請,請等待審核結果後再提出申請')
        
        # 冪等性檢查
        if idempotency_key:
            existing_app = Application.query.filter_by(
                idempotency_key=idempotency_key,
                applicant_id=applicant.user_id
            ).first()
            if existing_app:
                return existing_app
        
        # 為SQLite手動分配application_id（解決BIGINT autoincrement問題）
        max_id_result = db.session.execute(
            db.text("SELECT MAX(application_id) FROM applications")
        ).scalar()
        next_application_id = (max_id_result or 0) + 1
        
        # 創建申請
        application = Application(
            application_id=next_application_id,
            animal_id=data['animal_id'],
            applicant_id=applicant.user_id,
            type=data.get('type', 'ADOPTION'),
            status=ApplicationStatus.PENDING,
            submitted_at=get_naive_taipei_now(),
            attachments=data.get('attachments'),
            idempotency_key=idempotency_key,
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
        
        # 發送通知給動物擁有者
        try:
            applicant_name = applicant.username or applicant.email
            animal_name = animal.name or f'動物 #{animal.animal_id}'
            
            notification_service.notify_application_submitted(
                application=application,
                applicant_name=applicant_name,
                animal_name=animal_name
            )
        except Exception as e:
            # 通知失敗不影響主流程
            print(f'通知發送失敗: {e}')
        
        return application
    
    @staticmethod
    def review_application(application_id: int, reviewer: User, action: str, 
                          review_notes: Optional[str] = None, 
                          expected_version: Optional[int] = None) -> Application:
        """
        審核申請（批准/拒絕）
        
        業務邏輯：
        1. 只有送養人可以審核申請（管理員不能審核）
        2. 檢查申請狀態（只能審核待審核或審核中的申請）
        3. 樂觀鎖檢查（避免並發衝突）
        4. 批准申請時將動物狀態改為已領養
        5. 記錄審計日誌
        6. 發送通知給申請人
        
        Args:
            application_id: 申請 ID
            reviewer: 審核者
            action: 'approve' 或 'reject'
            review_notes: 審核備註
            expected_version: 預期版本號（樂觀鎖）
            
        Returns:
            Application: 更新後的申請物件
            
        Raises:
            NotFoundError: 申請不存在
            PermissionDeniedError: 無權限審核
            ValidationError: action 無效或申請狀態不符
            ConflictError: 版本衝突（樂觀鎖）
        """
        application = Application.query.filter_by(
            application_id=application_id,
            deleted_at=None
        ).first()
        
        if not application:
            raise NotFoundError('申請不存在')
        
        # 權限檢查：只有送養人可以審核
        if not permission_service.can_review_application(reviewer, application):
            if reviewer.role == UserRole.ADMIN:
                raise PermissionDeniedError('領養申請應由送養人或收容所成員審核,管理員無權審核')
            else:
                raise PermissionDeniedError('只有送養人或收容所成員可以審核此申請')
        
        # 檢查 action
        if action not in ['approve', 'reject']:
            raise ValidationError('action 必須為 approve 或 reject')
        
        # 檢查狀態
        if application.status not in [ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW]:
            raise ValidationError('此申請無法審核')
        
        # 樂觀鎖檢查
        if expected_version is not None:
            if application.version != expected_version:
                raise ConflictError('申請已被其他人修改，請重新載入')
        
        # 保存舊狀態用於審計日誌
        old_status = application.status
        
        # 更新申請狀態
        if action == 'approve':
            application.status = ApplicationStatus.APPROVED
            
            # 批准申請時，將動物狀態改為已領養
            animal = application.animal
            if animal:
                animal.status = AnimalStatus.ADOPTED
                animal.updated_at = get_naive_taipei_now()
        else:
            application.status = ApplicationStatus.REJECTED
        
        application.assignee_id = reviewer.user_id
        application.reviewed_at = get_naive_taipei_now()
        application.review_notes = review_notes
        application.version += 1
        
        db.session.commit()
        
        # 記錄審計日誌
        try:
            audit_service.log_application_review(
                application_id,
                reviewer.user_id,
                old_status.value,
                application.status.value
            )
        except Exception as e:
            print(f'審計日誌記錄失敗: {e}')
        
        # 發送審核結果通知
        try:
            notification_service.notify_application_reviewed(
                application=application,
                reviewer_id=reviewer.user_id,
                status=application.status.value,
                review_notes=application.review_notes
            )
            
            # 發送 Email 通知（透過 Celery 任務）
            animal = application.animal
            applicant = application.applicant
            if animal and applicant and applicant.email:
                status_str = 'approved' if application.status == ApplicationStatus.APPROVED else 'rejected'
                
                # 收集聯絡資訊
                contact_info = {}
                if animal.owner_id:
                    owner = User.query.get(animal.owner_id)
                    if owner:
                        contact_info = {
                            'type': 'owner',
                            'name': owner.username or f"{owner.first_name or ''} {owner.last_name or ''}".strip(),
                            'email': owner.email,
                            'phone': owner.phone_number
                        }
                elif animal.shelter_id:
                    from app.models.shelter import Shelter
                    shelter = Shelter.query.get(animal.shelter_id)
                    if shelter:
                        contact_info = {
                            'type': 'shelter',
                            'name': shelter.name,
                            'email': shelter.contact_email,
                            'phone': shelter.contact_phone
                        }
                
                # 延遲導入避免循環依賴
                from app.tasks.email_tasks import send_application_notification_email_task
                send_application_notification_email_task.delay(
                    applicant.email,
                    animal.name if animal else f'動物 #{application.animal_id}',
                    status_str,
                    application.review_notes,
                    contact_info
                )
        except Exception as e:
            print(f'通知發送失敗: {e}')
        
        return application
    
    @staticmethod
    def withdraw_application(application_id: int, applicant: User) -> Application:
        """
        撤回申請（申請人自己）
        
        Args:
            application_id: 申請 ID
            applicant: 申請人
            
        Returns:
            Application: 更新後的申請物件
            
        Raises:
            NotFoundError: 申請不存在或無權限
            ValidationError: 申請狀態不符
        """
        application = Application.query.filter_by(
            application_id=application_id,
            applicant_id=applicant.user_id,
            deleted_at=None
        ).first()
        
        if not application:
            raise NotFoundError('申請不存在或無權限')
        
        if application.status not in [ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW]:
            raise ValidationError('此申請無法撤回')
        
        application.status = ApplicationStatus.WITHDRAWN
        application.version += 1
        
        db.session.commit()
        
        return application
    
    @staticmethod
    def assign_application(application_id: int, admin: User, assignee_id: int) -> Application:
        """
        指派申請給處理人員
        
        業務邏輯：
        1. 只有管理員可以使用此功能（緊急情況使用）
        2. 驗證受理人是否存在
        3. 更新申請狀態為審核中
        
        Args:
            application_id: 申請 ID
            admin: 管理員
            assignee_id: 受理人 ID
            
        Returns:
            Application: 更新後的申請物件
            
        Raises:
            NotFoundError: 申請或受理人不存在
            PermissionDeniedError: 無權限指派
            ValidationError: 無效的受理人
        """
        if admin.role != UserRole.ADMIN:
            raise PermissionDeniedError('無權限指派申請')
        
        application = Application.query.filter_by(
            application_id=application_id,
            deleted_at=None
        ).first()
        
        if not application:
            raise NotFoundError('申請不存在')
        
        # 驗證受理人
        assignee = User.query.get(assignee_id)
        if not assignee:
            raise ValidationError('無效的受理人')
        
        application.assignee_id = assignee_id
        application.status = ApplicationStatus.UNDER_REVIEW
        application.version += 1
        
        db.session.commit()
        
        # 發送進入審核通知給申請人
        try:
            assignee_name = assignee.username or assignee.email
            notification_service.notify_application_under_review(
                application=application,
                assignee_id=assignee_id,
                assignee_name=assignee_name
            )
        except Exception as e:
            print(f'通知發送失敗: {e}')
        
        return application


# 創建全局實例
application_service = ApplicationService()
