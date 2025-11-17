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
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        abort(404, message='用戶不存在')
    
    # 基本查詢：排除已刪除的動物
    query = Animal.query.filter_by(deleted_at=None)
    
    if user.role == UserRole.ADMIN:
        # 管理員可以看到所有動物
        pass
    elif user.role == UserRole.SHELTER_MEMBER:
        # 收容所成員可以看到：
        # 1. 自己擁有的動物 (個人送養)
        # 2. 所屬收容所的動物
        conditions = [Animal.owner_id == current_user_id]
        if user.primary_shelter_id:
            conditions.append(Animal.shelter_id == user.primary_shelter_id)
        query = query.filter(or_(*conditions))
    else:
        # 一般用戶只能看到自己的動物
        query = query.filter_by(owner_id=current_user_id)
    
    # 支援查詢參數：name (partial)、species (CAT|DOG)、min_age、max_age、breed (partial)、adopted (true/false)
    name_q = request.args.get('name')
    species_q = request.args.get('species')
    breed_q = request.args.get('breed')
    min_age = request.args.get('min_age')
    max_age = request.args.get('max_age')
    adopted = request.args.get('adopted')

    # 篩選 - 名稱部分匹配
    if name_q:
        query = query.filter(Animal.name.ilike(f"%{name_q}%"))

    # 品種精確或部分匹配
    if breed_q:
        query = query.filter(Animal.breed.ilike(f"%{breed_q}%"))

    # 物種過濾 (預期 CAT 或 DOG)
    if species_q:
        try:
            # 將輸入上轉大寫以對應枚舉值
            query = query.filter(Animal.species == species_q.upper())
        except Exception:
            pass

    # 年齡範圍: 使用 SQL 計算年齡(月數)，與 /api/animals 保持一致
    try:
        if min_age is not None and min_age != '':
            min_age_val = int(min_age)
            # 使用 TIMESTAMPDIFF(MONTH, dob, CURDATE()) 計算月數
            age_in_months = func.timestampdiff(db.text('MONTH'), Animal.dob, func.curdate())
            query = query.filter(age_in_months >= min_age_val)

        if max_age is not None and max_age != '':
            max_age_val = int(max_age)
            if 'age_in_months' not in locals():
                age_in_months = func.timestampdiff(db.text('MONTH'), Animal.dob, func.curdate())
            query = query.filter(age_in_months <= max_age_val)
    except ValueError:
        # 忽略年齡解析錯誤，繼續返回未篩選的結果
        pass

    # 是否已領養：我們將「申請中/審核中」視為未領養，直到申請完成。
    # 因此已領養的條件為：status == ADOPTED 或 (owner_id 有值 且 無待審核申請)
    # 未領養的條件為：status != ADOPTED 且 (owner_id 為 NULL 或 有待審核申請)
    if adopted is not None:
        adopted_val = str(adopted).lower()
        # 準備 exists 子查詢：檢查是否存在待審核的申請
        from app.models.application import Application, ApplicationStatus

        pending_app_exists = db.session.query(Application).filter(
            Application.animal_id == Animal.animal_id,
            Application.deleted_at == None,
            Application.status.in_([ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW])
        ).exists()

        if adopted_val in ('1', 'true', 'yes'):
            # 已領養：status == ADOPTED OR (owner_id 有值 AND NOT pending_app_exists)
            query = query.filter(or_(
                Animal.status == AnimalStatus.ADOPTED,
                and_(Animal.owner_id.isnot(None), ~pending_app_exists)
            ))
        elif adopted_val in ('0', 'false', 'no'):
            # 未領養：status != ADOPTED AND (owner_id 為 NULL OR pending_app_exists)
            query = query.filter(and_(
                Animal.status != AnimalStatus.ADOPTED,
                or_(Animal.owner_id.is_(None), pending_app_exists)
            ))

    # 執行查詢並序列化
    animals = query.all()
    animals_data = []
    
    for animal in animals:
        animal_dict = animal.to_dict()
        # 添加圖片信息
        if hasattr(animal, 'images') and animal.images:
            animal_dict['images'] = [img.to_dict() for img in animal.images]
        animals_data.append(animal_dict)
    
    return jsonify({
        'animals': animals_data,
        'total': len(animals_data)
    })


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

