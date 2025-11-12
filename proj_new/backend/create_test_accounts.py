"""
快速生成測試帳號腳本
使用方法: 
  - 本地運行: python create_test_accounts.py
  - Docker 環境: docker-compose exec backend python create_test_accounts.py
"""
import sys
import os
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User, UserRole
from app.models.shelter import Shelter
from app.utils.security import hash_password


def create_test_accounts():
    """建立測試帳號"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🚀 開始建立測試帳號...")
        print("=" * 60)
        print()
        
        # 定義測試帳號
        test_accounts = [
            {
                'email': 'admin@test.com',
                'username': 'admin',
                'password': 'Admin123',
                'role': UserRole.ADMIN,
                'verified': True,
                'first_name': '測試',
                'last_name': '管理員',
                'description': '管理員帳號 - 擁有所有權限'
            },
            {
                'email': 'shelter@test.com',
                'username': 'shelter_tester',
                'password': 'Shelter123',
                'role': UserRole.SHELTER_MEMBER,
                'verified': True,
                'first_name': '測試',
                'last_name': '收容所',
                'description': '收容所會員 - 可管理動物和申請',
                'create_shelter': True,
                'shelter_name': '測試收容所',
                'shelter_address': '台北市測試區測試路123號',
                'shelter_phone': '02-12345678'
            },
            {
                'email': 'user@test.com',
                'username': 'general_user',
                'password': 'User123',
                'role': UserRole.GENERAL_MEMBER,
                'verified': True,
                'first_name': '測試',
                'last_name': '用戶',
                'description': '一般會員 - 可瀏覽和申請領養'
            },
            {
                'email': 'user2@test.com',
                'username': 'general_user2',
                'password': 'User123',
                'role': UserRole.GENERAL_MEMBER,
                'verified': True,
                'first_name': '測試',
                'last_name': '用戶2',
                'description': '一般會員 2 - 額外測試帳號'
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for account_data in test_accounts:
            email = account_data['email']
            
            # 檢查帳號是否已存在
            existing_user = User.query.filter_by(email=email).first()
            
            if existing_user:
                print(f"⏭️  跳過: {email} (已存在)")
                print(f"   角色: {existing_user.role.value}")
                print(f"   驗證狀態: {'✅ 已驗證' if existing_user.verified else '❌ 未驗證'}")
                skipped_count += 1
                print()
                continue
            
            # 建立新用戶
            user = User(
                email=account_data['email'],
                username=account_data['username'],
                password_hash=hash_password(account_data['password']),
                role=account_data['role'],
                verified=account_data['verified'],
                first_name=account_data.get('first_name'),
                last_name=account_data.get('last_name'),
                failed_login_attempts=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(user)
            db.session.flush()
            
            # 如果是收容所會員，建立關聯收容所
            if account_data.get('create_shelter'):
                shelter = Shelter(
                    name=account_data['shelter_name'],
                    address={'street': account_data['shelter_address'], 'city': '台北市', 'county': '測試區', 'postal_code': '100'},
                    contact_phone=account_data['shelter_phone'],
                    contact_email=account_data['email'],
                    verified=True,
                    primary_account_user_id=user.user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(shelter)
                db.session.flush()
                
                user.primary_shelter_id = shelter.shelter_id
                
                print(f"✅ 建立: {email}")
                print(f"   使用者名稱: {account_data['username']}")
                print(f"   密碼: {account_data['password']}")
                print(f"   角色: {account_data['role'].value}")
                print(f"   描述: {account_data['description']}")
                print(f"   🏢 收容所: {shelter.name} (ID: {shelter.shelter_id})")
            else:
                print(f"✅ 建立: {email}")
                print(f"   使用者名稱: {account_data['username']}")
                print(f"   密碼: {account_data['password']}")
                print(f"   角色: {account_data['role'].value}")
                print(f"   描述: {account_data['description']}")
            
            created_count += 1
            print()
        
        # 提交所有變更
        try:
            db.session.commit()
            print("=" * 60)
            print("✅ 測試帳號建立完成!")
            print(f"   建立: {created_count} 個")
            print(f"   跳過: {skipped_count} 個")
            print("=" * 60)
            print()
            print("📋 測試帳號摘要:")
            print("-" * 60)
            print("角色             | Email                | 密碼")
            print("-" * 60)
            print("管理員           | admin@test.com       | Admin123")
            print("收容所會員       | shelter@test.com     | Shelter123")
            print("一般會員         | user@test.com        | User123")
            print("一般會員2        | user2@test.com       | User123")
            print("-" * 60)
            print()
            print("🌐 前端登入頁面: http://localhost:5173/login")
            print("📚 API 文檔: http://localhost:5000/api/docs")
            print()
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 錯誤: 建立帳號時發生錯誤")
            print(f"   {str(e)}")
            return False
        
        return True


if __name__ == '__main__':
    success = create_test_accounts()
    sys.exit(0 if success else 1)
