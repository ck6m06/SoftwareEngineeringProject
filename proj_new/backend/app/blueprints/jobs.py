"""
Jobs Blueprint - 背景任務 API
"""
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.job_service import JobService

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
        
        # 獲取查詢參數
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        filters = {
            'type': request.args.get('type'),
            'status': request.args.get('status'),
            'created_by': request.args.get('created_by', type=int)
        }
        
        # 移除空值
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result = JobService.list_jobs(
            user_id=current_user_id,
            page=page,
            per_page=per_page,
            filters=filters
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@jobs_bp.route('/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_status(job_id):
    """取得任務狀態"""
    try:
        current_user_id = int(get_jwt_identity())
        
        result = JobService.get_job(current_user_id, job_id)
        return jsonify(result), 200
        
    except ValueError as e:
        if '任務不存在' in str(e):
            abort(404, message=str(e))
        elif '無權限' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@jobs_bp.route('/<int:job_id>/retry', methods=['POST'])
@jwt_required()
def retry_job(job_id):
    """
    重試失敗的任務
    僅創建者或管理員可操作
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = JobService.retry_job(current_user_id, job_id)
        return jsonify(result), 200
        
    except ValueError as e:
        if '任務不存在' in str(e):
            abort(404, message=str(e))
        elif '無權限' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@jobs_bp.route('/<int:job_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_job(job_id):
    """
    取消待處理或運行中的任務
    僅創建者或管理員可操作
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = JobService.cancel_job(current_user_id, job_id)
        return jsonify(result), 200
        
    except ValueError as e:
        if '任務不存在' in str(e):
            abort(404, message=str(e))
        elif '無權限' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


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
        
        result = JobService.approve_job(current_user_id, job_id, notes)
        return jsonify(result), 200
        
    except ValueError as e:
        if '任務不存在' in str(e):
            abort(404, message=str(e))
        elif '僅管理員' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


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
        
        result = JobService.reject_job(current_user_id, job_id, reason)
        return jsonify(result), 200
        
    except ValueError as e:
        if '任務不存在' in str(e):
            abort(404, message=str(e))
        elif '僅管理員' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))