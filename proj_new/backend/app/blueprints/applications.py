"""
Applications Blueprint - 申請相關 API (精簡控制器)
"""
from flask import request, jsonify
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.application_service import ApplicationService
from app.decorators.role_decorators import role_required
from app.schemas import ApplicationCreateSchema, ApplicationUpdateSchema

applications_bp = Blueprint('applications', __name__, description='申請管理 API')


@applications_bp.route('', methods=['GET'])
@jwt_required()
def list_applications():
    """
    取得申請列表 (需要登入)
    """
    try:
        # 收集查詢參數
        filters = {
            'page': request.args.get('page', 1, type=int),
            'per_page': min(request.args.get('per_page', 20, type=int), 100),
            'status': request.args.get('status'),
            'mode': request.args.get('mode'),  # 添加mode參數支持
            'applicant_id': request.args.get('applicant_id', type=int),
            'animal_id': request.args.get('animal_id', type=int),
            'shelter_id': request.args.get('shelter_id', type=int),
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date')
        }
        
        # 移除空值參數
        filters = {k: v for k, v in filters.items() if v not in [None, '']}
        
        # 獲取當前用戶身份
        current_user_id = get_jwt_identity()
        
        # 調用服務層處理業務邏輯
        result = ApplicationService.search_applications(filters, current_user_id)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@applications_bp.route('/<application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    """
    取得特定申請詳情
    """
    try:
        application = ApplicationService.get_application_by_id(application_id)
        return jsonify(application), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@applications_bp.route('', methods=['POST'])
@jwt_required()
def create_application():
    """
    創建新申請
    """
    try:
        # 獲取原始請求數據
        raw_data = request.get_json()
        print(f"🔍 收到申請創建請求: {raw_data}")
        
        # 資料驗證
        schema = ApplicationCreateSchema()
        data = schema.load(raw_data)
        print(f"🔍 驗證後的數據: {data}")
        
        # 調用服務層
        user_id = get_jwt_identity()
        application = ApplicationService.create_application(data, user_id)
        
        return jsonify(application), 201
        
    except ValidationError as e:
        print(f"❌ 驗證錯誤: {e.messages}")
        print(f"❌ 原始數據: {request.get_json()}")
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        print(f"❌ 值錯誤: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"❌ 系統錯誤: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@applications_bp.route('/<application_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(application_id):
    """
    更新申請狀態 (審核)
    """
    try:
        # 資料驗證
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        status = data['status']
        notes = data.get('notes')
        
        # 調用服務層
        user_id = get_jwt_identity()
        application = ApplicationService.update_application_status(
            application_id, status, user_id, notes
        )
        
        return jsonify(application), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@applications_bp.route('/<application_id>/review', methods=['POST'])
@jwt_required()
def review_application(application_id):
    """
    審核申請 (核准/拒絕)
    """
    try:
        # 資料驗證
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'error': 'Action is required'}), 400
        
        action = data['action']
        review_notes = data.get('review_notes', '')
        version = data.get('version')
        
        if action not in ['approve', 'reject']:
            return jsonify({'error': 'Invalid action. Must be approve or reject'}), 400
        
        # 轉換為對應狀態
        status = 'APPROVED' if action == 'approve' else 'REJECTED'
        
        # 調用服務層
        user_id = get_jwt_identity()
        application = ApplicationService.update_application_status(
            application_id, status, user_id, review_notes
        )
        
        return jsonify({
            'message': f'申請已{"核准" if action == "approve" else "拒絕"}',
            'application': application
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@applications_bp.route('/<application_id>/assign', methods=['POST'])
@jwt_required()
def assign_application(application_id):
    """
    指派申請給處理人員
    """
    try:
        # 資料驗證
        data = request.get_json()
        if not data or 'assignee_id' not in data:
            return jsonify({'error': 'Assignee ID is required'}), 400
        
        assignee_id = data['assignee_id']
        
        # 調用服務層
        user_id = get_jwt_identity()
        application = ApplicationService.assign_application(
            application_id, assignee_id, user_id
        )
        
        return jsonify({
            'message': '申請已指派',
            'application': application
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@applications_bp.route('/<application_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_application(application_id):
    """
    取消申請
    """
    try:
        user_id = get_jwt_identity()
        ApplicationService.cancel_application(application_id, user_id)
        
        return jsonify({'message': 'Application canceled successfully'}), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500