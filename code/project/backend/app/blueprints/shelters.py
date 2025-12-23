"""
Shelters Blueprint - 收容所管理 API
"""
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

from app import db
from app.models.shelter import Shelter
from app.models.animal import Animal, AnimalStatus, Species, AnimalImage, Sex
from app.models.medical_record import MedicalRecord, RecordType
from app.services.shelter_service import shelter_service
from app.services.permission_service import permission_service
from app.exceptions import BusinessException, ValidationError
from config import Config
from minio import Minio

# 初始化 MinIO 客戶端
minio_client = None
try:
    if Config.MINIO_ENDPOINT:
        minio_client = Minio(
            Config.MINIO_ENDPOINT,
            access_key=Config.MINIO_ACCESS_KEY,
            secret_key=Config.MINIO_SECRET_KEY,
            secure=False
        )
except Exception as e:
    print(f"MinIO initialization error in shelters blueprint: {e}")

shelters_bp = Blueprint('shelters', __name__, description='收容所管理 API')


@shelters_bp.route('', methods=['GET'])
def list_shelters():
    """
    獲取收容所列表 (公開端點)
    支援分頁和搜尋
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        verified_only = request.args.get('verified', 'false').lower() == 'true'
        
        result = shelter_service.list_shelters(
            page=page,
            per_page=per_page,
            search=search,
            verified_only=verified_only
        )
        
        return jsonify(result), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@shelters_bp.route('', methods=['POST'])
@jwt_required()
def create_shelter():
    """
    創建收容所
    需要 SHELTER_MEMBER 或 ADMIN 角色
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 檢查權限
        shelter_service.check_shelter_permission(current_user_id)
        
        # 創建收容所
        shelter = shelter_service.create_shelter(
            user_id=current_user_id,
            data=data
        )
        
        return jsonify({
            'message': '收容所創建成功',
            'shelter': shelter.to_dict()
        }), 201
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@shelters_bp.route('/<int:shelter_id>', methods=['GET'])
def get_shelter(shelter_id):
    """取得收容所資訊 (公開端點)"""
    try:
        shelter = shelter_service.get_shelter(shelter_id)
        return jsonify(shelter.to_dict()), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@shelters_bp.route('/<int:shelter_id>', methods=['PATCH'])
