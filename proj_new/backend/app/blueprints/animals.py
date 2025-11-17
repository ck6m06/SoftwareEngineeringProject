"""
Animals Blueprint - 動物相關 API (精簡控制器)
"""
from flask import request, jsonify
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.animal_service import AnimalService
from app.decorators.role_decorators import role_required
from app.schemas import AnimalCreateSchema, AnimalUpdateSchema

animals_bp = Blueprint('animals', __name__, description='動物管理 API')


@animals_bp.route('', methods=['GET'])
def list_animals():
    """
    取得動物列表 (支援搜尋與篩選)
    """
    try:
        # 收集查詢參數
        filters = {
            'page': request.args.get('page', 1, type=int),
            'per_page': min(request.args.get('per_page', 20, type=int), 100),
            'species': request.args.get('species'),
            'sex': request.args.get('sex'),
            'status': request.args.get('status'),
            'shelter_id': request.args.get('shelter_id', type=int),
            'owner_id': request.args.get('owner_id', type=int),
            'created_by': request.args.get('created_by', type=int),
            'source_type': request.args.get('source_type'),
            'region': request.args.get('region'),
            'min_age': request.args.get('min_age', type=int),
            'max_age': request.args.get('max_age', type=int),
            'q': request.args.get('q', '').strip()
        }
        
        # 移除空值參數
        filters = {k: v for k, v in filters.items() if v not in [None, '']}
        
        # 獲取當前用戶身份（如果有）
        current_user_id = None
        try:
            current_user_id = get_jwt_identity()
        except:
            pass  # 未登入狀態
        
        # 調用服務層處理業務邏輯
        result = AnimalService.search_animals(filters, current_user_id)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@animals_bp.route('/<animal_id>', methods=['GET'])
def get_animal(animal_id):
    """
    取得特定動物詳情
    """
    try:
        animal = AnimalService.get_animal_by_id(animal_id)
        return jsonify(animal), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@animals_bp.route('', methods=['POST'])
@jwt_required()
def create_animal():
    """
    創建新動物
    """
    try:
        # 資料驗證
        schema = AnimalCreateSchema()
        data = schema.load(request.get_json())
        
        # 調用服務層
        user_id = get_jwt_identity()
        animal = AnimalService.create_animal(data, user_id)
        
        return jsonify(animal), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@animals_bp.route('/<animal_id>', methods=['PUT'])
@jwt_required()
def update_animal(animal_id):
    """
    更新動物資料
    """
    try:
        # 資料驗證
        schema = AnimalUpdateSchema()
        data = schema.load(request.get_json())
        
        # 調用服務層
        user_id = get_jwt_identity()
        animal = AnimalService.update_animal(animal_id, data, user_id)
        
        return jsonify(animal), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@animals_bp.route('/<animal_id>', methods=['DELETE'])
@jwt_required()
def delete_animal(animal_id):
    """
    刪除動物 (軟刪除)
    """
    try:
        user_id = get_jwt_identity()
        AnimalService.delete_animal(animal_id, user_id)
        
        return jsonify({'message': 'Animal deleted successfully'}), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@animals_bp.route('/<animal_id>/status', methods=['PUT'])
@jwt_required()
def update_animal_status(animal_id):
    """
    更新動物狀態 (發布/下架/等)
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
        animal = AnimalService.update_animal_status(animal_id, status, user_id, notes)
        
        return jsonify(animal), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@animals_bp.route('/<animal_id>/publish', methods=['POST'])
@jwt_required()
def publish_animal(animal_id):
    """
    發布動物 (設置狀態為 PUBLISHED)
    """
    try:
        user_id = get_jwt_identity()
        animal = AnimalService.update_animal_status(animal_id, 'PUBLISHED', user_id)
        return jsonify({
            'message': '動物已成功發布',
            'animal': animal
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@animals_bp.route('/<animal_id>/retire', methods=['POST'])
@jwt_required()
def retire_animal(animal_id):
    """
    下架動物 (設置狀態為 RETIRED)
    """
    try:
        user_id = get_jwt_identity()
        animal = AnimalService.update_animal_status(animal_id, 'RETIRED', user_id)
        return jsonify({
            'message': '動物已成功下架',
            'animal': animal
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@animals_bp.route('/<animal_id>/submit', methods=['POST'])
@jwt_required()
def submit_animal(animal_id):
    """
    提交動物審核 (設置狀態為 SUBMITTED)
    """
    try:
        user_id = get_jwt_identity()
        animal = AnimalService.update_animal_status(animal_id, 'SUBMITTED', user_id)
        return jsonify({
            'message': '動物已提交審核',
            'animal': animal
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@animals_bp.route('/<animal_id>/reject', methods=['POST'])
@jwt_required()
def reject_animal(animal_id):
    """
    拒絕動物審核 (設置狀態為 DRAFT 並記錄原因)
    """
    try:
        data = request.get_json()
        rejection_reason = data.get('rejectionReason', '未指定原因') if data else '未指定原因'
        
        user_id = get_jwt_identity()
        animal = AnimalService.update_animal_status(animal_id, 'DRAFT', user_id, rejection_reason)
        return jsonify({
            'message': '動物審核已拒絕',
            'animal': animal
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500