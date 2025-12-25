"""
共用測試配置和 Fixtures
用於單元測試和整合測試
"""
import pytest
from app import create_app, db
from app.models.user import User, UserRole
from app.models.shelter import Shelter
from app.models.animal import Animal, Species, Sex, AnimalStatus
from datetime import datetime


@pytest.fixture(scope='session')
def app():
    """創建測試用的 Flask 應用實例"""
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def client(app):
    """創建測試客戶端"""
    return app.test_client()


@pytest.fixture(scope='function')
def app_context(app):
    """創建應用上下文"""
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db_session(app_context):
    """
    創建資料庫會話
    每個測試函數執行前建立，執行後回滾
    """
    db.create_all()
    yield db.session
    db.session.rollback()
    db.drop_all()


@pytest.fixture
def test_admin(db_session):
    """創建測試管理員"""
    admin = User(
        email='admin@test.com',
        username='testadmin',
        password_hash='hashed_password',
        role=UserRole.ADMIN,
        verified=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def test_user(db_session):
    """創建測試一般用戶"""
    from app.utils.security import hash_password
    user = User(
        email='user@test.com',
        username='testuser',
        password_hash=hash_password('Password123'),
        role=UserRole.GENERAL_MEMBER,
        verified=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_shelter_member(db_session):
    """創建測試收容所會員"""
    shelter_member = User(
        email='shelter@test.com',
        username='shelteruser',
        password_hash='hashed_password',
        role=UserRole.SHELTER_MEMBER,
        verified=True
    )
    db_session.add(shelter_member)
    db_session.commit()
    return shelter_member


@pytest.fixture
def test_shelter(db_session, test_shelter_member):
    """創建測試收容所"""
    shelter = Shelter(
        shelter_id=1,  # 手動設置 ID（SQLite BIGINT 不會自動遞增）
        name='Test Shelter',
        slug='test-shelter',
        contact_email='shelter@test.com',
        contact_phone='0912345678',
        address={
            'street': '123 Test St',
            'city': 'Test City',
            'county': 'Test County',
            'postal_code': '12345'
        },
        region='北部',
        primary_account_user_id=test_shelter_member.user_id,
        verified=True
    )
    db_session.add(shelter)
    db_session.commit()
    
    # 設定收容所會員的 primary_shelter_id
    test_shelter_member.primary_shelter_id = shelter.shelter_id
    db_session.commit()
    
    return shelter


@pytest.fixture
def test_animal(db_session, test_user):
    """創建測試動物（個人送養）"""
    from datetime import date
    animal = Animal(
        animal_id=1,  # 手動設置 ID（SQLite BIGINT 不會自動遞增）
        name='Test Dog',
        species=Species.DOG,
        breed='Mixed',
        sex=Sex.MALE,
        dob=date(2022, 1, 1),
        description='A friendly test dog',
        status=AnimalStatus.PUBLISHED,
        owner_id=test_user.user_id,
        created_by=test_user.user_id,
        shelter_id=None
    )
    db_session.add(animal)
    db_session.commit()
    return animal


@pytest.fixture
def test_shelter_animal(db_session, test_shelter, test_shelter_member):
    """創建測試動物（收容所送養）"""
    from datetime import date
    animal = Animal(
        animal_id=2,  # 手動設置 ID（避免與 test_animal 衝突）
        name='Shelter Cat',
        species=Species.CAT,
        breed='Persian',
        sex=Sex.FEMALE,
        dob=date(2023, 6, 1),
        description='A lovely shelter cat',
        status=AnimalStatus.PUBLISHED,
        owner_id=None,
        created_by=test_shelter_member.user_id,
        shelter_id=test_shelter.shelter_id
    )
    db_session.add(animal)
    db_session.commit()
    return animal


@pytest.fixture
def auth_headers(client, test_user):
    """
    生成認證 Headers
    返回包含 JWT token 的 headers 字典
    """
    # 這裡需要實際登入來獲取 token
    # 簡化版本，實際使用時需要調用登入 API
    from flask_jwt_extended import create_access_token
    
    access_token = create_access_token(identity=test_user.user_id)
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def admin_headers(client, test_admin):
    """生成管理員認證 Headers"""
    from flask_jwt_extended import create_access_token
    
    access_token = create_access_token(identity=test_admin.user_id)
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def shelter_member_headers(client, test_shelter_member):
    """生成收容所會員認證 Headers"""
    from flask_jwt_extended import create_access_token
    
    access_token = create_access_token(identity=test_shelter_member.user_id)
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
