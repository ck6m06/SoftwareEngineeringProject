"""
Applications Blueprint - 領養申請 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from datetime import datetime

from app import db
from app.models.application import Application, ApplicationStatus
from app.models.user import User, UserRole
from app.models.animal import Animal
from app.services.audit_service import audit_service
from app.services.notification_service import notification_service

applications_bp = Blueprint('applications', __name__, description='領養申請 API')


@applications_bp.route('', methods=['GET'])
@jwt_required()
def list_applications():
    """
    取得申請列表
    ---
    支援過濾: status, animal_id, applicant_id
    """
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # 分頁參數
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 基礎查詢
        query = Application.query.filter_by(deleted_at=None)
        
        # 權限過濾邏輯:
        # - 管理員: 可以看到所有申請
        # - 送養人: 只能看到針對自己動物的申請
        # - 申請人: 只能看到自己提交的申請
        
        # 檢查查詢模式
        mode = request.args.get('mode', 'all')  # 'all', 'review', 'my'
        
        if current_user.role == UserRole.ADMIN:
            # 管理員可以看到所有申請,不需要額外過濾
            pass
        else:
            # 非管理員: 查詢自己擁有的動物ID列表
            owned_animal_ids = []
            
            # 1. 查詢個人送養動物 (owner_id = 當前用戶)
            personal_animals = db.session.query(Animal.animal_id).filter_by(
                owner_id=current_user_id,
                deleted_at=None
            ).all()
            owned_animal_ids.extend([aid[0] for aid in personal_animals])
            
            # 2. 如果是收容所成員，查詢所屬收容所的動物 (shelter_id = 用戶所屬收容所)
            if current_user.role == UserRole.SHELTER_MEMBER and current_user.primary_shelter_id:
                shelter_animals = db.session.query(Animal.animal_id).filter_by(
                    shelter_id=current_user.primary_shelter_id,
                    deleted_at=None
                ).all()
                owned_animal_ids.extend([aid[0] for aid in shelter_animals])
            
            # 根據模式決定過濾條件
            if mode == 'review':
                # 審核模式: 只顯示別人對自己動物的申請 (不包括自己提交的申請)
                query = query.filter(Application.animal_id.in_(owned_animal_ids))
            elif mode == 'my':
                # 我的申請模式: 只顯示自己提交的申請
                query = query.filter_by(applicant_id=current_user_id)
            else:
                # 默認模式 (向後兼容): 自己提交的申請 OR 針對自己動物的申請
                query = query.filter(
                    or_(
                        Application.applicant_id == current_user_id,
                        Application.animal_id.in_(owned_animal_ids)
                    )
                )
        
        # 過濾條件
        if 'status' in request.args:
            status_str = request.args.get('status')
            try:
                status_enum = ApplicationStatus(status_str)
                query = query.filter_by(status=status_enum)
            except ValueError:
                abort(400, message=f'無效的狀態值: {status_str}')
        if 'animal_id' in request.args:
            query = query.filter_by(animal_id=request.args.get('animal_id', type=int))
        
        # applicant_id 過濾邏輯優化
        if 'applicant_id' in request.args:
            requested_applicant_id = request.args.get('applicant_id', type=int)
            
            # 非管理員只能查詢自己的申請
            if current_user.role != UserRole.ADMIN:
                if requested_applicant_id != current_user_id:
                    abort(403, message='無權限查看其他用戶的申請')
                query = query.filter_by(applicant_id=current_user_id)
            else:
                # 只有管理員可以查詢指定用戶的申請
                query = query.filter_by(applicant_id=requested_applicant_id)
        
        # 執行分頁查詢
        pagination = query.order_by(Application.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'items': [app.to_dict(include_relations=True) for app in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@applications_bp.route('', methods=['POST'])
@jwt_required()
def create_application():
    """
    建立領養申請
    ---
    支援冪等性: 透過 Idempotency-Key header
    """
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        data = request.get_json()

        # 只有一般會員可以提出領養申請 (管理員與收容所帳號不可申請)
        if not current_user:
            abort(404, message='用戶不存在')
        if current_user.role != UserRole.GENERAL_MEMBER:
            abort(403, message='只有一般會員可提出領養申請')
        
        # 驗證必填欄位
        if not data.get('animal_id'):
            abort(400, message='缺少必填欄位: animal_id')
        
        # 檢查動物是否存在且可領養
        animal = Animal.query.filter_by(
            animal_id=data['animal_id'],
            deleted_at=None
        ).first()
        
        if not animal:
            abort(404, message='動物不存在')
        
        # 檢查動物狀態 - 只有 PUBLISHED 可申請
        from app.models.animal import AnimalStatus
        if animal.status == AnimalStatus.ADOPTED:
            abort(400, message='此動物已被領養')
        if animal.status != AnimalStatus.PUBLISHED:
            abort(400, message='此動物目前無法申請領養')
        
        # 檢查申請人不能是刊登者本人
        if animal.owner_id == current_user_id or animal.created_by == current_user_id:
            abort(400, message='您不能申請自己刊登的動物')
        
        # 檢查是否已有進行中的申請(任何用戶)
        any_pending = Application.query.filter_by(
            animal_id=data['animal_id'],
            deleted_at=None
        ).filter(
            Application.status.in_([ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW])
        ).first()
        
        if any_pending:
            abort(409, message='此動物目前有待審核的申請,請等待審核結果後再提出申請')
        
        # 檢查當前用戶是否已對此動物提交過申請
        existing = Application.query.filter_by(
            animal_id=data['animal_id'],
            applicant_id=current_user_id,
            deleted_at=None
        ).filter(
            Application.status.in_([ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW, ApplicationStatus.APPROVED])
        ).first()
        
        if existing:
            abort(409, message='您已對此動物提交申請')
        
        # 冪等性檢查
        idempotency_key = request.headers.get('Idempotency-Key')
        if idempotency_key:
            existing_app = Application.query.filter_by(
                idempotency_key=idempotency_key,
                applicant_id=current_user_id
            ).first()
            if existing_app:
                return jsonify(existing_app.to_dict()), 200
        
        # 建立申請
        application = Application(
            animal_id=data['animal_id'],
            applicant_id=current_user_id,
            type=data.get('type', 'ADOPTION'),
            status=ApplicationStatus.PENDING,
            submitted_at=datetime.utcnow(),
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
            applicant = User.query.get(current_user_id)
            applicant_name = applicant.username or applicant.email if applicant else '未知用戶'
            animal_name = animal.name or f'動物 #{animal.animal_id}'
            
            notification_service.notify_application_submitted(
                application=application,
                applicant_name=applicant_name,
                animal_name=animal_name
            )
        except Exception as notify_error:
            # 通知失敗不影響主流程
            print(f'通知發送失敗: {notify_error}')
            import traceback
            traceback.print_exc()
        
        return jsonify({
            'message': '申請已提交',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f'Create application error: {str(e)}')
        import traceback
        traceback.print_exc()
        
        # 如果是 werkzeug HTTP 異常,返回正確的狀態碼
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            return jsonify({'error': e.description}), e.code
        
        return jsonify({'error': str(e)}), 500


@applications_bp.route('/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    """
    取得單一申請詳情
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        application = Application.query.filter_by(
            application_id=application_id,
            deleted_at=None
        ).first()
        
        if not application:
            abort(404, message='申請不存在')
        
        # 權限檢查: 申請人本人、動物擁有者、或管理員
        from app.models.animal import Animal
        animal = Animal.query.get(application.animal_id)
        
        is_applicant = application.applicant_id == current_user_id
        is_admin = current_user.role == UserRole.ADMIN
        
        # 檢查是否為動物擁有者 (個人送養或收容所成員)
        is_owner = False
        if animal:
            # 個人送養動物
            if animal.owner_id and animal.owner_id == current_user_id:
                is_owner = True
            # 收容所動物且當前用戶是該收容所成員
            elif animal.shelter_id and current_user.role == UserRole.SHELTER_MEMBER and current_user.primary_shelter_id == animal.shelter_id:
                is_owner = True
        
        if not (is_applicant or is_owner or is_admin):
            abort(403, message='無權限查看此申請')
        
        return jsonify(application.to_dict(include_relations=True)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@applications_bp.route('/<int:application_id>/review', methods=['POST'])
@jwt_required()
def review_application(application_id):
    """
    審核申請 (核准/拒絕)
    ---
    送養人審核權限
    支援樂觀鎖: 透過 version 欄位
    """
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            abort(404, message='用戶不存在')
        
        application = Application.query.filter_by(
            application_id=application_id,
            deleted_at=None
        ).first()
        
        if not application:
            abort(404, message='申請不存在')
        
        # 權限檢查: 只有送養人(擁有者)可以審核申請
        from app.models.animal import Animal
        animal = Animal.query.get(application.animal_id)
        if not animal:
            abort(404, message='動物不存在')
        
        # 檢查是否有權限審核 (個人送養或收容所成員)
        has_permission = False
        
        # 個人送養動物: 只有動物擁有者可以審核
        if animal.owner_id and animal.owner_id == current_user_id:
            has_permission = True
        # 收容所動物: 該收容所的成員可以審核
        elif animal.shelter_id and current_user.role == UserRole.SHELTER_MEMBER and current_user.primary_shelter_id == animal.shelter_id:
            has_permission = True
        
        if not has_permission:
            if current_user.role == UserRole.ADMIN:
                abort(403, message='領養申請應由送養人或收容所成員審核,管理員無權審核')
            else:
                abort(403, message='只有送養人或收容所成員可以審核此申請')
        
        data = request.get_json()
        action = data.get('action')  # 'approve' or 'reject'
        
        if action not in ['approve', 'reject']:
            abort(400, message='action 必須為 approve 或 reject')
        
        # 檢查狀態
        if application.status not in [ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW]:
            abort(400, message='此申請無法審核')
        
        # 樂觀鎖檢查
        if 'version' in data:
            if application.version != data['version']:
                abort(409, message='申請已被其他人修改，請重新載入')
        
        # 保存舊狀態用於審計日誌
        old_status = application.status
        
        # 更新申請狀態
        if action == 'approve':
            application.status = ApplicationStatus.APPROVED
            
            # 批准申請時，將動物狀態改為已領養
            if animal:
                from app.models.animal import AnimalStatus
                animal.status = AnimalStatus.ADOPTED
                animal.updated_at = datetime.utcnow()
        else:
            application.status = ApplicationStatus.REJECTED
        
        application.assignee_id = current_user_id
        application.reviewed_at = datetime.utcnow()
        application.review_notes = data.get('review_notes')
        application.version += 1
        
        db.session.commit()
        
        # 記錄審計日誌 (包裝在 try-catch 中)
        try:
            audit_service.log_application_review(
                application_id,
                current_user_id,
                old_status.value,
                application.status.value
            )
        except Exception as audit_error:
            # 審計日誌失敗不影響主流程,但要記錄錯誤
            print(f'審計日誌記錄失敗: {audit_error}')
            import traceback
            traceback.print_exc()
        
        # 發送審核結果通知給申請人
        try:
            notification_service.notify_application_reviewed(
                application=application,
                reviewer_id=current_user_id,
                status=application.status.value,
                review_notes=application.review_notes
            )
            # Also send an email to the applicant with contact info of the rehome owner/shelter
            try:
                # determine recipient email
                applicant = User.query.get(application.applicant_id)
                recipient_email = applicant.email if applicant else None

                # gather contact info from animal owner or shelter
                contact_info = {}
                if animal:
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

                # Dispatch Celery task (non-blocking)
                if recipient_email:
                    status_str = 'approved' if application.status == ApplicationStatus.APPROVED else 'rejected'
                    # import the task here to avoid circular import during app initialization
                    from app.tasks.email_tasks import send_application_notification_email_task

                    send_application_notification_email_task.delay(
                        recipient_email,
                        animal.name if animal else f'動物 #{application.animal_id}',
                        status_str,
                        application.review_notes,
                        contact_info
                    )
            except Exception as email_err:
                print(f'發送審核結果 Email 失敗: {email_err}')
                import traceback
                traceback.print_exc()
        except Exception as notify_error:
            # 通知失敗不影響主流程
            print(f'通知發送失敗: {notify_error}')
            import traceback
            traceback.print_exc()
        
        return jsonify({
            'message': f'申請已{("核准" if action == "approve" else "拒絕")}',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        print(f"審核申請時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@applications_bp.route('/<int:application_id>/assign', methods=['POST'])
@jwt_required()
def assign_application(application_id):
    """
    指派申請給處理人員
    ---
    需要管理員權限 (此功能已棄用,保留僅供管理員緊急情況使用)
    """
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # 只有管理員可以使用此功能
        if current_user.role != UserRole.ADMIN:
            abort(403, message='無權限指派申請')
        
        application = Application.query.filter_by(
            application_id=application_id,
            deleted_at=None
        ).first()
        
        if not application:
            abort(404, message='申請不存在')
        
        data = request.get_json()
        assignee_id = data.get('assignee_id')
        
        # 驗證受理人
        assignee = User.query.get(assignee_id)
        if not assignee:
            abort(400, message='無效的受理人')
        
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
        except Exception as notify_error:
            # 通知失敗不影響主流程
            print(f'通知發送失敗: {notify_error}')
        
        return jsonify({
            'message': '已指派處理人員',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@applications_bp.route('/<int:application_id>/withdraw', methods=['POST'])
@jwt_required()
def withdraw_application(application_id):
    """
    撤回申請 (申請人自己)
    ---
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        application = Application.query.filter_by(
            application_id=application_id,
            applicant_id=current_user_id,
            deleted_at=None
        ).first()
        
        if not application:
            abort(404, message='申請不存在或無權限')
        
        if application.status not in [ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW]:
            abort(400, message='此申請無法撤回')
        
        application.status = ApplicationStatus.WITHDRAWN
        application.version += 1
        
        db.session.commit()
        
        return jsonify({
            'message': '申請已撤回',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
