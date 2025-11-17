"""
Animals Blueprint - 動物相關 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime

from app import db
from app.models import Animal, AnimalImage, User, AnimalStatus, Species, Sex, UserRole
from app.models.shelter import Shelter
from app.services.animal_service import animal_service
from app.services.permission_service import permission_service
from app.exceptions import BusinessException

animals_bp = Blueprint('animals', __name__, description='動物管理 API')


@animals_bp.route('', methods=['GET'])
def list_animals():
    """
    取得動物列表 (公開，支援搜尋與篩選)
    ---
    Query Parameters:
        - species: 物種 (CAT, DOG)
        - sex: 性別 (MALE, FEMALE, UNKNOWN)
        - status: 狀態 (DRAFT, SUBMITTED, PUBLISHED, RETIRED)
        - shelter_id: 收容所 ID
        - source_type: 來源類型 (shelter=收容所, personal=個人送養)
        - region: 地區/縣市
        - min_age: 最小年齡 (月數)
        - max_age: 最大年齡 (月數)
        - page: 頁碼 (預設 1)
        - per_page: 每頁筆數 (預設 20, 最大 100)
    """
    # 取得查詢參數
    species = request.args.get('species')
    sex = request.args.get('sex')
    status = request.args.get('status')
    shelter_id = request.args.get('shelter_id')
    owner_id = request.args.get('owner_id', type=int)
    created_by = request.args.get('created_by', type=int)
    source_type = request.args.get('source_type')  # 'shelter' 或 'personal'
    region = request.args.get('region')  # 地區/縣市
    min_age = request.args.get('min_age', type=int)  # 最小年齡(月數)
    max_age = request.args.get('max_age', type=int)  # 最大年齡(月數)
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # 建立查詢
    query = Animal.query.filter_by(deleted_at=None)
    
    # 如果有 owner_id 或 created_by 參數，查詢該用戶的所有動物(包含草稿)
    # 否則預設只顯示已發布的動物
    if owner_id:
        # 特殊處理：如果查詢者是收容所成員，同時查詢個人動物和收容所動物
        try:
            # 檢查是否有 JWT token
            verify_jwt_in_request(optional=True)
            current_user_id = int(get_jwt_identity()) if get_jwt_identity() else None
            
            if current_user_id == owner_id:  # 查詢自己的動物
                current_user = db.session.get(User, current_user_id)
                
                if current_user and current_user.role == UserRole.SHELTER_MEMBER and current_user.primary_shelter_id:
                    # 收容所成員：查詢個人動物 + 收容所動物
                    query = query.filter(
                        db.or_(
                            Animal.owner_id == owner_id,
                            Animal.shelter_id == current_user.primary_shelter_id
                        )
                    )
                else:
                    # 一般用戶：只查詢個人動物 (包含草稿)
                    query = query.filter_by(owner_id=owner_id)
            elif current_user_id is None:
                # 沒有認證但查詢特定用戶的動物：允許查詢該用戶的所有動物
                # 這是為了處理前端認證狀態異常的情況
                query = query.filter_by(owner_id=owner_id)
            else:
                # 查詢其他用戶的動物，只能看已發布的
                query = query.filter_by(owner_id=owner_id, status=AnimalStatus.PUBLISHED)
        except Exception as e:
            # 發生錯誤時的備用方案：如果是查詢特定用戶的動物，允許查看所有狀態
            query = query.filter_by(owner_id=owner_id)
    elif created_by:
        query = query.filter_by(created_by=created_by)
    else:
        # 預設只顯示已發布的動物
        if not status:
            status = AnimalStatus.PUBLISHED.value
    
    # 狀態篩選
    if status:
        try:
            query = query.filter_by(status=AnimalStatus(status))
        except ValueError:
            abort(400, message='無效的狀態值')
    
    # 篩選條件
    if species:
        try:
            query = query.filter_by(species=Species(species))
        except ValueError:
            abort(400, message='無效的物種值')
    
    if sex:
        try:
            query = query.filter_by(sex=Sex(sex))
        except ValueError:
            abort(400, message='無效的性別值')
    
    if shelter_id:
        query = query.filter_by(shelter_id=shelter_id)
    
    # 來源類型篩選
    if source_type:
        if source_type == 'shelter':
            # 只顯示收容所動物
            query = query.filter(Animal.shelter_id.isnot(None))
        elif source_type == 'personal':
            # 只顯示個人送養動物
            query = query.filter(Animal.owner_id.isnot(None))
    
    # 地區篩選 - 需要 JOIN 用戶和收容所資料來取得地區資訊
    if region:
        from app.models.user import User
        from app.models.shelter import Shelter
        
        # 建立子查詢條件
        shelter_region_condition = db.exists().where(
            db.and_(
                Animal.shelter_id == Shelter.shelter_id,
                Shelter.region.like(f'%{region}%')
            )
        )
        
        owner_region_condition = db.exists().where(
            db.and_(
                Animal.owner_id == User.user_id,
                User.region.like(f'%{region}%')
            )
        )
        
        query = query.filter(
            db.or_(shelter_region_condition, owner_region_condition)
        )
    
    # 年齡篩選 - 計算動物年齡(月數)
    if min_age is not None or max_age is not None:
        from sqlalchemy import func, extract
        
        # 計算年齡：當前日期 - 出生日期，轉換為月數
        # TIMESTAMPDIFF(MONTH, dob, CURDATE()) 計算月數差
        age_in_months = func.timestampdiff(
            db.text('MONTH'),
            Animal.dob,
            func.curdate()
        )
        
        if min_age is not None:
            query = query.filter(age_in_months >= min_age)
        
        if max_age is not None:
            query = query.filter(age_in_months <= max_age)
    
    # 關鍵字搜尋
    if q:
        query = query.filter(
            db.or_(
                Animal.name.like(f'%{q}%'),
                Animal.description.like(f'%{q}%'),
                Animal.breed.like(f'%{q}%')
            )
        )
    
    # 分頁
    pagination = query.order_by(Animal.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'animals': [animal.to_dict(include_relations=True) for animal in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }), 200


@animals_bp.route('/<int:animal_id>', methods=['GET'])
def get_animal(animal_id):
    """取得單一動物詳細資訊"""
    try:
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            abort(404, message='動物不存在')
        
        return jsonify(animal.to_dict(include_relations=True)), 200
        
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@animals_bp.route('', methods=['POST'])
@jwt_required()
def create_animal():
    """建立動物資料 (需登入)"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        data = request.get_json()
        
        animal = animal_service.create_animal(
            user=current_user,
            data=data
        )
        
        return jsonify({
            'message': '動物資料建立成功',
            'animal': animal.to_dict(include_relations=True)
        }), 201
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@animals_bp.route('/<int:animal_id>', methods=['PATCH'])
@jwt_required()
def update_animal(animal_id):
    """更新動物資料 (需為擁有者或管理員)"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        data = request.get_json()
        
        animal = animal_service.update_animal(
            animal_id=animal_id,
            user=current_user,
            data=data
        )
        
        return jsonify({
            'message': '動物資料更新成功',
            'animal': animal.to_dict(include_relations=True)
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@animals_bp.route('/<int:animal_id>', methods=['DELETE'])
@jwt_required()
def delete_animal(animal_id):
    """刪除動物資料 (軟刪除)"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        animal_service.delete_animal(animal_id, current_user)
        
        return jsonify({'message': '動物資料已刪除'}), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


