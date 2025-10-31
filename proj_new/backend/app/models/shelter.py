"""
Database Models - Shelter
"""
from datetime import datetime
from app import db


class Shelter(db.Model):
    """收容所模型"""
    __tablename__ = 'shelters'
    
    shelter_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=True, index=True)
    contact_email = db.Column(db.String(320), nullable=False)
    contact_phone = db.Column(db.String(32), nullable=False)
    address = db.Column(db.JSON, nullable=False)  # {street, city, county, postal_code}
    region = db.Column(db.String(100), nullable=True)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    primary_account_user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(6), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime(6), nullable=True)
    
    # Relationships
    primary_account = db.relationship('User', foreign_keys=[primary_account_user_id], back_populates='managed_shelters')
    primary_users = db.relationship('User', foreign_keys='User.primary_shelter_id', back_populates='primary_shelter')
    animals = db.relationship('Animal', back_populates='shelter')
    
    def __repr__(self):
        return f'<Shelter {self.name}>'
    
    def to_dict(self):
        """轉換為字典"""
        return {
            'shelter_id': self.shelter_id,
            'name': self.name,
            'slug': self.slug,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'address': self.address,
            'region': self.region,
            'verified': self.verified,
            'primary_account_user_id': self.primary_account_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
