#!/usr/bin/env python3
"""建立測試管理員帳號"""
import bcrypt
from app import create_app, db
from app.models import User, UserRole

app = create_app()

with app.app_context():
    # 檢查是否已存在
    existing = User.query.filter_by(email='admin@test.com').first()
    if existing:
        # 更新密碼
        password_hash = bcrypt.hashpw(b'Admin123', bcrypt.gensalt()).decode('utf-8')
        existing.password_hash = password_hash
        existing.role = UserRole.ADMIN
        existing.verified = True
        db.session.commit()
        print(f"✅ 更新現有帳號: {existing.email} (ID: {existing.user_id})")
        print(f"   角色: {existing.role.value}")
        print(f"   密碼: Admin123")
    else:
        # 建立新帳號
        password_hash = bcrypt.hashpw(b'Admin123', bcrypt.gensalt()).decode('utf-8')
        admin = User(
            email='admin@test.com',
            username='admin',
            password_hash=password_hash,
            role=UserRole.ADMIN,
            verified=True,
            failed_login_attempts=0
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ 建立新管理員帳號: {admin.email} (ID: {admin.user_id})")
        print(f"   角色: {admin.role.value}")
        print(f"   密碼: Admin123")
