"""
Database Models - Application
"""
from datetime import datetime
from app import db
from enum import Enum


class ApplicationType(str, Enum):
    """申請類型枚舉"""
    ADOPTION = 'ADOPTION'
    REHOME = 'REHOME'


class ApplicationStatus(str, Enum):
    """申請狀態枚舉"""
    PENDING = 'PENDING'
    UNDER_REVIEW = 'UNDER_REVIEW'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    WITHDRAWN = 'WITHDRAWN'


class Application(db.Model):
    """領養申請模型"""
    __tablename__ = 'applications'
    
    application_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    applicant_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    animal_id = db.Column(db.BigInteger, db.ForeignKey('animals.animal_id'), nullable=False)
    type = db.Column(db.Enum(ApplicationType), nullable=False)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    submitted_at = db.Column(db.DateTime(6), nullable=True)
    reviewed_at = db.Column(db.DateTime(6), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    assignee_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=True)
    version = db.Column(db.Integer, default=1, nullable=False)  # Optimistic locking
    idempotency_key = db.Column(db.String(255), unique=True, nullable=True, index=True)
    attachments = db.Column(db.JSON, nullable=True)
    
    # 申請人詳細資料 (新增欄位)
    contact_phone = db.Column(db.String(32), nullable=True)
    contact_address = db.Column(db.String(500), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    housing_type = db.Column(db.String(50), nullable=True)  # 例: 公寓、透天厝、獨棟
    has_experience = db.Column(db.Boolean, default=False, nullable=True)
    reason = db.Column(db.Text, nullable=True)  # 領養原因
    notes = db.Column(db.Text, nullable=True)  # 其他備註
    
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(6), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime(6), nullable=True)
    
    # Relationships
    applicant = db.relationship('User', foreign_keys=[applicant_id], back_populates='applications')
    animal = db.relationship('Animal', back_populates='applications')
    assignee = db.relationship('User', foreign_keys=[assignee_id])
    
    def __repr__(self):
        return f'<Application {self.application_id} by User {self.applicant_id} for Animal {self.animal_id}>'
    
    def to_dict(self, include_relations=False):
        """轉換為字典"""
        data = {
            'application_id': self.application_id,
            'applicant_id': self.applicant_id,
            'animal_id': self.animal_id,
            'type': self.type.value if self.type else None,
            'status': self.status.value if self.status else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_notes': self.review_notes,
            'assignee_id': self.assignee_id,
            'version': self.version,
            'attachments': self.attachments,
            # 申請人詳細資料
            'contact_phone': self.contact_phone,
            'contact_address': self.contact_address,
            'occupation': self.occupation,
            'housing_type': self.housing_type,
            'has_experience': self.has_experience,
            'reason': self.reason,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            data['applicant'] = self.applicant.to_dict() if self.applicant else None
            data['animal'] = self.animal.to_dict(include_relations=True) if self.animal else None
            data['assignee'] = self.assignee.to_dict() if self.assignee else None
        
        return data
