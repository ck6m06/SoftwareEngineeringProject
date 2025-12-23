"""
Medical Records Blueprint - 醫療紀錄 API
"""
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from app import db
from app.models.medical_record import MedicalRecord, RecordType
from app.models.animal import Animal, AnimalStatus
from sqlalchemy import or_, and_, func
from sqlalchemy.sql import exists
from app.models.user import User, UserRole
from sqlalchemy import or_
from app.services.medical_record_service import medical_record_service
from app.exceptions import ValidationError, NotFoundError, PermissionDeniedError

medical_records_bp = Blueprint('medical_records', __name__, description='醫療紀錄 API')


@medical_records_bp.route('/animals', methods=['GET'])
@jwt_required()
def list_animals_for_medical_records():
    """
    獲取當前用戶有權限管理醫療紀錄的動物列表
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = db.session.get(User, current_user_id)
        
        if not user:
            abort(404, message='用戶不存在')
        
        # 收集過濾參數
        filters = {
            'name': request.args.get('name'),
            'species': request.args.get('species'),
            'breed': request.args.get('breed'),
            'min_age': request.args.get('min_age'),
            'max_age': request.args.get('max_age'),
            'adopted': request.args.get('adopted')
        }
        
        # 呼叫 Service 層
        result = medical_record_service.list_animals_for_medical_records(user, filters)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@medical_records_bp.route('/animals/<int:animal_id>/medical-records', methods=['POST'])
@jwt_required()
def create_medical_record(animal_id):
    """
    為動物創建醫療紀錄
    需要認證 (動物擁有者、收容所成員或管理員)
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    try:
        # 驗證 record_type
        record_type = None
        if 'record_type' in data:
            try:
                record_type = RecordType(data['record_type'])
            except ValueError:
                abort(400, message=f'無效的紀錄類型: {data["record_type"]}')
        
        # 驗證日期格式
        record_date = None
        if 'date' in data:
            record_date = medical_record_service.parse_date(data['date'])
        
        # 使用 service 創建醫療記錄
        medical_record = medical_record_service.create_medical_record(
            animal_id=animal_id,
            current_user_id=current_user_id,
            record_type=record_type,
            date=record_date,
            provider=data.get('provider'),
            details=data.get('details'),
            attachments_data=data.get('attachments', [])
        )
        
        return jsonify({
            'message': '醫療紀錄創建成功',
            'medical_record': medical_record.to_dict()
        }), 201
        
    except NotFoundError as e:
        abort(404, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except ValidationError as e:
        abort(400, message=str(e))


@medical_records_bp.route('/animals/<int:animal_id>/medical-records', methods=['GET'])
def list_medical_records(animal_id):
    """
    取得動物的醫療紀錄列表 (公開端點)
    """
    try:
        records = medical_record_service.list_animal_medical_records(animal_id)
        
        return jsonify({
            'total': len(records),
            'medical_records': [record.to_dict() for record in records]
        }), 200
    except NotFoundError as e:
        abort(404, message=str(e))


@medical_records_bp.route('/<int:record_id>', methods=['PATCH'])
@jwt_required()
def update_medical_record(record_id):
    """
    更新醫療紀錄
    僅創建者、動物擁有者或管理員可更新
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    try:
        # 解析日期格式（如果有）
        parsed_date = None
        if 'date' in data:
            parsed_date = medical_record_service.parse_date(data['date'])
        
        # 解析 record_type（如果有）
        record_type = None
        if 'record_type' in data:
            try:
                record_type = RecordType(data['record_type'])
            except ValueError:
                abort(400, message=f'無效的紀錄類型: {data["record_type"]}')
        
        # 使用 service 更新
        record = medical_record_service.update_medical_record(
            record_id=record_id,
            current_user_id=current_user_id,
            record_type=record_type,
            date=parsed_date,
            provider=data.get('provider'),
            details=data.get('details'),
            attachments_data=data.get('attachments')
        )
        
        return jsonify({
            'message': '醫療紀錄更新成功',
            'medical_record': record.to_dict()
        }), 200
        
    except NotFoundError as e:
        abort(404, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except ValidationError as e:
        abort(400, message=str(e))


@medical_records_bp.route('/<int:record_id>/verify', methods=['POST'])
@jwt_required()
def verify_medical_record(record_id):
    """
    驗證醫療紀錄 (僅管理員)
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    verified = data.get('verified', True)
    
    try:
        record = medical_record_service.verify_medical_record(
            record_id=record_id,
            current_user_id=current_user_id,
            verified=verified
        )
        
        return jsonify({
            'message': f'醫療紀錄已{"驗證" if verified else "取消驗證"}',
            'medical_record': record.to_dict()
        }), 200
        
    except NotFoundError as e:
        abort(404, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))