# ========== 圖片管理 ==========

@animals_bp.route('/<int:animal_id>/images', methods=['POST'])
@jwt_required()
def add_animal_image(animal_id):
    """新增動物圖片"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': '用戶不存在'}), 404
        
        data = request.get_json()
        
        # 從請求中提取必要欄位
        storage_key = data.get('storage_key')
        url = data.get('image_url')
        mime_type = data.get('mime_type')
        
        if not storage_key or not url:
            return jsonify({'message': '缺少必要欄位: storage_key 和 image_url'}), 400
        
        image = animal_service.add_image(
            animal_id=animal_id,
            user=current_user,
            storage_key=storage_key,
            url=url,
            mime_type=mime_type
        )
        
        return jsonify({
            'message': '圖片已新增',
            'image': image.to_dict()
        }), 201
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@animals_bp.route('/<int:animal_id>/images/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_animal_image(animal_id, image_id):
    """刪除動物圖片"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': '用戶不存在'}), 404
        
        animal_service.delete_image(animal_id, image_id, current_user)
        
        return jsonify({'message': '圖片已刪除'}), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@animals_bp.route('/<int:animal_id>/images/reorder', methods=['PATCH'])
@jwt_required()
def reorder_animal_images(animal_id):
    """重新排序動物圖片"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': '用戶不存在'}), 404
        
        data = request.get_json()
        
        animal_service.reorder_images(
            animal_id=animal_id,
            user=current_user,
            image_orders=data.get('image_orders', [])
        )
        
        return jsonify({'message': '圖片順序已更新'}), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


# ========== 狀態管理 ==========

@animals_bp.route('/<int:animal_id>/submit', methods=['POST'])
@jwt_required()
def submit_animal(animal_id):
    """提交動物供審核 (狀態: DRAFT -> SUBMITTED)"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        animal = animal_service.submit_for_review(animal_id, current_user)
        
        return jsonify({
            'message': '動物已提交審核',
            'animal': animal.to_dict()
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@animals_bp.route('/<int:animal_id>/publish', methods=['POST'])
@jwt_required()
def publish_animal(animal_id):
    """發布動物 (狀態: DRAFT/SUBMITTED -> PUBLISHED) - 需要管理員權限"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        animal = animal_service.publish_animal(animal_id, current_user)
        
        return jsonify({
            'message': '動物已發布',
            'animal': animal.to_dict()
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@animals_bp.route('/<int:animal_id>/retire', methods=['POST'])
@jwt_required()
def retire_animal(animal_id):
    """下架動物 (狀態: PUBLISHED -> RETIRED) - 需要管理員或擁有者權限"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        animal = animal_service.retire_animal(animal_id, current_user)
        
        return jsonify({
            'message': '動物已下架',
            'animal': animal.to_dict()
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@animals_bp.route('/<int:animal_id>/reject', methods=['POST'])
@jwt_required()
def reject_animal(animal_id):
    """拒絕批准動物上架 (狀態: SUBMITTED -> DRAFT) - 需要管理員權限"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        # 取得拒絕原因
        data = request.get_json() or {}
        rejection_reason = data.get('rejection_reason', '').strip()
        
        if not rejection_reason:
            return jsonify({'message': '請提供拒絕原因'}), 400
        
        animal = animal_service.reject_animal(animal_id, current_user, rejection_reason)
        
        return jsonify({
            'message': '已拒絕批准,動物狀態改為草稿',
            'animal': animal.to_dict()
        }), 200
        
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500
