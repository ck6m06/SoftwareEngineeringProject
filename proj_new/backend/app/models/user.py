"""
Database Models - User
"""
from datetime import datetime
from app import db
from enum import Enum


class UserRole(str, Enum):
    """使用者角色枚舉"""
    GENERAL_MEMBER = 'GENERAL_MEMBER'
    SHELTER_MEMBER = 'SHELTER_MEMBER'
    ADMIN = 'ADMIN'


class User(db.Model):
    """使用者模型"""
    __tablename__ = 'users'
    
    # Use Integer primary key to ensure SQLite in-memory tests auto-increment the id
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(320), unique=True, nullable=False, index=True)
    username = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(32), nullable=True)
    first_name = db.Column(db.String(120), nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    address = db.Column(db.JSON, nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.GENERAL_MEMBER, nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    primary_shelter_id = db.Column(db.BigInteger, db.ForeignKey('shelters.shelter_id'), nullable=True)
    profile_photo_url = db.Column(db.String(1024), nullable=True)
    settings = db.Column(db.JSON, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    password_changed_at = db.Column(db.DateTime(6), nullable=True)
    last_login_at = db.Column(db.DateTime(6), nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime(6), nullable=True)
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(6), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime(6), nullable=True)
    
    # Relationships
    primary_shelter = db.relationship('Shelter', foreign_keys=[primary_shelter_id], back_populates='primary_users')
    managed_shelters = db.relationship('Shelter', foreign_keys='Shelter.primary_account_user_id', back_populates='primary_account')
    animals = db.relationship('Animal', foreign_keys='Animal.owner_id', back_populates='owner')
    applications = db.relationship('Application', foreign_keys='Application.applicant_id', back_populates='applicant')
    notifications = db.relationship('Notification', foreign_keys='Notification.recipient_id', back_populates='recipient')
    created_jobs = db.relationship('Job', foreign_keys='Job.created_by', back_populates='creator')
    audit_logs = db.relationship('AuditLog', foreign_keys='AuditLog.actor_id', back_populates='actor')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def is_admin(self):
        """檢查是否為管理員"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_shelter_member(self):
        """檢查是否為收容所會員"""
        return self.role == UserRole.SHELTER_MEMBER
    
    @property
    def is_general_member(self):
        """檢查是否為一般會員"""
        return self.role == UserRole.GENERAL_MEMBER
    
    @property
    def is_locked(self):
        """檢查帳號是否被鎖定"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def to_dict(self, include_sensitive=False):
        """轉換為字典"""
        data = {
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username,
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'region': self.region,
            'address': self.address,
            'role': self.role.value if self.role else None,
            'verified': self.verified,
            'primary_shelter_id': self.primary_shelter_id,
            'profile_photo_url': self.profile_photo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            data.update({
                'settings': self.settings,
                'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
                'failed_login_attempts': self.failed_login_attempts,
            })
        
        return data
