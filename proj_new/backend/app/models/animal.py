"""
Database Models - Animal
"""
from datetime import datetime
from app import db
from enum import Enum


class Species(str, Enum):
    """動物物種枚舉"""
    CAT = 'CAT'
    DOG = 'DOG'


class Sex(str, Enum):
    """動物性別枚舉"""
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    UNKNOWN = 'UNKNOWN'


class AnimalStatus(str, Enum):
    """動物狀態枚舉"""
    DRAFT = 'DRAFT'  # 草稿
    SUBMITTED = 'SUBMITTED'  # 已提交審核
    PUBLISHED = 'PUBLISHED'  # 已發布
    ADOPTED = 'ADOPTED'  # 已被領養
    RETIRED = 'RETIRED'  # 已下架


class Animal(db.Model):
    """動物模型"""
    __tablename__ = 'animals'
    
    animal_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=True)
    species = db.Column(db.Enum(Species), nullable=True)
    breed = db.Column(db.String(200), nullable=True)
    color = db.Column(db.String(100), nullable=True)
    sex = db.Column(db.Enum(Sex), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(AnimalStatus), default=AnimalStatus.DRAFT, nullable=False)
    shelter_id = db.Column(db.BigInteger, db.ForeignKey('shelters.shelter_id'), nullable=True)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=True)
    medical_summary = db.Column(db.Text, nullable=True)
    
    # 拒絕批准相關欄位 (問題5)
    rejection_reason = db.Column(db.Text, nullable=True)
    rejected_at = db.Column(db.DateTime(6), nullable=True)
    rejected_by = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=True)
    
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(6), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime(6), nullable=True)
    
    # Relationships
    shelter = db.relationship('Shelter', back_populates='animals')
    owner = db.relationship('User', foreign_keys=[owner_id], back_populates='animals')
    creator = db.relationship('User', foreign_keys=[created_by])
    rejecter = db.relationship('User', foreign_keys=[rejected_by])
    images = db.relationship('AnimalImage', back_populates='animal', cascade='all, delete-orphan')
    applications = db.relationship('Application', back_populates='animal')
    medical_records = db.relationship('MedicalRecord', back_populates='animal')
    
    def __repr__(self):
        return f'<Animal {self.name} ({self.animal_id})>'
    
    @property
    def age(self):
        """計算動物年齡"""
        if self.dob:
            today = datetime.utcnow().date()
            age_years = today.year - self.dob.year
            if today.month < self.dob.month or (today.month == self.dob.month and today.day < self.dob.day):
                age_years -= 1
            return age_years
        return None
    
    def has_pending_application(self):
        """檢查是否有待審核的申請"""
        from app.models.application import Application, ApplicationStatus
        pending_app = Application.query.filter_by(
            animal_id=self.animal_id,
            deleted_at=None
        ).filter(
            Application.status.in_([ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW])
        ).first()
        return pending_app is not None
    
    def to_dict(self, include_relations=False):
        """轉換為字典"""
        data = {
            'animal_id': self.animal_id,
            'name': self.name,
            'species': self.species.value if self.species else None,
            'breed': self.breed,
            'color': self.color,
            'sex': self.sex.value if self.sex else None,
            'dob': self.dob.isoformat() if self.dob else None,
            'age': self.age,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'shelter_id': self.shelter_id,
            'owner_id': self.owner_id,
            'medical_summary': self.medical_summary,
            'rejection_reason': self.rejection_reason,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'rejected_by': self.rejected_by,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'has_pending_application': self.has_pending_application(),
            # 總是包含 images，確保前端有正確的圖片數組
            'images': [img.to_dict() for img in self.images] if hasattr(self, 'images') else []
        }
        
        if include_relations:
            data['shelter'] = self.shelter.to_dict() if self.shelter else None
        
        return data


class AnimalImage(db.Model):
    """動物圖片模型"""
    __tablename__ = 'animal_images'
    
    animal_image_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    animal_id = db.Column(db.BigInteger, db.ForeignKey('animals.animal_id'), nullable=False)
    storage_key = db.Column(db.String(1024), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    mime_type = db.Column(db.String(128), nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    
    # Relationships
    animal = db.relationship('Animal', back_populates='images')
    
    def __repr__(self):
        return f'<AnimalImage {self.animal_image_id} for Animal {self.animal_id}>'
    
    def to_dict(self):
        """轉換為字典"""
        from config import Config
        
        # 使用 storage_key 重新構建永久的公開 URL
        # 避免使用資料庫中可能過期的 presigned URL
        if self.storage_key:
            url = f"http://{Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000'}/{Config.MINIO_BUCKET}/{self.storage_key}"
        else:
            # 如果沒有 storage_key,嘗試轉換 URL (向後兼容)
            url = self.url
            if url and 'minio:9000' in url:
                url = url.replace('minio:9000', Config.MINIO_EXTERNAL_ENDPOINT or 'localhost:9000')
            # 移除可能過期的查詢參數
            if url and '?' in url:
                url = url.split('?')[0]
        
        return {
            'animal_image_id': self.animal_image_id,
            'animal_id': self.animal_id,
            'storage_key': self.storage_key,
            'url': url,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