@jwt_required()
def update_shelter(shelter_id):
    """
    更新收容所資訊
    僅該收容所的主要負責人或管理員可更新
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 檢查權限
        shelter_service.check_shelter_permission(current_user_id, shelter_id)
        
        # 更新收容所
        shelter = shelter_service.update_shelter(
            shelter_id=shelter_id,
            user_id=current_user_id,
            data=data
        )
        
        return jsonify({
            'message': '收容所更新成功',
            'shelter': shelter.to_dict()
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@shelters_bp.route('/<int:shelter_id>/verify', methods=['POST'])
@jwt_required()
def verify_shelter(shelter_id):
    """
    驗證收容所 (僅管理員)
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        verified = data.get('verified', True)
        
        shelter = shelter_service.verify_shelter(
            shelter_id=shelter_id,
            admin_id=current_user_id,
            verified=verified
        )
        
        return jsonify({
            'message': f'收容所已{"驗證" if verified else "取消驗證"}',
            'shelter': shelter.to_dict()
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@shelters_bp.route('/<int:shelter_id>/animals/batch', methods=['POST'])
@jwt_required()
def batch_upload_animals(shelter_id):
    """
    批次匯入動物 (使用 Job Pattern)
    接收多個檔案:
    - animal_csv: 動物基本資訊 CSV (必填)
    - medical_csv: 醫療記錄 CSV (選填)
    - medical_proofs[]: 醫療證明文件 (選填,檔名格式: {animal_code}_{record_sequence}.pdf)
    - photos[]: 動物照片 (選填,檔名格式: {animal_code}_{order}.jpg)
    返回 202 Accepted + jobId
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 檢查權限
        shelter_service.check_shelter_permission(current_user_id, shelter_id)
        
        # 讀取必要的 CSV 文件
        animal_csv_file = request.files.get('animal_csv')
        if not animal_csv_file:
            raise ValidationError('缺少動物 CSV 檔案')
        
        animal_csv_content = animal_csv_file.read().decode('utf-8')
        animal_csv_filename = animal_csv_file.filename
        
        # 讀取可選的醫療記錄 CSV
        medical_csv_file = request.files.get('medical_csv')
        medical_csv_content = None
        medical_csv_filename = None
        if medical_csv_file:
            medical_csv_content = medical_csv_file.read().decode('utf-8')
            medical_csv_filename = medical_csv_file.filename
        
        # 處理醫療證明文件 - 上傳到 MinIO
        medical_proofs = []
        # 同時支持 'medical_proofs[]' 和 'medical_proofs'
        medical_proof_files = request.files.getlist('medical_proofs[]')
        if not medical_proof_files:
            medical_proof_files = request.files.getlist('medical_proofs')
        
        for file in medical_proof_files:
            if file and file.filename:
                # 上傳到 MinIO
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                
                ext = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
                object_key = f"batch-import/medical-proofs/{shelter_id}/{uuid.uuid4()}.{ext}"
                
                minio_client.put_object(
                    bucket_name=Config.MINIO_BUCKET,
                    object_name=object_key,
                    data=file,
                    length=file_size,
                    content_type=file.content_type or 'application/octet-stream'
                )
                
                file_url = f"/minio/{Config.MINIO_BUCKET}/{object_key}"
                
                medical_proofs.append({
                    'filename': file.filename,
                    'storage_key': object_key,
                    'url': file_url,
                    'size': file_size,
                    'content_type': file.content_type
                })
        
        # 處理照片文件 - 上傳到 MinIO
        photos = []
        # 同時支持 'photos[]' 和 'photos'
        photo_files = request.files.getlist('photos[]')
        if not photo_files:
            photo_files = request.files.getlist('photos')
        
        for file in photo_files:
            if file and file.filename:
                # 上傳到 MinIO
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                
                ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
                object_key = f"batch-import/photos/{shelter_id}/{uuid.uuid4()}.{ext}"
                
                minio_client.put_object(
                    bucket_name=Config.MINIO_BUCKET,
                    object_name=object_key,
                    data=file,
                    length=file_size,
                    content_type=file.content_type or 'image/jpeg'
                )
                
                file_url = f"/minio/{Config.MINIO_BUCKET}/{object_key}"
                
                photos.append({
                    'filename': file.filename,
                    'storage_key': object_key,
                    'url': file_url,
                    'size': file_size,
                    'content_type': file.content_type
                })
        
        # 創建批次匯入任務
        job = shelter_service.create_batch_import_job(
            shelter_id=shelter_id,
            user_id=current_user_id,
            animal_csv_content=animal_csv_content,
            animal_csv_filename=animal_csv_filename,
            medical_csv_content=medical_csv_content,
            medical_csv_filename=medical_csv_filename,
            medical_proofs=medical_proofs if medical_proofs else None,
            photos=photos if photos else None
        )
        
        return jsonify({
            'message': '批次匯入已加入隊列',
            'job_id': job.job_id,
            'status': job.status.value,
            'files_received': job.payload.get('files_received', {})
        }), 202
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@shelters_bp.route('/<int:shelter_id>/animals/batch/status', methods=['PATCH'])
@jwt_required()
def batch_update_animal_status(shelter_id):
    """
    批次更新動物狀態
    ---
    Request Body:
        animal_ids: List[int] - 動物 ID 列表
        action: str - 操作類型 ('draft', 'submit', 'publish', 'retire')
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 檢查權限
        shelter_service.check_shelter_permission(current_user_id, shelter_id)
        
        # 執行批次更新
        result = shelter_service.batch_update_animal_status(
            shelter_id=shelter_id,
            user_id=current_user_id,
            animal_ids=data.get('animal_ids', []),
            action=data.get('action', '').lower()
        )
        
        return jsonify(result), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@shelters_bp.route('/<int:shelter_id>/animals', methods=['GET'])
@jwt_required()
def get_shelter_animals(shelter_id):
    """
    取得收容所的動物列表 (含草稿狀態，供管理用)
    支援多種篩選條件: status, species, sex, keyword, age range, vaccinated
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 檢查權限
        shelter_service.check_shelter_permission(current_user_id, shelter_id)
        
        # 取得查詢參數
        status = request.args.get('status')
        species = request.args.get('species')
        sex = request.args.get('sex')
        keyword = request.args.get('keyword') or request.args.get('q')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        vaccinated = request.args.get('vaccinated')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # 驗證 shelter 存在
        shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
        if not shelter:
            abort(404, message='收容所不存在')
        
        # 建立查詢
        query = Animal.query.filter(Animal.shelter_id == shelter_id, Animal.deleted_at == None)
        
        # 套用篩選
        if status:
            try:
                query = query.filter_by(status=AnimalStatus[status.upper()])
            except KeyError:
                abort(400, message=f'無效的狀態: {status}')
        
        if species:
            try:
                query = query.filter_by(species=Species[species.upper()])
            except KeyError:
                abort(400, message=f'無效的物種: {species}')
        
        if sex:
            try:
                query = query.filter_by(sex=Sex[sex.upper()])
            except KeyError:
                abort(400, message=f'無效的性別: {sex}')
        
        if keyword:
            kw = f"%{keyword}%"
            query = query.filter(db.or_(
                Animal.name.ilike(kw),
                Animal.breed.ilike(kw),
                Animal.color.ilike(kw)
            ))
        
        if min_age is not None or max_age is not None:
            today = datetime.utcnow().date()
            if min_age is not None:
                cutoff_max = today.replace(year=today.year - min_age)
                query = query.filter(Animal.dob != None, Animal.dob <= cutoff_max)
            if max_age is not None:
                cutoff_min = today.replace(year=today.year - max_age)
                query = query.filter(Animal.dob != None, Animal.dob >= cutoff_min)
        
        if vaccinated is not None:
            vaccinated_bool = str(vaccinated).lower() == 'true'
            if vaccinated_bool:
                query = query.filter(Animal.medical_records.any(
                    db.and_(MedicalRecord.record_type == RecordType.VACCINE, MedicalRecord.verified == True)
                ))
            else:
                query = query.filter(~Animal.medical_records.any(
                    db.and_(MedicalRecord.record_type == RecordType.VACCINE, MedicalRecord.verified == True)
                ))
        
        # 分頁
        pagination = query.order_by(Animal.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        animals = pagination.items
        for animal in animals:
            animal.images = AnimalImage.query.filter_by(animal_id=animal.animal_id).order_by(AnimalImage.order).all()
        
        return jsonify({
            'animals': [animal.to_dict(include_relations=True) for animal in animals],
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500
