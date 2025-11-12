"""
Database Models - Notification, Job, Attachment, AuditLog
"""
from datetime import datetime
from app import db
from enum import Enum


class Notification(db.Model):
    """通知模型"""
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    recipient_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    actor_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=True)
    type = db.Column(db.String(128), nullable=False)
    payload = db.Column(db.JSON, nullable=True)
    read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    read_at = db.Column(db.DateTime(6), nullable=True)
    
    # Relationships
    recipient = db.relationship('User', foreign_keys=[recipient_id], back_populates='notifications')
    actor = db.relationship('User', foreign_keys=[actor_id])
    
    def __repr__(self):
        return f'<Notification {self.notification_id} to User {self.recipient_id}>'
    
    def to_dict(self):
        """轉換為字典"""
        return {
            'notification_id': self.notification_id,
            'recipient_id': self.recipient_id,
            'actor_id': self.actor_id,
            'type': self.type,
            'payload': self.payload,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
        }


class JobType(str, Enum):
    """工作類型枚舉"""
    IMPORT_ANIMALS = 'import_animals'
    EXPORT_USER_DATA = 'export_user_data'
    BATCH_NOTIFICATION = 'batch_notification'
    GENERATE_REPORT = 'generate_report'


class JobStatus(str, Enum):
    """工作狀態枚舉"""
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'


class Job(db.Model):
    """背景任務模型"""
    __tablename__ = 'jobs'
    
    job_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    type = db.Column(db.String(320), nullable=False)
    status = db.Column(db.Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    payload = db.Column(db.JSON, nullable=True)
    result_summary = db.Column(db.JSON, nullable=True)
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime(6), nullable=True)
    finished_at = db.Column(db.DateTime(6), nullable=True)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships
    creator = db.relationship('User', back_populates='created_jobs')
    
    def __repr__(self):
        return f'<Job {self.job_id} ({self.type})>'
    
    def to_dict(self):
        """轉換為字典"""
        from sqlalchemy.orm import object_session
        from sqlalchemy.inspection import inspect
        
        # 檢查屬性是否已載入
        state = inspect(self)
        
        result = {
            'job_id': self.job_id,
            'type': self.type,
            'status': self.status.value if self.status else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'attempts': self.attempts,
        }
        
        # 只在已載入時才加入 payload 和 result_summary
        if 'payload' not in state.unloaded:
            result['payload'] = self.payload
        if 'result_summary' not in state.unloaded:
            result['result_summary'] = self.result_summary
            
        return result


class Attachment(db.Model):
    """附件模型"""
    __tablename__ = 'attachments'
    
    attachment_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    owner_type = db.Column(db.String(64), nullable=False)
    owner_id = db.Column(db.BigInteger, nullable=False)
    storage_key = db.Column(db.String(1024), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    filename = db.Column(db.String(1024), nullable=True)
    mime_type = db.Column(db.String(128), nullable=True)
    size = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime(6), nullable=True)
    
    # Relationships
    creator = db.relationship('User')
    
    def __repr__(self):
        return f'<Attachment {self.attachment_id} ({self.owner_type}:{self.owner_id})>'
    
    def to_dict(self):
        """轉換為字典"""
        return {
            'attachment_id': self.attachment_id,
            'owner_type': self.owner_type,
            'owner_id': self.owner_id,
            'storage_key': self.storage_key,
            'url': self.url,
            'filename': self.filename,
            'mime_type': self.mime_type,
            'size': self.size,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(db.Model):
    """審計日誌模型"""
    __tablename__ = 'audit_logs'
    
    audit_log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    actor_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=True)
    action = db.Column(db.String(150), nullable=False)
    target_type = db.Column(db.String(128), nullable=True)
    target_id = db.Column(db.BigInteger, nullable=True)
    shelter_id = db.Column(db.BigInteger, db.ForeignKey('shelters.shelter_id'), nullable=True)
    before_state = db.Column(db.JSON, nullable=True)
    after_state = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    
    # Relationships
    actor = db.relationship('User', back_populates='audit_logs')
    shelter = db.relationship('Shelter')
    
    def __repr__(self):
        return f'<AuditLog {self.audit_log_id} ({self.action})>'
    
    def to_dict(self):
        """轉換為字典"""
        return {
            'audit_log_id': self.audit_log_id,
            'actor_id': self.actor_id,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'shelter_id': self.shelter_id,
            'before_state': self.before_state,
            'after_state': self.after_state,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
