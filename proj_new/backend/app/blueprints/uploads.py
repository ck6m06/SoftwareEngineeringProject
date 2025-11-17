"""
Uploads Blueprint - 檔案上傳 API
"""
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.upload_service import UploadService

uploads_bp = Blueprint('uploads', __name__, description='檔案上傳 API')


@uploads_bp.route('/direct', methods=['POST'])
@jwt_required()
def upload_direct():
    """
    直接上傳檔案 (後端代理)
    解決 presigned URL 的 CORS 和簽名問題
    前端直接將檔案發送到此 endpoint,後端負責上傳到 MinIO
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 檢查是否有檔案
        if 'file' not in request.files:
            abort(400, message='缺少檔案')
        
        file = request.files['file']
        
        result = UploadService.upload_direct(
            user_id=current_user_id,
            file_data=file
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@uploads_bp.route('/attachments', methods=['POST'])
@jwt_required()
def create_attachment():
    """
    建立附件記錄
    上傳完成後建立元數據
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            abort(400, message='缺少請求資料')
        
        result = UploadService.create_attachment(
            user_id=current_user_id,
            data=data
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        if '檔案不存在於儲存系統' in str(e):
            abort(404, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@uploads_bp.route('/attachments', methods=['GET'])
@jwt_required()
def list_attachments():
    """
    獲取用戶附件列表
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # 獲取篩選參數
        filters = {
            'entity_type': request.args.get('entity_type'),
            'entity_id': request.args.get('entity_id', type=int)
        }
        
        # 移除空值
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result = UploadService.list_user_attachments(
            user_id=current_user_id,
            filters=filters
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@uploads_bp.route('/attachments/<int:attachment_id>', methods=['GET'])
@jwt_required()
def get_attachment(attachment_id):
    """
    取得附件資訊及下載 URL
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = UploadService.get_attachment(
            user_id=current_user_id,
            attachment_id=attachment_id
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '附件不存在' in str(e):
            abort(404, message=str(e))
        elif '無權限' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@uploads_bp.route('/attachments/<int:attachment_id>', methods=['DELETE'])
@jwt_required()
def delete_attachment(attachment_id):
    """
    刪除附件
    軟刪除，實際檔案保留在 MinIO
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = UploadService.delete_attachment(
            user_id=current_user_id,
            attachment_id=attachment_id
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        if '附件不存在' in str(e):
            abort(404, message=str(e))
        elif '無權限' in str(e):
            abort(403, message=str(e))
        else:
            abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))


@uploads_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_upload_stats():
    """
    獲取用戶上傳統計
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        result = UploadService.get_upload_stats(current_user_id)
        
        return jsonify(result), 200
        
    except ValueError as e:
        abort(400, message=str(e))
    except RuntimeError as e:
        abort(500, message=str(e))
