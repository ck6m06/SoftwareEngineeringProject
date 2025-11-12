"""
Jobs Blueprint - 背景任務 API
"""
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.others import Job, JobStatus
from app.models.user import User, UserRole
from app.services.notification_service import notification_service

jobs_bp = Blueprint('jobs', __name__, description='背景任務 API')


@jobs_bp.route('', methods=['GET'])
@jwt_required()
def list_jobs():
    """
    查詢任務列表
    支援過濾: type, status, created_by
    """
    current_user_id = int(get_jwt_identity())
    
    # 獲取查詢參數
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    job_type = request.args.get('type')
    status = request.args.get('status')
    created_by = request.args.get('created_by', type=int)
    
    # 限制 per_page
    per_page = min(per_page, 100)
    
    # 構建查詢 (延遲載入大型欄位以避免記憶體問題)
    from sqlalchemy.orm import defer
    query = Job.query.options(defer(Job.payload), defer(Job.result_summary))
    
    # 過濾條件
    if job_type:
        query = query.filter(Job.type == job_type)
    
    if status:
        try:
            status_enum = JobStatus(status)
            query = query.filter(Job.status == status_enum)
        except ValueError:
            abort(400, message=f'無效的狀態: {status}')
    
    # 普通用戶只能看到自己的任務
    user = User.query.get(current_user_id)
    if user and user.role != UserRole.ADMIN:
        query = query.filter(Job.created_by == current_user_id)
    elif created_by:
        # 管理員可以篩選特定用戶的任務
        query = query.filter(Job.created_by == created_by)
    
    # 排序並分頁
    query = query.order_by(Job.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'jobs': [job.to_dict() for job in pagination.items]
    }), 200


