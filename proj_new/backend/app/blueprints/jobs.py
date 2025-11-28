"""
Jobs Blueprint - 背景任務 API
"""
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.job_service import job_service
from app.exceptions import (
    NotFoundError, PermissionDeniedError, ValidationError
)

jobs_bp = Blueprint('jobs', __name__, description='背景任務 API')


@jobs_bp.route('', methods=['GET'])
@jwt_required()
def list_jobs():
    """
    查詢任務列表
    支援過濾: type, status, created_by
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        filters = {
            'page': request.args.get('page', 1, type=int),
            'per_page': request.args.get('per_page', 20, type=int),
            'type': request.args.get('type'),
            'status': request.args.get('status'),
            'created_by': request.args.get('created_by', type=int)
        }
        
        result = job_service.list_jobs(current_user_id, filters)
        return jsonify(result), 200
    except ValidationError as e:
        abort(400, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_status(job_id):
    """取得任務狀態"""
    try:
        current_user_id = int(get_jwt_identity())
        job = job_service.get_job(job_id, current_user_id)
        return jsonify(job.to_dict()), 200
    except NotFoundError as e:
        abort(404, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/<int:job_id>/retry', methods=['POST'])
@jwt_required()
def retry_job(job_id):
    """
    重試失敗的任務
    僅創建者或管理員可操作
    """
    try:
        current_user_id = int(get_jwt_identity())
        job = job_service.retry_job(job_id, current_user_id)
        
        return jsonify({
            'message': '任務已重新加入隊列',
            'job': job.to_dict()
        }), 200
    except NotFoundError as e:
        abort(404, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except ValidationError as e:
        abort(400, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/<int:job_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_job(job_id):
    """
    取消待處理或運行中的任務
    僅創建者或管理員可操作
    """
    try:
        current_user_id = int(get_jwt_identity())
        job = job_service.cancel_job(job_id, current_user_id)
        
        return jsonify({
            'message': '任務已取消',
            'job': job.to_dict()
        }), 200
    except NotFoundError as e:
        abort(404, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except ValidationError as e:
        abort(400, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/<int:job_id>/approve', methods=['POST'])
@jwt_required()
def approve_job(job_id):
    """
    核准任務 (僅管理員)
    主要用於需要審核的任務，如帳號刪除請求
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        notes = data.get('notes', '')
        
        job = job_service.approve_job(job_id, current_user_id, notes)
        
        return jsonify({
            'message': '任務已核准',
            'job': job.to_dict()
        }), 200
    except NotFoundError as e:
        abort(404, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except ValidationError as e:
        abort(400, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/<int:job_id>/reject', methods=['POST'])
@jwt_required()
def reject_job(job_id):
    """
    拒絕任務 (僅管理員)
    主要用於需要審核的任務，如帳號刪除請求
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        reason = data.get('reason', '管理員拒絕')
        
        job = job_service.reject_job(job_id, current_user_id, reason)
        
        return jsonify({
            'message': '任務已拒絕',
            'job': job.to_dict()
        }), 200
    except NotFoundError as e:
        abort(404, message=str(e))
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except ValidationError as e:
        abort(400, message=str(e))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


