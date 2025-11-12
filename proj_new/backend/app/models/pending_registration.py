"""
Model: PendingRegistration
暫存註冊資料與驗證碼
"""
from datetime import datetime
from app import db


class PendingRegistration(db.Model):
    __tablename__ = 'pending_registrations'

    # use Integer primary key so SQLite in-memory tests auto-increment correctly
    pending_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(320), nullable=False, index=True)
    username = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(32), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    address = db.Column(db.JSON, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    verification_code_hash = db.Column(db.String(255), nullable=False)
    code_expires_at = db.Column(db.DateTime(6), nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    resend_count = db.Column(db.Integer, default=0, nullable=False)
    client_ip = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(1024), nullable=True)
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(6), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'pending_id': self.pending_id,
            'email': self.email,
            'username': self.username,
            'phone_number': self.phone_number,
            'region': self.region,
            'address': self.address,
            'code_expires_at': self.code_expires_at.isoformat() if self.code_expires_at else None,
            'attempts': self.attempts,
            'resend_count': self.resend_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
