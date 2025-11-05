"""
Shelters Blueprint - 收容所管理 API
"""
import base64
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.shelter import Shelter
from app.models.user import User, UserRole
from app.models.others import Job, JobType, JobStatus
from app.models.animal import Animal, AnimalStatus, Species, AnimalImage
from app.services.audit_service import audit_service
import re

shelters_bp = Blueprint('shelters', __name__, description='收容所管理 API')


def check_shelter_member_or_admin(user_id, shelter_id=None):
    """檢查用戶是否為收容所成員或管理員"""
    user = User.query.get(user_id)
    if not user:
        abort(404, message='用戶不存在')
    
    # 管理員有完全權限
    if user.role == UserRole.ADMIN:
        return True
    
    # 收容所成員需要檢查關聯
    if user.role == UserRole.SHELTER_MEMBER:
        if shelter_id:
            # 檢查是否為該收容所的主要負責人或關聯成員
            shelter = Shelter.query.get(shelter_id)
            if shelter and (shelter.primary_account_user_id == user_id or user.primary_shelter_id == shelter_id):
                return True
        else:
            # 創建新收容所時,只要是收容所成員即可
            return True
    
    return False


@shelters_bp.route('', methods=['GET'])
def list_shelters():
    """
    獲取收容所列表 (公開端點)
    支援分頁和搜尋
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    verified_only = request.args.get('verified', 'false').lower() == 'true'
    
    # 驗證分頁參數
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
    
    # 構建查詢
    query = Shelter.query.filter_by(deleted_at=None)
    
    # 搜尋過濾
    if search:
        query = query.filter(
            db.or_(
                Shelter.name.ilike(f'%{search}%'),
                Shelter.contact_email.ilike(f'%{search}%')
            )
        )
    
    # 僅顯示已驗證收容所
    if verified_only:
        query = query.filter_by(verified=True)
    
    # 排序和分頁
    query = query.order_by(Shelter.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'shelters': [shelter.to_dict() for shelter in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@shelters_bp.route('', methods=['POST'])
@jwt_required()
def create_shelter():
    """
    創建收容所
    需要 SHELTER_MEMBER 或 ADMIN 角色
    """
    current_user_id = int(get_jwt_identity())
    
    # 檢查權限
    if not check_shelter_member_or_admin(current_user_id):
        abort(403, message='僅收容所成員或管理員可創建收容所')
    
    data = request.get_json()
    
    # 驗證必填欄位
    required_fields = ['name', 'contact_email', 'contact_phone', 'address']
    for field in required_fields:
        if field not in data:
            abort(400, message=f'缺少必填欄位: {field}')
    
    # 驗證 email 格式
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data['contact_email']):
        abort(400, message='Email 格式不正確')
    
    # 驗證 address 結構
    if not isinstance(data['address'], dict):
        abort(400, message='地址必須為JSON對象')
    
    address_fields = ['street', 'city', 'county', 'postal_code']
    for field in address_fields:
        if field not in data['address']:
            abort(400, message=f'地址缺少必填欄位: {field}')
    
    # 生成 slug (如果未提供)
    slug = data.get('slug')
    if slug:
        # 檢查 slug 唯一性
        if Shelter.query.filter_by(slug=slug).first():
            abort(400, message='Slug 已存在')
    
    # 創建收容所
    shelter = Shelter(
        name=data['name'],
        slug=slug,
        contact_email=data['contact_email'],
        contact_phone=data['contact_phone'],
        address=data['address'],
        region=data.get('region'),  # 可選的地區欄位
        verified=False,  # 預設未驗證
        primary_account_user_id=current_user_id
    )
    
    db.session.add(shelter)
    db.session.commit()
    
    return jsonify({
        'message': '收容所創建成功',
        'shelter': shelter.to_dict()
    }), 201


@shelters_bp.route('/<int:shelter_id>', methods=['GET'])
def get_shelter(shelter_id):
    """取得收容所資訊 (公開端點)"""
    shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
    
    if not shelter:
        abort(404, message='收容所不存在')
    
    return jsonify(shelter.to_dict()), 200


@shelters_bp.route('/<int:shelter_id>', methods=['PATCH'])
@jwt_required()
def update_shelter(shelter_id):
    """
    更新收容所資訊
    僅該收容所的主要負責人或管理員可更新
    """
    current_user_id = int(get_jwt_identity())
    
    shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
    if not shelter:
        abort(404, message='收容所不存在')
    
    # 檢查權限
    if not check_shelter_member_or_admin(current_user_id, shelter_id):
        abort(403, message='無權限更新此收容所')
    
    data = request.get_json()
    
    # 可更新的欄位
    allowed_fields = ['name', 'slug', 'contact_email', 'contact_phone', 'address', 'region']
    
    for field in allowed_fields:
        if field in data:
            # 特殊驗證
            if field == 'contact_email':
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, data['contact_email']):
                    abort(400, message='Email 格式不正確')
            
            if field == 'slug' and data['slug']:
                # 檢查 slug 唯一性(排除自己)
                existing = Shelter.query.filter(
                    Shelter.slug == data['slug'],
                    Shelter.shelter_id != shelter_id
                ).first()
                if existing:
                    abort(400, message='Slug 已存在')
            
            if field == 'address':
                if not isinstance(data['address'], dict):
                    abort(400, message='地址必須為JSON對象')
                address_fields = ['street', 'city', 'county', 'postal_code']
                for addr_field in address_fields:
                    if addr_field not in data['address']:
                        abort(400, message=f'地址缺少必填欄位: {addr_field}')
            
            setattr(shelter, field, data[field])
    
    shelter.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': '收容所更新成功',
        'shelter': shelter.to_dict()
    }), 200


@shelters_bp.route('/<int:shelter_id>/verify', methods=['POST'])
@jwt_required()
def verify_shelter(shelter_id):
    """
    驗證收容所 (僅管理員)
    """
    current_user_id = int(get_jwt_identity())
    
    user = User.query.get(current_user_id)
    if not user or user.role != UserRole.ADMIN:
        abort(403, message='僅管理員可驗證收容所')
    
    shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
    if not shelter:
        abort(404, message='收容所不存在')
    
    data = request.get_json() or {}
    verified = data.get('verified', True)
    
    shelter.verified = verified
    shelter.updated_at = datetime.utcnow()
    db.session.commit()
    
    # 記錄審計日誌
    audit_service.log_shelter_verify(shelter_id, current_user_id, verified)
    
    return jsonify({
        'message': f'收容所已{"驗證" if verified else "取消驗證"}',
        'shelter': shelter.to_dict()
    }), 200


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
    current_user_id = int(get_jwt_identity())
    
    shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
    if not shelter:
        abort(404, message='收容所不存在')
    
    # 檢查權限
    if not check_shelter_member_or_admin(current_user_id, shelter_id):
        abort(403, message='無權限執行批次匯入')
    
    # === 處理動物基本資訊 CSV (必填) ===
    if 'animal_csv' not in request.files:
        abort(400, message='缺少必填欄位: animal_csv')
    
    animal_csv = request.files['animal_csv']
    
    if animal_csv.filename == '':
        abort(400, message='未選擇動物基本資訊 CSV 檔案')
    
    # 驗證檔案類型
    if not animal_csv.filename.lower().endswith('.csv'):
        abort(400, message='動物基本資訊檔案必須為 CSV 格式')
    
    # 驗證檔案大小 (最大 10MB)
    animal_csv.seek(0, 2)
    file_size = animal_csv.tell()
    animal_csv.seek(0)
    
    if file_size > 10 * 1024 * 1024:
        abort(400, message='動物基本資訊 CSV 檔案不能超過 10MB')
    
    # 讀取動物 CSV 內容
    try:
        animal_csv_content = animal_csv.read().decode('utf-8')
    except UnicodeDecodeError:
        abort(400, message='動物基本資訊 CSV 編碼錯誤,請使用 UTF-8 編碼')
    
    # 驗證 CSV 格式
    import csv
    import io
    try:
        csv_reader = csv.DictReader(io.StringIO(animal_csv_content))
        first_row = next(csv_reader, None)
        if not first_row:
            abort(400, message='動物基本資訊 CSV 檔案為空')
    except Exception as e:
        abort(400, message=f'動物基本資訊 CSV 格式錯誤: {str(e)}')
    
    # === 處理醫療記錄 CSV (選填) ===
    medical_csv_content = None
    if 'medical_csv' in request.files:
        medical_csv = request.files['medical_csv']
        
        if medical_csv.filename and medical_csv.filename != '':
            # 驗證檔案類型
            if not medical_csv.filename.lower().endswith('.csv'):
                abort(400, message='醫療記錄檔案必須為 CSV 格式')
            
            # 驗證檔案大小
            medical_csv.seek(0, 2)
            file_size = medical_csv.tell()
            medical_csv.seek(0)
            
            if file_size > 10 * 1024 * 1024:
                abort(400, message='醫療記錄 CSV 檔案不能超過 10MB')
            
            # 讀取內容
            try:
                medical_csv_content = medical_csv.read().decode('utf-8')
            except UnicodeDecodeError:
                abort(400, message='醫療記錄 CSV 編碼錯誤,請使用 UTF-8 編碼')
    
    # === 處理醫療證明文件 (選填) ===
    medical_proof_data = []
    if 'medical_proofs' in request.files:
        medical_proofs = request.files.getlist('medical_proofs')
        
        # 導入 MinIO 客戶端
        from app.blueprints.uploads import minio_client, minio_available
        from config import Config
        import uuid as uuid_lib
        
        if not minio_available:
            abort(500, message='MinIO 服務不可用')
        
        for proof in medical_proofs:
            if proof.filename and proof.filename != '':
                # 驗證檔案類型 (PDF, DOC, DOCX, 圖片)
                allowed_types = [
                    'application/pdf',
                    'application/msword', 
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'image/jpeg', 'image/jpg', 'image/png'
                ]
                
                if not proof.content_type or proof.content_type not in allowed_types:
                    abort(400, message=f'醫療證明文件 {proof.filename} 格式不支援。支援格式: PDF, DOC, DOCX, JPG, PNG')
                
                # 驗證檔案大小 (最大 10MB per file)
                proof.seek(0, 2)
                proof_size = proof.tell()
                proof.seek(0)
                
                if proof_size > 10 * 1024 * 1024:
                    abort(400, message=f'醫療證明文件 {proof.filename} 超過 10MB 限制')
                
                # 驗證檔名格式: animal_code_record_sequence.ext
                import re
                filename_pattern = re.compile(r'^(.+?)_(\d+)\.(pdf|doc|docx|jpg|jpeg|png)$', re.IGNORECASE)
                match = filename_pattern.match(proof.filename)
                
                if not match:
                    abort(400, message=f'醫療證明文件 {proof.filename} 檔名格式錯誤。正確格式: 動物編號_記錄序號.副檔名 (例: 001_1.pdf)')
                
                animal_code = match.group(1)
                record_sequence = int(match.group(2))
                
                # 上傳到 MinIO
                try:
                    # 生成唯一的 object key
                    ext = proof.filename.split('.')[-1] if '.' in proof.filename else 'pdf'
                    object_key = f"medical-proofs/{shelter_id}/{uuid_lib.uuid4()}.{ext}"
                    
                    # 上傳到 MinIO
                    minio_client.put_object(
                        bucket_name=Config.MINIO_BUCKET,
                        object_name=object_key,
                        data=proof,
                        length=proof_size,
                        content_type=proof.content_type
                    )
                    
                    # 生成公開 URL
                    proof_url = f"http://{Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'}/{Config.MINIO_BUCKET}/{object_key}"
                    
                    medical_proof_data.append({
                        'filename': proof.filename,
                        'content_type': proof.content_type,
                        'storage_key': object_key,
                        'url': proof_url,
                        'size': proof_size,
                        'animal_code': animal_code,
                        'record_sequence': record_sequence
                    })
                except Exception as e:
                    db.session.rollback()
                    abort(400, message=f'上傳醫療證明文件 {proof.filename} 到 MinIO 失敗: {str(e)}')

    # === 處理照片 (選填) ===
    photos_data = []
    if 'photos' in request.files:
        photos = request.files.getlist('photos')
        
        # 導入 MinIO 客戶端
        from app.blueprints.uploads import minio_client, minio_available
        from config import Config
        import uuid as uuid_lib
        
        if not minio_available:
            abort(500, message='MinIO 服務不可用')
        
        for photo in photos:
            if photo.filename and photo.filename != '':
                # 驗證檔案類型
                if not photo.content_type or not photo.content_type.startswith('image/'):
                    abort(400, message=f'檔案 {photo.filename} 不是圖片格式')
                
                # 驗證檔案大小 (最大 5MB per photo)
                photo.seek(0, 2)
                photo_size = photo.tell()
                photo.seek(0)
                
                if photo_size > 5 * 1024 * 1024:
                    abort(400, message=f'照片 {photo.filename} 超過 5MB 限制')
                
                # 上傳照片到 MinIO
                try:
                    # 生成唯一的 object key
                    ext = photo.filename.split('.')[-1] if '.' in photo.filename else 'jpg'
                    object_key = f"batch-uploads/{shelter_id}/{uuid_lib.uuid4()}.{ext}"
                    
                    # 上傳到 MinIO
                    minio_client.put_object(
                        bucket_name=Config.MINIO_BUCKET,
                        object_name=object_key,
                        data=photo,
                        length=photo_size,
                        content_type=photo.content_type or 'image/jpeg'
                    )
                    
                    # 生成公開 URL
                    photo_url = f"http://{Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'}/{Config.MINIO_BUCKET}/{object_key}"
                    
                    photos_data.append({
                        'filename': photo.filename,
                        'content_type': photo.content_type,
                        'storage_key': object_key,
                        'url': photo_url,
                        'size': photo_size
                    })
                except Exception as e:
                    db.session.rollback()
                    abort(400, message=f'上傳照片 {photo.filename} 到 MinIO 失敗: {str(e)}')
    
    # 獲取醫療記錄檔名 (安全處理)
    medical_csv_filename = None
    if 'medical_csv' in request.files:
        medical_file = request.files['medical_csv']
        if medical_file and medical_file.filename:
            medical_csv_filename = medical_file.filename
    
    # 創建 Job 記錄
    try:
        job = Job(
            type=JobType.IMPORT_ANIMALS.value,
            status=JobStatus.PENDING,
            created_by=current_user_id,
            payload={
                'shelter_id': shelter_id,
                'animal_csv_content': animal_csv_content,
                'medical_csv_content': medical_csv_content,
                'medical_proofs': medical_proof_data,
                'photos': photos_data,
                'animal_csv_filename': animal_csv.filename,
                'medical_csv_filename': medical_csv_filename,
                'options': {}
            }
        )
        
        db.session.add(job)
        db.session.commit()
        
        # 將 job 加入 Celery 隊列
        from app.tasks import process_animal_batch_import
        process_animal_batch_import.delay(job.job_id)
        
        return jsonify({
            'message': '批次匯入已加入隊列',
            'job_id': job.job_id,
            'status': job.status.value,
            'files_received': {
                'animal_csv': animal_csv.filename,
                'medical_csv': medical_csv_filename,
                'medical_proofs_count': len(medical_proof_data),
                'photos_count': len(photos_data)
            }
        }), 202
        
    except Exception as e:
        db.session.rollback()
        abort(500, message=f'創建批次匯入任務失敗: {str(e)}')


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
    current_user_id = int(get_jwt_identity())
    
    shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
    if not shelter:
        abort(404, message='收容所不存在')
    
    # 檢查權限
    if not check_shelter_member_or_admin(current_user_id, shelter_id):
        abort(403, message='無權限執行批次操作')
    
    # 解析請求
    data = request.get_json()
    if not data:
        abort(400, message='缺少請求資料')
    
    animal_ids = data.get('animal_ids', [])
    action = data.get('action', '').lower()
    
    if not animal_ids:
        abort(400, message='請選擇要處理的動物')
    
    if action not in ['draft', 'submit', 'publish', 'retire']:
        abort(400, message='無效的操作類型。支援: draft, submit, publish, retire')
    
    # 檢查動物是否屬於該收容所
    animals = Animal.query.filter(
        Animal.animal_id.in_(animal_ids),
        Animal.shelter_id == shelter_id,
        Animal.deleted_at == None
    ).all()
    
    if len(animals) != len(animal_ids):
        found_ids = [a.animal_id for a in animals]
        missing_ids = [aid for aid in animal_ids if aid not in found_ids]
        abort(400, message=f'以下動物不存在或不屬於該收容所: {missing_ids}')
    
    # 執行批次狀態更新
    success_count = 0
    failed_count = 0
    errors = []
    
    for animal in animals:
        try:
            # 根據 action 更新狀態
            if action == 'draft':
                if animal.status in [AnimalStatus.SUBMITTED, AnimalStatus.PUBLISHED, AnimalStatus.RETIRED]:
                    animal.status = AnimalStatus.DRAFT
                    animal.updated_at = datetime.utcnow()
                    success_count += 1
                else:
                    errors.append(f'動物 {animal.animal_id} ({animal.name}) 目前狀態無法變更為草稿')
                    failed_count += 1
                    
            elif action == 'submit':
                if animal.status == AnimalStatus.DRAFT:
                    animal.status = AnimalStatus.SUBMITTED
                    animal.updated_at = datetime.utcnow()
                    success_count += 1
                else:
                    errors.append(f'動物 {animal.animal_id} ({animal.name}) 必須是草稿狀態才能提交')
                    failed_count += 1
                    
            elif action == 'publish':
                if animal.status in [AnimalStatus.SUBMITTED, AnimalStatus.DRAFT]:
                    animal.status = AnimalStatus.PUBLISHED
                    animal.updated_at = datetime.utcnow()
                    success_count += 1
                else:
                    errors.append(f'動物 {animal.animal_id} ({animal.name}) 目前狀態無法發布')
                    failed_count += 1
                    
            elif action == 'retire':
                if animal.status == AnimalStatus.PUBLISHED:
                    animal.status = AnimalStatus.RETIRED
                    animal.updated_at = datetime.utcnow()
                    success_count += 1
                else:
                    errors.append(f'動物 {animal.animal_id} ({animal.name}) 必須是已發布狀態才能下架')
                    failed_count += 1
                    
        except Exception as e:
            errors.append(f'動物 {animal.animal_id} ({animal.name}) 處理失敗: {str(e)}')
            failed_count += 1
    
    # 提交變更
    try:
        db.session.commit()
        
        # 創建通知
        from app.services.notification_service import NotificationService
        
        # 計算狀態中文名稱
        action_names = {
            'draft': '草稿',
            'submit': '提交審核',
            'publish': '發布',
            'retire': '下架'
        }
        action_name = action_names.get(action, action)
        
        NotificationService.create(
            recipient_id=current_user_id,
            type='system_notification',
            payload={
                'title': f'批次{action_name}完成',
                'message': f'成功處理 {success_count} 隻動物，失敗 {failed_count} 隻動物',
                'priority': 'NORMAL'
            }
        )
        
        return jsonify({
            'message': f'批次{action_name}完成',
            'success_count': success_count,
            'failed_count': failed_count,
            'total_count': len(animal_ids),
            'errors': errors[:10]  # 只返回前10個錯誤
        }), 200
        
    except Exception as e:
        db.session.rollback()
        abort(500, message=f'批次更新失敗: {str(e)}')


@shelters_bp.route('/<int:shelter_id>/animals', methods=['GET'])
@jwt_required()
def get_shelter_animals(shelter_id):
    """
    取得收容所的動物列表 (含草稿狀態，供管理用)
    ---
    Query Parameters:
        - status: 狀態篩選 (DRAFT, SUBMITTED, PUBLISHED, RETIRED)
        - species: 物種篩選 (CAT, DOG)
        - page: 頁碼 (預設 1)
        - per_page: 每頁筆數 (預設 20)
    """
    current_user_id = int(get_jwt_identity())
    
    shelter = Shelter.query.filter_by(shelter_id=shelter_id, deleted_at=None).first()
    if not shelter:
        abort(404, message='收容所不存在')
    
    # 檢查權限
    if not check_shelter_member_or_admin(current_user_id, shelter_id):
        abort(403, message='無權限查看收容所動物')
    
    # 取得查詢參數
    status = request.args.get('status')
    species = request.args.get('species')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # 建立查詢
    query = Animal.query.filter(
        Animal.shelter_id == shelter_id,
        Animal.deleted_at == None
    )
    
    # 套用篩選
    if status:
        try:
            status_enum = AnimalStatus[status.upper()]
            query = query.filter_by(status=status_enum)
        except KeyError:
            abort(400, message=f'無效的狀態: {status}')
    
    if species:
        try:
            species_enum = Species[species.upper()]
            query = query.filter_by(species=species_enum)
        except KeyError:
            abort(400, message=f'無效的物種: {species}')
    
    # 分頁
    pagination = query.order_by(Animal.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    animals = pagination.items
    
    # 載入圖片
    for animal in animals:
        animal.images = AnimalImage.query.filter_by(
            animal_id=animal.animal_id
        ).order_by(AnimalImage.order).all()
    
    return jsonify({
        'animals': [animal.to_dict(include_relations=True) for animal in animals],
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next
    }), 200
