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
from app.services.application_service import application_service
from app.services.permission_service import permission_service
from app.exceptions import BusinessException

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
    """建立領養申請 - 支援冪等性透過 Idempotency-Key header"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        data = request.get_json()
        
        if not current_user:
            return jsonify({'message': '用戶不存在'}), 404
        
        # 冪等性檢查
        idempotency_key = request.headers.get('Idempotency-Key')
        
        application = application_service.create_application(
            applicant=current_user,
            data=data,
            idempotency_key=idempotency_key
        )
        
        return jsonify({
            'message': '申請已提交',
            'application': application.to_dict()
        }), 201
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@applications_bp.route('/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    """取得單一申請詳情"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        application = Application.query.filter_by(
            application_id=application_id,
            deleted_at=None
        ).first()
        
        if not application:
            return jsonify({'message': '申請不存在'}), 404
        
        # 權限檢查
        if not permission_service.can_view_application(current_user, application):
            return jsonify({'message': '無權限查看此申請'}), 403
        
        return jsonify(application.to_dict(include_relations=True)), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@applications_bp.route('/<int:application_id>/review', methods=['POST'])
@jwt_required()
def review_application(application_id):
    """審核申請（核准/拒絕）- 送養人審核權限，支援樂觀鎖透過 version 欄位"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        if not current_user:
            return jsonify({'message': '用戶不存在'}), 404
        
        data = request.get_json()
        action = data.get('action')
        review_notes = data.get('review_notes')
        version = data.get('version')
        
        application = application_service.review_application(
            application_id=application_id,
            reviewer=current_user,
            action=action,
            review_notes=review_notes,
            version=version
        )
        
        return jsonify({
            'message': f'申請已{("核准" if action == "approve" else "拒絕")}',
            'application': application.to_dict()
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@applications_bp.route('/<int:application_id>/assign', methods=['POST'])
@jwt_required()
def assign_application(application_id):
    """指派申請給處理人員 - 需要管理員權限"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        data = request.get_json()
        assignee_id = data.get('assignee_id')
        
        if not assignee_id:
            return jsonify({'message': '缺少受理人 ID'}), 400
        
        application = application_service.assign_application(
            application_id=application_id,
            admin=current_user,
            assignee_id=assignee_id
        )
        
        return jsonify({
            'message': '已指派處理人員',
            'application': application.to_dict()
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@applications_bp.route('/<int:application_id>/withdraw', methods=['POST'])
@jwt_required()
def withdraw_application(application_id):
    """撤回申請（申請人自己）"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        application = application_service.withdraw_application(
            application_id=application_id,
            applicant=current_user
        )
        
        return jsonify({
            'message': '申請已撤回',
            'application': application.to_dict()
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500
