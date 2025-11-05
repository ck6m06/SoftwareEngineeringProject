"""
Medical Records Blueprint - 醫療紀錄 API
"""
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from app import db
from app.models.medical_record import MedicalRecord, RecordType
from app.models.animal import Animal
from app.models.user import User, UserRole
from sqlalchemy import or_

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
    
    # 檢查動物是否存在
    animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
    if not animal:
        abort(404, message='動物不存在')
    
    # 檢查權限
    user = User.query.get(current_user_id)
    if not user:
        abort(404, message='用戶不存在')
    
    # 權限檢查:
    # 1. 管理員可以為所有動物創建醫療紀錄
    # 2. 動物擁有者(owner_id)可以為自己的動物創建醫療紀錄
    # 3. 收容所成員可以為所屬收容所的動物創建醫療紀錄
    has_permission = False
    
    if user.role == UserRole.ADMIN:
        has_permission = True
    elif animal.owner_id and animal.owner_id == current_user_id:
        # 個人送養動物：動物擁有者可以創建醫療紀錄
        has_permission = True
    elif animal.shelter_id and user.role == UserRole.SHELTER_MEMBER and user.primary_shelter_id == animal.shelter_id:
        # 收容所動物：該收容所成員可以創建醫療紀錄
        has_permission = True
    
    if not has_permission:
        abort(403, message='無權限為此動物創建醫療紀錄')
    
    data = request.get_json()
    
    # 驗證 record_type
    record_type = None
    if 'record_type' in data:
        try:
            record_type = RecordType(data['record_type'])
        except ValueError:
            abort(400, message=f'無效的紀錄類型: {data["record_type"]}')
    
    # 驗證日期格式 - 支援多種格式
    record_date = None
    if 'date' in data:
        try:
            date_str = data['date'].strip()
            # 嘗試多種日期格式
            date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y']
            for fmt in date_formats:
                try:
                    record_date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
            
            if record_date is None:
                abort(400, message='日期格式錯誤,支援格式: YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY, DD-MM-YYYY')
        except Exception:
            abort(400, message='日期格式錯誤,支援格式: YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY, DD-MM-YYYY')
    
    # 創建醫療紀錄
    medical_record = MedicalRecord(
        animal_id=animal_id,
        record_type=record_type,
        date=record_date,
        provider=data.get('provider'),
        details=data.get('details'),
        attachments=data.get('attachments', []),
        verified=False,
        created_by=current_user_id
    )
    
    db.session.add(medical_record)
    db.session.flush()  # 獲取醫療記錄 ID，但不提交事務
    
    # 處理附件：如果有附件，創建 Attachment 記錄
    attachments_data = data.get('attachments', [])
    if attachments_data and isinstance(attachments_data, list):
        from app.models.others import Attachment
        
        for attachment_info in attachments_data:
            if isinstance(attachment_info, dict) and 'storage_key' in attachment_info:
                # 創建 Attachment 記錄
                attachment = Attachment(
                    owner_type='medical_record',
                    owner_id=medical_record.medical_record_id,
                    filename=attachment_info.get('filename', '未知檔案'),
                    storage_key=attachment_info.get('storage_key'),
                    url=attachment_info.get('url'),
                    mime_type=attachment_info.get('mime_type'),
                    size=attachment_info.get('size'),
                    meta_data={
                        'type': 'user_uploaded',
                        'uploaded_via': 'medical_record_form'
                    },
                    created_by=current_user_id
                )
                db.session.add(attachment)
    
    db.session.commit()
    
    return jsonify({
        'message': '醫療紀錄創建成功',
        'medical_record': medical_record.to_dict()
    }), 201


@medical_records_bp.route('/animals/<int:animal_id>/medical-records', methods=['GET'])
def list_medical_records(animal_id):
    """
    取得動物的醫療紀錄列表 (公開端點)
    """
    # 檢查動物是否存在
    animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
    if not animal:
        abort(404, message='動物不存在')
    
    # 查詢醫療紀錄
    records = MedicalRecord.query.filter_by(
        animal_id=animal_id,
        deleted_at=None
    ).order_by(MedicalRecord.date.desc()).all()
    
    return jsonify({
        'total': len(records),
        'medical_records': [record.to_dict() for record in records]
    }), 200


