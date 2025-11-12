"""
Database Models - Medical Record
"""
from datetime import datetime
from app import db
from enum import Enum


class RecordType(str, Enum):
    """醫療紀錄類型枚舉"""
    TREATMENT = 'TREATMENT'
    CHECKUP = 'CHECKUP'
    VACCINE = 'VACCINE'
    SURGERY = 'SURGERY'
    OTHER = 'OTHER'


class MedicalRecord(db.Model):
    """醫療紀錄模型"""
    __tablename__ = 'medical_records'
    
    medical_record_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    animal_id = db.Column(db.BigInteger, db.ForeignKey('animals.animal_id'), nullable=False)
    record_type = db.Column(db.Enum(RecordType), nullable=True)
    date = db.Column(db.Date, nullable=True)
    provider = db.Column(db.String(255), nullable=True)
    details = db.Column(db.Text, nullable=True)
    attachments = db.Column(db.JSON, nullable=True)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    verified_by = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=True)
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(6), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime(6), nullable=True)
    
    # Relationships
    animal = db.relationship('Animal', back_populates='medical_records')
    verifier = db.relationship('User', foreign_keys=[verified_by])
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<MedicalRecord {self.medical_record_id} for Animal {self.animal_id}>'
    
    def to_dict(self, include_relations=False):
        """轉換為字典"""
        data = {
            'medical_record_id': self.medical_record_id,
            'animal_id': self.animal_id,
            'record_type': self.record_type.value if self.record_type else None,
            'date': self.date.isoformat() if self.date else None,
            'provider': self.provider,
            'details': self.details,
            'attachments': self.attachments,
            'verified': self.verified,
            'verified_by': self.verified_by,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            data['animal'] = self.animal.to_dict() if self.animal else None
            data['verifier'] = self.verifier.to_dict() if self.verifier else None
        
        return data
