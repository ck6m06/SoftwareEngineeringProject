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
    try:
        # 檢查是否有 JWT token (可選)
        verify_jwt_in_request(optional=True)
        current_user_id = int(get_jwt_identity()) if get_jwt_identity() else None
        
        # 收集所有篩選參數
        filters = {
            'species': request.args.get('species'),
            'sex': request.args.get('sex'),
            'status': request.args.get('status'),
            'shelter_id': request.args.get('shelter_id'),
            'owner_id': request.args.get('owner_id', type=int),
            'created_by': request.args.get('created_by', type=int),
            'source_type': request.args.get('source_type'),
            'region': request.args.get('region'),
            'min_age': request.args.get('min_age', type=int),
            'max_age': request.args.get('max_age', type=int),
            'q': request.args.get('q', '').strip(),
            'page': request.args.get('page', 1, type=int),
            'per_page': request.args.get('per_page', 20, type=int)
        }
        
        result = animal_service.list_animals(filters, current_user_id)
        return jsonify(result), 200
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'message': f'系統錯誤: {str(e)}'}), 500


@animals_bp.route('/<int:animal_id>', methods=['GET'])
def get_animal(animal_id):
    """取得單一動物詳細資訊"""
    try:
        animal = animal_service.get_animal(animal_id)
        return jsonify(animal.to_dict(include_relations=True)), 200
    except BusinessException as e:
        return jsonify({'message': str(e)}), e.status_code
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
