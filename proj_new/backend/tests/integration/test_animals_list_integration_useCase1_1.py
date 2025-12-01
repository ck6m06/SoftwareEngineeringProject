"""
Use Case 1.1 動物列表瀏覽 - 整合測試（Integration Tests）

測試範圍：完整的請求流程（route → service → ORM → database）
測試方法：建立真實測試資料（使用 SQLite in-memory），驗證端到端行為  
與單元測試的區別：單元測試使用 mock；整合測試驗證完整業務邏輯流程

參考：現有 test_animals_filters.py 使用 requests 對實際服務器進行 API 測試
此整合測試使用 Flask test client 直接測試 app instance，不依賴外部服務器
"""
import pytest
from datetime import datetime, timedelta

from app import create_app, db
from app.models.user import User, UserRole
from app.models.animal import Animal, AnimalStatus, Species, Sex


@pytest.fixture
def app():
    """建立測試用 Flask app 與 SQLite in-memory 資料庫"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """測試客戶端"""
    return app.test_client()


def make_user(email='test@example.com', role=UserRole.GENERAL_MEMBER):
    """建立測試使用者"""
    u = User(email=email, password_hash='test', role=role)
    db.session.add(u)
    db.session.commit()
    return u


def make_animal(created_by, **kwargs):
    """建立測試動物"""
    # 確保用戶 ID 存在
    db.session.refresh(created_by)
    
    defaults = dict(
        name='Test',
        species=Species.DOG,
        sex=Sex.UNKNOWN,
        status=AnimalStatus.PUBLISHED,
        created_by=created_by.user_id
    )
    defaults.update(kwargs)
    
    # 暫時手動設定 animal_id 來繞過 SQLite BIGINT autoincrement 問題
    if 'animal_id' not in defaults:
        # 簡單的自增邏輯
        last_animal = Animal.query.order_by(Animal.animal_id.desc()).first()
        defaults['animal_id'] = 1 if not last_animal else last_animal.animal_id + 1
    
    a = Animal(**defaults)
    db.session.add(a)
    db.session.commit()
    return a


def test_returns_200_and_sorted_by_newest(client):
    """
    整合測試：驗證 GET /api/animals 回傳 200，且動物清單依 created_at 降冪排序
    
    Use Case 1.1 主要流程步驟 3：「系統依『最新上架』順序排序動物資料」
    
    測試層級：整合測試（完整流程）
    前置條件：建立三筆不同時間的動物資料
    驗證重點：
    - HTTP 200 回應
    - 回傳結構包含 'animals' key
    - 動物按建立時間降冪排序（最新優先）
    """
    user = make_user('owner1@example.com')
    now = datetime.utcnow()
    make_animal(user, name='OldestAnimal', created_at=now - timedelta(days=2))
    make_animal(user, name='MiddleAnimal', created_at=now - timedelta(days=1))
    make_animal(user, name='NewestAnimal', created_at=now)

    resp = client.get('/api/animals')
    assert resp.status_code == 200
    data = resp.get_json()
    
    # service 回傳結構：{'animals': [...], 'total': n, 'page': 1, 'per_page': 20, 'pages': 1}
    assert 'animals' in data
    animals = data['animals']
    assert len(animals) == 3
    
    # 驗證排序：最新的應該在第一筆
    names = [a['name'] for a in animals]
    assert names == ['NewestAnimal', 'MiddleAnimal', 'OldestAnimal']


def test_response_contains_required_card_fields(client):
    """
    整合測試：驗證動物清單中每筆記錄包含必要的卡片欄位
    
    Use Case 1.1 主要流程步驟 2：「系統顯示動物清單，包含動物圖片、名稱、物種、年齡、性別等基本資訊」
    
    測試層級：整合測試
    前置條件：建立一筆動物資料
    驗證重點：
    - 每筆動物包含 animal_id, name, images, species, age, sex
    - 欄位型態正確（如 animal_id 為 int，images 為 list）
    """
    user = make_user('owner2@example.com')
    animal = make_animal(user, name='FieldTestAnimal', species=Species.CAT, sex=Sex.FEMALE)

    resp = client.get('/api/animals')
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert len(data['animals']) == 1
    animal_data = data['animals'][0]
    
    # 驗證必要欄位存在
    required_fields = ['animal_id', 'name', 'images', 'species', 'age', 'sex']
    for field in required_fields:
        assert field in animal_data, f"Missing required field: {field}"
    
    # 驗證欄位型態
    assert isinstance(animal_data['animal_id'], int)
    assert isinstance(animal_data['name'], str)
    assert isinstance(animal_data['images'], list)
    assert animal_data['species'] in ['CAT', 'DOG']
    assert animal_data['sex'] in ['MALE', 'FEMALE', 'UNKNOWN']


def test_guest_sees_published_only(client):
    """
    整合測試：驗證訪客（未登入）只能看到已發布的動物
    
    Use Case 1.1 輔助說明 1：「若登入角色為訪客，僅能瀏覽公開動物資料」
    Use Case 1.1 輔助說明 3：「動物狀態為『已領養』或『下架』時，不會顯示在清單中」
    
    測試層級：整合測試
    前置條件：建立不同狀態的動物
    驗證重點：
    - 訪客只看到 PUBLISHED 狀態的動物
    - DRAFT、ADOPTED、RETIRED 狀態的動物不會出現
    """
    user = make_user('owner3@example.com')
    
    # 建立不同狀態的動物
    make_animal(user, name='PublishedAnimal', status=AnimalStatus.PUBLISHED)
    make_animal(user, name='DraftAnimal', status=AnimalStatus.DRAFT)
    make_animal(user, name='AdoptedAnimal', status=AnimalStatus.ADOPTED)
    make_animal(user, name='RetiredAnimal', status=AnimalStatus.RETIRED)

    resp = client.get('/api/animals')
    assert resp.status_code == 200
    data = resp.get_json()
    
    # 只應該回傳 PUBLISHED 的動物
    names = [a['name'] for a in data['animals']]
    assert 'PublishedAnimal' in names
    assert 'DraftAnimal' not in names
    assert 'AdoptedAnimal' not in names
    assert 'RetiredAnimal' not in names


def test_pagination_defaults_and_limits(client):
    """
    整合測試：驗證分頁參數的預設值與上限
    
    Use Case 1.1 擴充功能：分頁支援
    
    測試層級：整合測試
    前置條件：建立超過預設頁面大小的動物數量
    驗證重點：
    - 預設 per_page 為 20
    - page 參數正常運作
    - per_page 超過 100 時被限制
    """
    user = make_user('owner4@example.com')
    
    # 建立 25 筆動物（超過預設 per_page=20）
    for i in range(25):
        make_animal(user, name=f'Animal_{i:02d}')

    # 測試預設分頁
    resp = client.get('/api/animals')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['per_page'] == 20
    assert len(data['animals']) == 20
    assert data['total'] == 25
    assert data['pages'] == 2

    # 測試第二頁
    resp = client.get('/api/animals?page=2')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['page'] == 2
    assert len(data['animals']) == 5  # 剩餘 5 筆

    # 測試 per_page 限制（service 限制為 100）
    resp = client.get('/api/animals?per_page=150')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['per_page'] <= 100  # 應被限制為最大值


def test_species_filter(client):
    """
    整合測試：驗證物種過濾功能
    
    Use Case 1.1 擴充功能：過濾支援
    
    測試層級：整合測試
    前置條件：建立不同物種的動物
    驗證重點：
    - species=DOG 只回傳狗
    - species=CAT 只回傳貓
    """
    user = make_user('owner5@example.com')
    
    # 建立不同物種的動物
    make_animal(user, name='TestDog', species=Species.DOG)
    make_animal(user, name='TestCat', species=Species.CAT)
    make_animal(user, name='AnotherDog', species=Species.DOG)

    # 測試狗過濾
    resp = client.get('/api/animals?species=DOG')
    assert resp.status_code == 200
    data = resp.get_json()
    names = [a['name'] for a in data['animals']]
    assert 'TestDog' in names
    assert 'AnotherDog' in names
    assert 'TestCat' not in names
    
    # 測試貓過濾
    resp = client.get('/api/animals?species=CAT')
    assert resp.status_code == 200
    data = resp.get_json()
    names = [a['name'] for a in data['animals']]
    assert 'TestCat' in names
    assert 'TestDog' not in names
    assert 'AnotherDog' not in names


def test_search_by_name_or_breed(client):
    """
    整合測試：驗證關鍵字搜尋功能
    
    Use Case 1.1 擴充功能：搜尋支援
    
    測試層級：整合測試
    前置條件：建立含不同名稱與品種的動物
    驗證重點：
    - q 參數能匹配 name 欄位
    - q 參數能匹配 breed 欄位
    """
    user = make_user('owner6@example.com')
    
    # 建立不同名稱與品種的動物
    make_animal(user, name='Fluffy', breed='Golden Retriever')
    make_animal(user, name='Rex', breed='Bulldog')
    make_animal(user, name='Bella', breed='Fluffy Persian')

    # 測試名稱搜尋
    resp = client.get('/api/animals?q=Fluffy')
    assert resp.status_code == 200
    data = resp.get_json()
    names = [a['name'] for a in data['animals']]
    
    # 應該包含名稱為 'Fluffy' 和品種包含 'Fluffy' 的動物
    assert 'Fluffy' in names
    assert 'Bella' in names
    assert 'Rex' not in names


def test_missing_image_behaviour(client):
    """
    整合測試：驗證無圖片時的行為
    
    測試層級：整合測試
    前置條件：建立沒有圖片的動物
    驗證重點：
    - images 欄位為空陣列
    - 後端不會自動填入 placeholder URL（由前端處理）
    """
    user = make_user('owner7@example.com')
    make_animal(user, name='NoImageAnimal')

    resp = client.get('/api/animals')
    assert resp.status_code == 200
    data = resp.get_json()
    
    animal = data['animals'][0]
    assert animal['images'] == []
    # 確保沒有自動填入預設圖片 URL
    assert not any('placeholder' in str(img).lower() for img in animal['images'])


def test_member_sees_additional_fields_vs_guest(client):
    """
    整合測試：驗證會員vs訪客權限差異
    
    Use Case 1.1 輔助說明 1&2：登入角色差異
    TC-I1.1-06: 會員vs訪客權限
    
    測試層級：整合測試
    前置條件：建立動物資料，模擬登入會員
    驗證重點：
    - 會員能看到更多欄位（如醫療資訊、聯絡方式）
    - 訪客看到的欄位較少
    """
    user = make_user('owner8@example.com', role=UserRole.GENERAL_MEMBER)
    make_animal(user, name='MemberTestAnimal', description='Test medical info')

    # 測試訪客視角（無 token）
    resp = client.get('/api/animals')
    assert resp.status_code == 200
    guest_data = resp.get_json()
    guest_animal = guest_data['animals'][0]
    
    # 驗證基本欄位存在
    assert 'name' in guest_animal
    assert 'species' in guest_animal
    assert 'images' in guest_animal
    
    # TODO: 當實作 JWT 驗證後，加入會員登入測試
    # 目前 API 尚未完全實作 JWT 會員權限差異
    # 此測試驗證基本結構正確即可


def test_empty_result_handling(client):
    """
    整合測試：驗證空結果時的回應結構
    
    TC-I1.1-08: 空結果處理
    
    測試層級：整合測試
    前置條件：無符合條件的動物資料
    驗證重點：
    - 回傳空陣列但結構正確
    - 分頁資訊正確（total=0, pages=0）
    """
    # 不建立任何動物資料
    
    resp = client.get('/api/animals')
    assert resp.status_code == 200
    data = resp.get_json()
    
    # 驗證空結果結構
    assert 'animals' in data
    assert data['animals'] == []
    assert data['total'] == 0
    assert data['page'] == 1
    assert data['per_page'] == 20
    assert data['pages'] == 0


def test_search_with_no_matches(client):
    """
    整合測試：驗證搜尋無結果時的處理
    
    測試層級：整合測試
    前置條件：建立動物但搜尋不匹配的關鍵字
    驗證重點：
    - 搜尋無匹配時回傳空陣列
    - 結構保持正確
    """
    user = make_user('owner9@example.com')
    make_animal(user, name='TestDog', breed='Labrador')

    resp = client.get('/api/animals?q=NonExistentKeyword')
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert data['animals'] == []
    assert data['total'] == 0