@jobs_bp.route('/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_status(job_id):
    """取得任務狀態"""
    current_user_id = int(get_jwt_identity())
    
    job = Job.query.get(job_id)
    if not job:
        abort(404, message='任務不存在')
    
    # 檢查權限 (只能查看自己的任務,管理員除外)
    user = User.query.get(current_user_id)
    if user and user.role != UserRole.ADMIN:
        if job.created_by != current_user_id:
            abort(403, message='無權限查看此任務')
    
    return jsonify(job.to_dict()), 200


@jobs_bp.route('/<int:job_id>/retry', methods=['POST'])
@jwt_required()
def retry_job(job_id):
    """
    重試失敗的任務
    僅創建者或管理員可操作
    """
    current_user_id = int(get_jwt_identity())
    
    job = Job.query.get(job_id)
    if not job:
        abort(404, message='任務不存在')
    
    # 檢查權限
    user = User.query.get(current_user_id)
    if user and user.role != UserRole.ADMIN:
        if job.created_by != current_user_id:
            abort(403, message='無權限操作此任務')
    
    # 只能重試失敗的任務
    if job.status != JobStatus.FAILED:
        abort(400, message='只能重試失敗的任務')
    
    # 更新任務狀態
    job.status = JobStatus.PENDING
    job.attempts += 1
    job.result_summary = None
    job.finished_at = None
    db.session.commit()
    
    # TODO: 重新加入 Celery 隊列
    # from app.tasks import retry_job_task
    # retry_job_task.delay(job_id)
    
    return jsonify({
        'message': '任務已重新加入隊列',
        'job': job.to_dict()
    }), 200


@jobs_bp.route('/<int:job_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_job(job_id):
    """
    取消待處理或運行中的任務
    僅創建者或管理員可操作
    """
    current_user_id = int(get_jwt_identity())
    
    job = Job.query.get(job_id)
    if not job:
        abort(404, message='任務不存在')
    
    # 檢查權限
    user = User.query.get(current_user_id)
    if user and user.role != UserRole.ADMIN:
        if job.created_by != current_user_id:
            abort(403, message='無權限操作此任務')
    
    # 只能取消待處理或運行中的任務
    if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
        abort(400, message='只能取消待處理或運行中的任務')
    
    # 更新任務狀態
    job.status = JobStatus.FAILED
    job.finished_at = datetime.utcnow()
    job.result_summary = {'error': '任務已被用戶取消'}
    db.session.commit()
    
    # TODO: 通知 Celery Worker 取消任務
    # from app.tasks import cancel_job_task
    # cancel_job_task.delay(job_id)
    
    return jsonify({
        'message': '任務已取消',
        'job': job.to_dict()
    }), 200


@jobs_bp.route('/<int:job_id>/approve', methods=['POST'])
@jwt_required()
def approve_job(job_id):
    """
    核准任務 (僅管理員)
    主要用於需要審核的任務，如帳號刪除請求
    """
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    # 檢查管理員權限
    if not user or user.role != UserRole.ADMIN:
        abort(403, message='僅管理員可執行此操作')
    
    job = Job.query.get(job_id)
    if not job:
        abort(404, message='任務不存在')
    
    # 只能核准待處理的任務
    if job.status != JobStatus.PENDING:
        abort(400, message='只能核准待處理的任務')
    
    data = request.get_json() or {}
    notes = data.get('notes', '')
    
    # 根據任務類型執行相應操作
    if job.type == 'user_data_deletion':
        # 帳號刪除請求
        user_id = job.payload.get('user_id')
        if user_id:
            target_user = User.query.get(user_id)
            if target_user:
                # 軟刪除用戶
                target_user.deleted_at = datetime.utcnow()
                
                # 記錄審計日誌
                from app.services.audit_service import audit_service
                audit_service.log(
                    action='user.deleted.approved',
                    actor_id=current_user_id,
                    target_type='user',
                    target_id=user_id,
                    after_state={'approved_by': current_user_id, 'notes': notes}
                )
    
    # 更新任務狀態
    job.status = JobStatus.SUCCEEDED
    job.finished_at = datetime.utcnow()
    job.result_summary = {
        'approved_by': current_user_id,
        'approved_at': datetime.utcnow().isoformat(),
        'notes': notes
    }
    
    db.session.commit()
    
    # 發送 Job 完成通知給建立者
    try:
        notification_service.notify_job_completed(job, 'SUCCEEDED')
    except Exception as notify_error:
        print(f'通知發送失敗: {notify_error}')
    
    return jsonify({
        'message': '任務已核准',
        'job': job.to_dict()
    }), 200


@jobs_bp.route('/<int:job_id>/reject', methods=['POST'])
@jwt_required()
def reject_job(job_id):
    """
    拒絕任務 (僅管理員)
    主要用於需要審核的任務，如帳號刪除請求
    """
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    # 檢查管理員權限
    if not user or user.role != UserRole.ADMIN:
        abort(403, message='僅管理員可執行此操作')
    
    job = Job.query.get(job_id)
    if not job:
        abort(404, message='任務不存在')
    
    # 只能拒絕待處理的任務
    if job.status != JobStatus.PENDING:
        abort(400, message='只能拒絕待處理的任務')
    
    data = request.get_json() or {}
    reason = data.get('reason', '管理員拒絕')
    
    # 更新任務狀態
    job.status = JobStatus.FAILED
    job.finished_at = datetime.utcnow()
    job.result_summary = {
        'rejected_by': current_user_id,
        'rejected_at': datetime.utcnow().isoformat(),
        'reason': reason
    }
    
    db.session.commit()
    
    # 記錄審計日誌
    from app.services.audit_service import audit_service
    audit_service.log(
        action='job.rejected',
        actor_id=current_user_id,
        target_type='job',
        target_id=job_id,
        after_state={'reason': reason}
    )
    
    # 發送 Job 完成通知給建立者
    try:
        notification_service.notify_job_completed(job, 'FAILED')
    except Exception as notify_error:
        print(f'通知發送失敗: {notify_error}')
    
    return jsonify({
        'message': '任務已拒絕',
        'job': job.to_dict()
    }), 200


