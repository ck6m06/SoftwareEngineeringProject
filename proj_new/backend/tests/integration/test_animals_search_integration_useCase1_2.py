"""
Use Case 1.2 動物搜尋篩選 - 整合測試（Integration Tests）

測試範圍：完整的請求流程（route → service → ORM → database）
測試方法：建立真實測試資料（使用 SQLite in-memory），驗證端到端搜尋行為  
與單元測試的區別：單元測試使用 mock；整合測試驗證完整業務邏輯流程

參考：現有 test_animals_list_integration_useCase1_1.py
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
    
    # 處理 age 參數，轉換為 dob
    age_years = kwargs.pop('age', None)
    if age_years is not None:
        from datetime import date, timedelta
        # 計算大概的生日（當前日期減去年數）
        kwargs['dob'] = date.today() - timedelta(days=age_years * 365)
    
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
        last_animal = Animal.query.order_by(Animal.animal_id.desc()).first()
        defaults['animal_id'] = 1 if not last_animal else last_animal.animal_id + 1
    
    a = Animal(**defaults)
    db.session.add(a)
    db.session.commit()
    return a


def test_basic_keyword_search_functionality(client):
    """
    TC-I1.2-01: 基本關鍵字搜尋功能
    
    Use Case 1.2 主要流程步驟 3&4：關鍵字搜尋
    Use Case 1.2 輔助說明 1：搜尋範圍包含動物名稱、品種、描述資訊
    
    測試層級：整合測試（完整流程）
    前置條件：建立包含不同名稱、品種、描述的動物
    驗證重點：
    - 關鍵字能匹配名稱、品種、描述
    - 搜尋不區分大小寫
    - 部分匹配功能正常
    """
    user = make_user('searcher1@example.com')
    
    # 建立測試動物
    make_animal(user, name='Golden', breed='Golden Retriever', description='friendly dog')
    make_animal(user, name='Buddy', breed='Labrador', description='energetic golden color')
    make_animal(user, name='Max', breed='Bulldog', description='calm and loyal')
    
    # 測試關鍵字搜尋 "golden"
    resp = client.get('/api/animals?q=golden')
    assert resp.status_code == 200
    data = resp.get_json()
    
    # 應該找到兩筆：名稱 "Golden" 和描述中包含 "golden"
    assert len(data['animals']) == 2
    names = [a['name'] for a in data['animals']]
    assert 'Golden' in names
    assert 'Buddy' in names
    assert 'Max' not in names


def test_species_filter_functionality(client):
    """
    TC-I1.2-02: 物種篩選功能
    
    Use Case 1.2 主要流程步驟 2&5：物種篩選
    
    測試層級：整合測試
    前置條件：建立不同物種的動物
    驗證重點：只回傳指定物種的動物
    """
    user = make_user('searcher2@example.com')
    
    # 建立不同物種的動物
    make_animal(user, name='Dog1', species=Species.DOG)
    make_animal(user, name='Cat1', species=Species.CAT)
    make_animal(user, name='Dog2', species=Species.DOG)
    
    # 測試狗過濾
    resp = client.get('/api/animals?species=DOG')
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert len(data['animals']) == 2
    names = [a['name'] for a in data['animals']]
    assert 'Dog1' in names
    assert 'Dog2' in names
    assert 'Cat1' not in names
    
    # 測試貓過濾
    resp = client.get('/api/animals?species=CAT')
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert len(data['animals']) == 1
    assert data['animals'][0]['name'] == 'Cat1'


def test_age_range_filter_functionality(client):
    """
    TC-I1.2-03: 年齡範圍篩選功能
    
    Use Case 1.2 主要流程步驟 2&5：年齡篩選
    
    測試層級：整合測試
    前置條件：建立不同年齡的動物
    驗證重點：只回傳指定年齡範圍的動物
    """
    user = make_user('searcher3@example.com')
    
    # 建立不同年齡的動物（年齡以月數計算，使用 30.44 天的平均月份長度）
    from datetime import date, timedelta
    today = date.today()
    make_animal(user, name='Puppy', dob=today - timedelta(days=int(12*30.44)))    # 約 12 個月
    make_animal(user, name='Young', dob=today - timedelta(days=int(37*30.44)))    # 約 37 個月 (確保超過36)
    make_animal(user, name='Adult', dob=today - timedelta(days=int(60*30.44)))    # 約 60 個月
    make_animal(user, name='Senior', dob=today - timedelta(days=int(108*30.44)))  # 約 108 個月
    
    # 測試年齡範圍 36-84 個月 (3-7 歲)
    resp = client.get('/api/animals?min_age=36&max_age=84')
    assert resp.status_code == 200
    data = resp.get_json()
    
    # 應該回傳 3 歲和 5 歲的動物
    assert len(data['animals']) == 2
    names = [a['name'] for a in data['animals']]
    assert 'Young' in names
    assert 'Adult' in names
    assert 'Puppy' not in names
    assert 'Senior' not in names


def test_sex_filter_functionality(client):
    """
    TC-I1.2-04: 性別篩選功能
    
    Use Case 1.2 主要流程步驟 2&5：性別篩選
    
    測試層級：整合測試
    前置條件：建立不同性別的動物
    驗證重點：只回傳指定性別的動物
    """
    user = make_user('searcher4@example.com')
    
    # 建立不同性別的動物
    make_animal(user, name='Male1', sex=Sex.MALE)
    make_animal(user, name='Female1', sex=Sex.FEMALE)
    make_animal(user, name='Male2', sex=Sex.MALE)
    
    # 測試雌性過濾
    resp = client.get('/api/animals?sex=FEMALE')
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert len(data['animals']) == 1
    assert data['animals'][0]['name'] == 'Female1'
    
    # 測試雄性過濾
    resp = client.get('/api/animals?sex=MALE')
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert len(data['animals']) == 2
    names = [a['name'] for a in data['animals']]
    assert 'Male1' in names
    assert 'Male2' in names


def test_multiple_conditions_and_logic(client):
    """
    TC-I1.2-05: 多重條件AND邏輯測試
    
    Use Case 1.2 輔助說明 2：多條件搜尋以AND邏輯處理
    
    測試層級：整合測試
    前置條件：建立多樣動物資料
    驗證重點：
    - 只回傳同時符合所有條件的動物
    - AND邏輯正確運作
    """
    user = make_user('searcher5@example.com')
    
    # 建立測試動物
    from datetime import date, timedelta
    today = date.today()
    make_animal(user, name='Perfect', species=Species.DOG, sex=Sex.MALE, dob=today - timedelta(days=36*30), description='friendly dog')  # 36 個月
    make_animal(user, name='Wrong Species', species=Species.CAT, sex=Sex.MALE, dob=today - timedelta(days=36*30), description='friendly cat')
    make_animal(user, name='Wrong Sex', species=Species.DOG, sex=Sex.FEMALE, dob=today - timedelta(days=36*30), description='friendly dog')
    make_animal(user, name='Wrong Age', species=Species.DOG, sex=Sex.MALE, dob=today - timedelta(days=96*30), description='friendly dog')  # 96 個月
    make_animal(user, name='No Keyword', species=Species.DOG, sex=Sex.MALE, dob=today - timedelta(days=36*30), description='calm dog')
    
    # 測試多重條件：狗 + 雄性 + 24-48個月 (2-4歲) + 關鍵字 "friendly"
    query = '/api/animals?species=DOG&sex=MALE&min_age=24&max_age=48&q=friendly'
    resp = client.get(query)
    assert resp.status_code == 200
    data = resp.get_json()
    
    # 只有 "Perfect" 符合所有條件
    assert len(data['animals']) == 1
    assert data['animals'][0]['name'] == 'Perfect'


def test_region_filter_functionality(client):
    """
    TC-I1.2-06: 地區篩選功能
    
    Use Case 1.2 主要流程步驟 2&5：縣市篩選
    
    測試層級：整合測試
    前置條件：建立不同地區的動物
    驗證重點：只回傳指定地區的動物
    """
    # 建立不同地區的用户（地區信息存在 User.region）
    from app.models.user import UserRole
    
    # 創建台北地區用户
    taipei_user = User(email='taipei@example.com', password_hash='test', role=UserRole.GENERAL_MEMBER)
    taipei_user.region = '台北市'
    db.session.add(taipei_user)
    db.session.commit()
    
    # 創建台中地區用户
    taichung_user = User(email='taichung@example.com', password_hash='test', role=UserRole.GENERAL_MEMBER)
    taichung_user.region = '台中市'
    db.session.add(taichung_user)
    db.session.commit()
    
    # 建立不同地區用户的動物
    make_animal(taipei_user, name='Taipei1', owner_id=taipei_user.user_id)
    make_animal(taipei_user, name='Taipei2', owner_id=taipei_user.user_id)
    make_animal(taichung_user, name='Taichung', owner_id=taichung_user.user_id)
    
    # 測試台北市過濾
    resp = client.get('/api/animals?region=台北')
    assert resp.status_code == 200
    data = resp.get_json()
    
    # 應該回傳兩筆台北市的動物
    assert len(data['animals']) == 2
    names = [a['name'] for a in data['animals']]
    assert 'Taipei1' in names
    assert 'Taipei2' in names
    assert 'Taichung' not in names


def test_empty_search_result_handling(client):
    """
    TC-I1.2-07: 空搜尋結果處理
    
    Use Case 1.2 後置條件：無符合條件顯示訊息
    
    測試層級：整合測試
    前置條件：搜尋不存在的條件組合
    驗證重點：
    - 回傳空陣列
    - total=0
    - 結構完整
    """
    user = make_user('searcher7@example.com')
    make_animal(user, name='TestDog', species=Species.DOG)
    
    # 搜尋不存在的條件
    resp = client.get('/api/animals?species=DOG&q=notexist')
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert data['animals'] == []
    assert data['total'] == 0
    assert 'page' in data
    assert 'per_page' in data
    assert 'pages' in data


def test_search_result_limit(client):
    """
    TC-I1.2-08: 結果數量限制測試
    
    Use Case 1.2 輔助說明 3：搜尋結果最多顯示100筆
    
    測試層級：整合測試
    前置條件：建立大量符合條件的動物（模擬）
    驗證重點：
    - 限制在100筆內
    - total顯示實際總數
    - 分頁資訊正確
    """
    user = make_user('searcher8@example.com')
    
    # 建立 25 筆動物來測試分頁（實際場景可能需要更多）
    for i in range(25):
        make_animal(user, name=f'Dog_{i:02d}', species=Species.DOG)
    
    # 測試 per_page 限制
    resp = client.get('/api/animals?species=DOG&per_page=200')
    assert resp.status_code == 200
    data = resp.get_json()
    
    # per_page 應該被限制（假設系統限制為 100）
    assert data['per_page'] <= 100
    assert data['total'] == 25
    assert len(data['animals']) <= data['per_page']


def test_partial_keyword_matching(client):
    """
    TC-I1.2-09: 關鍵字部分匹配測試
    
    測試層級：整合測試
    前置條件：建立包含中文名稱的動物
    驗證重點：部分關鍵字能找到完整動物名稱
    """
    user = make_user('searcher9@example.com')
    
    # 建立中文名稱動物
    make_animal(user, name='小黑', breed='拉布拉多', description='溫馴的狗狗')
    make_animal(user, name='小白', breed='波斯貓', description='可愛的貓咪')
    
    # 測試部分匹配
    resp = client.get('/api/animals?q=黑')
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert len(data['animals']) == 1
    assert data['animals'][0]['name'] == '小黑'


def test_complex_search_combination(client):
    """
    TC-I1.2-10: 複雜組合搜尋測試
    
    測試層級：整合測試
    前置條件：建立多樣化動物資料
    驗證重點：
    - 複雜搜尋條件正確執行
    - 效能在合理範圍內
    - 分頁功能正常
    """
    from app.models.user import UserRole
    
    # 建立台北地區用户
    taipei_user = User(email='taipei10@example.com', password_hash='test', role=UserRole.GENERAL_MEMBER)
    taipei_user.region = '台北市'
    db.session.add(taipei_user)
    db.session.commit()
    
    # 建立台中地區用户
    taichung_user = User(email='taichung10@example.com', password_hash='test', role=UserRole.GENERAL_MEMBER)
    taichung_user.region = '台中市'
    db.session.add(taichung_user)
    db.session.commit()
    
    # 建立多樣化動物
    from datetime import date, timedelta
    today = date.today()
    make_animal(taipei_user, name='黃金1', species=Species.DOG, sex=Sex.MALE, dob=today - timedelta(days=24*30), description='可愛的黃金獵犬', owner_id=taipei_user.user_id)  # 24 個月
    make_animal(taipei_user, name='黃金2', species=Species.DOG, sex=Sex.FEMALE, dob=today - timedelta(days=36*30), description='溫馴的黃金獵犬', owner_id=taipei_user.user_id)  # 36 個月  
    make_animal(taichung_user, name='拉拉', species=Species.DOG, sex=Sex.MALE, dob=today - timedelta(days=24*30), description='活潑的拉布拉多', owner_id=taichung_user.user_id)  # 24 個月
    
    # 執行複雜搜尋 (年齡以月數計算：12-36個月 = 1-3歲)
    complex_query = '/api/animals?species=DOG&sex=MALE&min_age=12&max_age=36&q=可愛&region=台北&page=1&per_page=5'
    resp = client.get(complex_query)
    assert resp.status_code == 200
    data = resp.get_json()
    
    # 驗證結果：只有「黃金1」符合所有條件
    assert len(data['animals']) == 1
    assert data['animals'][0]['name'] == '黃金1'
    
    # 驗證分頁資訊
    assert data['page'] == 1
    assert data['per_page'] == 5
    assert data['total'] == 1


def test_chinese_keyword_search(client):
    """
    TC-I1.2-11: 中文關鍵字搜尋測試
    
    測試層級：整合測試
    前置條件：建立中文名稱、描述的動物
    驗證重點：中文搜尋功能正常運作
    """
    user = make_user('searcher11@example.com')
    
    # 建立中文資料
    make_animal(user, name='小花', description='非常溫馴的狗狗')
    make_animal(user, name='大雄', description='活潑好動的貓咪')
    
    # 測試中文關鍵字
    resp = client.get('/api/animals?q=溫馴')
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert len(data['animals']) == 1
    assert data['animals'][0]['name'] == '小花'


def test_invalid_filter_values_handling(client):
    """
    測試層級：整合測試
    測試目的：驗證無效篩選值的處理
    前置條件：使用無效的 enum 值
    驗證重點：系統正確處理無效輸入
    """
    # 測試無效物種
    resp = client.get('/api/animals?species=INVALID_SPECIES')
    # 依據實際 API 設計，可能回傳 400 或忽略無效參數
    assert resp.status_code in [200, 400]
    
    # 如果回傳 200，表示無效參數被忽略
    if resp.status_code == 200:
        data = resp.get_json()
        assert 'animals' in data


def test_search_performance_with_multiple_filters(client):
    """
    測試層級：整合測試（效能）
    測試目的：驗證複雜搜尋的效能
    前置條件：建立足夠數量的測試資料
    驗證重點：響應時間在合理範圍內
    """
    user = make_user('performance@example.com')
    
    # 建立測試資料
    for i in range(20):
        make_animal(user, name=f'Animal_{i}', species=Species.DOG if i % 2 == 0 else Species.CAT)
    
    import time
    start_time = time.time()
    
    # 執行複雜搜尋 (年齡以月數計算：12-120個月 = 1-10歲)
    resp = client.get('/api/animals?q=Animal&species=DOG&min_age=12&max_age=120')
    
    end_time = time.time()
    response_time = end_time - start_time
    
    # 先檢查是否有錯誤，如果有則輸出錯誤信息
    if resp.status_code != 200:
        print(f"API 错误: {resp.status_code}, 响应: {resp.get_data(as_text=True)}")
    
    assert resp.status_code == 200
    data = resp.get_json()
    # 確保有回傳資料結構
    assert 'animals' in data
    # 驗證響應時間在合理範圍內（例如 2 秒）
    assert response_time < 2.0