@medical_records_bp.route('/<int:record_id>', methods=['PATCH'])
@jwt_required()
def update_medical_record(record_id):
    """
    更新醫療紀錄
    僅創建者、動物擁有者或管理員可更新
    """
    current_user_id = int(get_jwt_identity())
    
    record = MedicalRecord.query.filter_by(
        medical_record_id=record_id,
        deleted_at=None
    ).first()
    
    if not record:
        abort(404, message='醫療紀錄不存在')
    
    # 檢查權限
    user = User.query.get(current_user_id)
    if not user:
        abort(404, message='用戶不存在')
    
    # 獲取動物資料以檢查擁有者
    animal = Animal.query.get(record.animal_id)
    
    # 權限檢查: 醫療紀錄創建者、動物擁有者、或收容所成員可更新
    # 管理員不能直接編輯醫療記錄，只能查看和驗證
    has_permission = False
    
    # 管理員不能直接編輯醫療記錄（保護醫療記錄的專業性和完整性）
    if user.role == UserRole.ADMIN:
        has_permission = False
    elif record.created_by == current_user_id:
        # 醫療紀錄創建者可更新（限時24小時）
        from datetime import datetime, timedelta
        if record.created_at and datetime.utcnow() - record.created_at <= timedelta(hours=24):
            has_permission = True
    elif animal and animal.owner_id and animal.owner_id == current_user_id:
        # 個人送養動物：動物擁有者可更新
        has_permission = True
    elif animal and animal.shelter_id and user.role == UserRole.SHELTER_MEMBER and user.primary_shelter_id == animal.shelter_id:
        # 收容所動物：該收容所成員可更新
        has_permission = True
    
    if not has_permission:
        if user.role == UserRole.ADMIN:
            abort(403, message='管理員無法直接編輯醫療記錄，請使用"標記需要修正"功能通知相關人員')
        else:
            abort(403, message='僅創建者(24小時內)、動物擁有者或收容所成員可更新醫療紀錄')
    
    data = request.get_json()
    
    # 可更新的欄位
    if 'record_type' in data:
        try:
            record.record_type = RecordType(data['record_type'])
        except ValueError:
            abort(400, message=f'無效的紀錄類型: {data["record_type"]}')
    
    if 'date' in data:
        try:
            date_str = data['date'].strip()
            # 嘗試多種日期格式
            date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y']
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
            
            if parsed_date is None:
                abort(400, message='日期格式錯誤,支援格式: YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY, DD-MM-YYYY')
            
            record.date = parsed_date
        except Exception:
            abort(400, message='日期格式錯誤,支援格式: YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY, DD-MM-YYYY')
    
    if 'provider' in data:
        record.provider = data['provider']
    
    if 'details' in data:
        record.details = data['details']
    
    if 'attachments' in data:
        # 更新 JSON 附件數據
        new_attachments = data['attachments']
        existing_attachments = record.attachments or []
        
        # 處理新附件：如果有新的附件需要創建 Attachment 記錄
        if new_attachments and isinstance(new_attachments, list):
            from app.models.others import Attachment
            
            # 檢查哪些是新附件（沒有 attachment_id 的）
            for attachment_info in new_attachments:
                if (isinstance(attachment_info, dict) and 
                    'storage_key' in attachment_info and 
                    not attachment_info.get('attachment_id')):
                    
                    # 這是新附件，創建 Attachment 記錄
                    attachment = Attachment(
                        owner_type='medical_record',
                        owner_id=record.medical_record_id,
                        filename=attachment_info.get('filename', '未知檔案'),
                        storage_key=attachment_info.get('storage_key'),
                        url=attachment_info.get('url'),
                        mime_type=attachment_info.get('mime_type'),
                        size=attachment_info.get('size'),
                        meta_data={
                            'type': 'user_uploaded',
                            'uploaded_via': 'medical_record_form_update'
                        },
                        created_by=current_user_id
                    )
                    db.session.add(attachment)
        
        # 更新 JSON 欄位（保留向後兼容性）
        record.attachments = new_attachments
    
    record.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': '醫療紀錄更新成功',
        'medical_record': record.to_dict()
    }), 200


@medical_records_bp.route('/<int:record_id>/verify', methods=['POST'])
@jwt_required()
def verify_medical_record(record_id):
    """
    驗證醫療紀錄 (僅管理員)
    """
    current_user_id = int(get_jwt_identity())
    
    user = User.query.get(current_user_id)
    if not user or user.role != UserRole.ADMIN:
        abort(403, message='僅管理員可驗證醫療紀錄')
    
    record = MedicalRecord.query.filter_by(
        medical_record_id=record_id,
        deleted_at=None
    ).first()
    
    if not record:
        abort(404, message='醫療紀錄不存在')
    
    data = request.get_json() or {}
    verified = data.get('verified', True)
    
    record.verified = verified
    record.verified_by = current_user_id if verified else None
    record.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': f'醫療紀錄已{"驗證" if verified else "取消驗證"}',
        'medical_record': record.to_dict()
    }), 200

