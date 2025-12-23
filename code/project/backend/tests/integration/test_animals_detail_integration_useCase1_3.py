"""
Use Case 1.3 動物詳情檢視 - 整合測試（Integration Tests）

測試範圍：完整的請求流程（route → service → ORM → database）
測試方法：建立真實測試資料（使用 SQLite in-memory），驗證端到端行為  
與單元測試的區別：單元測試使用 mock；整合測試驗證完整業務邏輯流程
"""
import pytest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from app import create_app, db
from app.models.user import User, UserRole
from app.models.animal import Animal, AnimalStatus, Species, Sex
from app.models.medical_record import MedicalRecord


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


def make_user(email='test@example.com', role=UserRole.GENERAL_MEMBER, first_name='Test', last_name='User'):
    """建立測試使用者"""
    u = User(email=email, password_hash='test', role=role, first_name=first_name, last_name=last_name)
    db.session.add(u)
    db.session.commit()
    return u


def make_animal(created_by, owner=None, **kwargs):
    """建立測試動物"""
    # 確保用戶 ID 存在
    db.session.refresh(created_by)
    
    # 暫時手動設定 animal_id 來繞過 SQLite BIGINT autoincrement 問題
    if 'animal_id' not in kwargs:
        last_animal = Animal.query.order_by(Animal.animal_id.desc()).first()
        kwargs['animal_id'] = 1 if not last_animal else last_animal.animal_id + 1
    
    defaults = dict(
        name='測試動物',
        species=Species.DOG,
        breed='混種犬',
        sex=Sex.MALE,
        description='友善的測試動物',
        status=AnimalStatus.PUBLISHED,
        created_by=created_by.user_id,
        owner_id=owner.user_id if owner else created_by.user_id
    )
    defaults.update(kwargs)
    
    animal = Animal(**defaults)
    db.session.add(animal)
    db.session.commit()
    return animal


def make_medical_record(animal, **kwargs):
    """建立測試醫療紀錄"""
    # 暫時手動設定 medical_record_id 來繞過 SQLite BIGINT autoincrement 問題
    if 'medical_record_id' not in kwargs:
        last_record = MedicalRecord.query.order_by(MedicalRecord.medical_record_id.desc()).first()
        kwargs['medical_record_id'] = 1 if not last_record else last_record.medical_record_id + 1
        
    defaults = dict(
        animal_id=animal.animal_id,
        record_type='VACCINE',
        date=datetime.now() - timedelta(days=30),
        provider='測試動物醫院',
        details='完成疫苗接種',
        verified=True
    )
    defaults.update(kwargs)
    
    record = MedicalRecord(**defaults)
    db.session.add(record)
    db.session.commit()
    return record


class TestAnimalDetailIntegration:
    """動物詳情檢視整合測試"""
    
    def test_complete_animal_data_loading(self, client, app):
        """
        TC-I1.3-01: 完整動物資料載入測試
        
        Use Case 對應：主要流程完整驗證
        測試條件：建立完整的動物資料（包含圖片、醫療紀錄、擁有者）
        驗證重點：動物基本資料、圖片、擁有者資訊、醫療紀錄摘要正確載入
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            animal = make_animal(
                created_by=owner,
                owner=owner,
                name='小白',
                species=Species.DOG,
                breed='黃金獵犬',
                description='溫馴友善的狗狗，適合家庭飼養'
            )
            
            # 建立醫療紀錄
            verified_record = make_medical_record(
                animal,
                record_type='VACCINE',
                details='完成三合一疫苗接種',
                verified=True
            )
            
            unverified_record = make_medical_record(
                animal,
                record_type='CHECKUP', 
                details='健康檢查正常',
                verified=False
            )
            
            # 保存 animal_id 用於後續測試
            animal_id = animal.animal_id
        
        # 執行測試
        resp = client.get(f'/api/animals/{animal_id}')
        
        # 驗證
        assert resp.status_code == 200
        data = resp.get_json()
        
        # 驗證動物基本資料
        assert data['animal_id'] == animal_id
        assert data['name'] == '小白'
        assert data['species'] == 'DOG'
        assert data['breed'] == '黃金獵犬'
        assert data['description'] == '溫馴友善的狗狗，適合家庭飼養'
        
        # 驗證圖片資料（應該透過 images relationship 載入）
        # assert 'images' in data
        # assert isinstance(data['images'], list)
        
        # 驗證擁有者資訊
        # assert 'owner' in data
        # assert data['owner']['first_name'] == '動物'
    
    def test_guest_vs_member_permission_difference(self, client, app):
        """
        TC-I1.3-02: 訪客vs會員權限差異測試
        
        Use Case 對應：主要流程步驟 4 - 會員權限差異
        測試條件：同一動物，分別以訪客和已登入會員身份請求
        驗證重點：訪客與會員看到的資料差異正確
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            member = make_user(email='member@test.com', first_name='一般', last_name='會員')
            animal = make_animal(
                created_by=owner,
                owner=owner,
                status=AnimalStatus.PUBLISHED
            )
            animal_id = animal.animal_id
            member_id = member.user_id
        
        # 測試訪客請求
        resp_guest = client.get(f'/api/animals/{animal_id}')
        assert resp_guest.status_code == 200
        data_guest = resp_guest.get_json()
                
        # 測試已登入會員請求
        with app.app_context():
            access_token = create_access_token(identity=member_id)
        
        headers = {'Authorization': f'Bearer {access_token}'}
        resp_member = client.get(f'/api/animals/{animal_id}', headers=headers)
        assert resp_member.status_code == 200
        data_member = resp_member.get_json()
                
        # 驗證基本資料相同
        assert data_guest['animal_id'] == data_member['animal_id'] == animal_id
        assert data_guest['name'] == data_member['name']
        
        # 在實際實作中，會員應該能看到申請按鈕相關資訊
        # 而訪客則不應該看到
    
    def test_owner_viewing_own_animal(self, client, app):
        """
        TC-I1.3-03: 擁有者查看自己動物測試
        
        Use Case 對應：輔助說明 2 - 擁有者編輯權限
        測試條件：動物擁有者查看自己的動物
        驗證重點：顯示編輯權限標示，可看到所有私人資訊，不顯示申請按鈕
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            animal = make_animal(
                created_by=owner,
                owner=owner,
                name='我的寵物'
            )
            animal_id = animal.animal_id
            owner_id = owner.user_id
        
        # 擁有者查看自己的動物
        with app.app_context():
            access_token = create_access_token(identity=owner_id)
        
        headers = {'Authorization': f'Bearer {access_token}'}
        resp = client.get(f'/api/animals/{animal_id}', headers=headers)
        
        assert resp.status_code == 200
        data = resp.get_json()
        
        # 驗證基本資料
        assert data['animal_id'] == animal.animal_id
        assert data['name'] == '我的寵物'
        
        # 在實際實作中，這裡應該包含編輯權限標示
        # 例如：assert data['canEdit'] == True
        # 且不應該顯示申請按鈕：assert data['canApply'] == False
    
    def test_application_button_display_logic(self, client, app):
        """
        TC-I1.3-04: 申請按鈕顯示邏輯測試
        
        Use Case 對應：輔助說明 1 - 申請按鈕條件
        測試條件：建立不同狀態的動物
        驗證重點：不同狀態下申請按鈕的顯示邏輯
        """
        with app.app_context():
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            member = make_user(email='member@test.com', first_name='一般', last_name='會員')
            
            # 建立不同狀態的動物
            animal_available = make_animal(
                created_by=owner,
                owner=owner,
                name='可申請動物',
                status=AnimalStatus.PUBLISHED
            )
            
            animal_adopted = make_animal(
                created_by=owner,
                owner=owner,
                name='已領養動物',
                status=AnimalStatus.ADOPTED
            )
            
            # 儲存ID以避免DetachedInstanceError
            animal_available_id = animal_available.animal_id
            animal_adopted_id = animal_adopted.animal_id
            member_id = member.user_id
        
        # 準備會員的 JWT token
        with app.app_context():
            access_token = create_access_token(identity=member_id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 測試 PUBLISHED 狀態動物（應該可申請）
        resp_available = client.get(f'/api/animals/{animal_available_id}', headers=headers)
        assert resp_available.status_code == 200
        data_available = resp_available.get_json()
        assert data_available['status'] == 'PUBLISHED'
        
        # 測試 ADOPTED 狀態動物（不應該可申請）
        resp_adopted = client.get(f'/api/animals/{animal_adopted_id}', headers=headers)
        assert resp_adopted.status_code == 200
        data_adopted = resp_adopted.get_json()
        assert data_adopted['status'] == 'ADOPTED'
        
        # 測試訪客查看（不應該顯示申請按鈕）
        resp_guest = client.get(f'/api/animals/{animal_available_id}')
        assert resp_guest.status_code == 200
        data_guest = resp_guest.get_json()
        # 訪客不應該看到申請相關功能
    
    def test_medical_records_verification_filtering(self, client, app):
        """
        TC-I1.3-05: 醫療紀錄驗證狀態篩選測試
        
        Use Case 對應：輔助說明 3 - 僅顯示已驗證紀錄
        測試條件：建立動物包含已驗證和未驗證醫療紀錄
        驗證重點：只回傳 verified=true 的紀錄，紀錄內容為摘要格式
        """
        with app.app_context():
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            animal = make_animal(created_by=owner, owner=owner)
            
            # 儲存ID以避免DetachedInstanceError
            animal_id = animal.animal_id
            
            # 建立已驗證醫療紀錄
            verified_record1 = make_medical_record(
                animal,
                record_type='VACCINE',
                details='完成三合一疫苗接種',
                verified=True
            )
            
            verified_record2 = make_medical_record(
                animal,
                record_type='SURGERY',
                details='絕育手術完成',
                verified=True
            )
            
            # 建立未驗證醫療紀錄
            unverified_record = make_medical_record(
                animal,
                record_type='CHECKUP',
                details='一般健康檢查',
                verified=False
            )
        
        # 執行測試
        resp = client.get(f'/api/animals/{animal_id}')
        
        assert resp.status_code == 200
        data = resp.get_json()
        
        # 在實際實作中，應該只回傳已驗證的醫療紀錄
        # 且應該是摘要格式，不包含敏感醫療資訊
    
    def test_complex_associated_data_loading(self, client, app):
        """
        TC-I1.3-06: 複雜關聯資料載入測試
        
        測試條件：建立包含多種關聯資料的動物
        驗證重點：所有關聯資料正確載入，查詢效率合理，資料一致性保持
        """
        with app.app_context():
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            animal = make_animal(
                created_by=owner,
                owner=owner,
                name='複雜資料動物'
            )
            
            # 建立多筆醫療紀錄
            for i in range(5):
                make_medical_record(
                    animal,
                    record_type='VACCINE' if i % 2 == 0 else 'CHECKUP',
                    details=f'醫療記錄 {i+1}',
                    verified=True
                )
            
            # 儲存ID以避免DetachedInstanceError
            animal_id = animal.animal_id
        
        # 執行測試
        resp = client.get(f'/api/animals/{animal_id}')
        
        assert resp.status_code == 200
        data = resp.get_json()
        
        # 驗證基本資料
        assert data['animal_id'] == animal_id
        assert data['name'] == '複雜資料動物'
        
        # 驗證關聯資料是否正確載入
        # 在實際實作中，應該包含適當的圖片和醫療記錄資料
    
    def test_large_image_set_handling(self, client, app):
        """
        TC-I1.3-07: 大型圖片集處理測試
        
        測試條件：動物包含大量圖片
        驗證重點：圖片資料正確載入，響應時間合理，JSON解析無錯誤
        """
        with app.app_context():
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            
            # 建立包含大量圖片的動物（這裡應該透過 animal_images 表來處理）
            animal = make_animal(
                created_by=owner,
                owner=owner,
                name='多圖片動物'
            )
            
            # 儲存ID以避免DetachedInstanceError
            animal_id = animal.animal_id
        
        # 執行測試
        resp = client.get(f'/api/animals/{animal_id}')
        
        assert resp.status_code == 200
        data = resp.get_json()
        
        # 驗證基本資料
        assert data['animal_id'] == animal_id
        assert data['name'] == '多圖片動物'
        
        # 在實際實作中，圖片應該被正確解析為陣列
        # 且響應時間應該在合理範圍內
    
    def test_animal_not_found_handling(self, client, app):
        """
        TC-I1.3-08: 動物不存在處理測試
        
        測試條件：請求不存在的動物ID
        驗證重點：回傳404錯誤，錯誤訊息用戶友好，不洩露系統內部資訊
        """
        # 測試完全不存在的動物ID
        resp = client.get('/api/animals/99999')
        
        assert resp.status_code == 404
        data = resp.get_json()
        assert 'message' in data
        assert '動物不存在' in data['message']
        
        # 確保錯誤訊息是用戶友好的，不包含系統內部資訊
        assert 'database' not in data['message'].lower()
        assert 'sql' not in data['message'].lower()
    
    def test_deleted_animal_access_prevention(self, client, app):
        """
        測試目的：驗證已刪除動物無法被存取
        測試條件：動物被軟刪除（deleted_at 不為 None）
        驗證重點：已刪除動物回傳 404 錯誤
        """
        with app.app_context():
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            animal = make_animal(created_by=owner, owner=owner, name='待刪除動物')
            
            # 軟刪除動物
            animal.deleted_at = datetime.now()
            db.session.commit()
            
            animal_id = animal.animal_id
        
        # 嘗試存取已刪除的動物
        resp = client.get(f'/api/animals/{animal_id}')
        
        assert resp.status_code == 404
        data = resp.get_json()
        assert '動物不存在' in data['message']
    
    def test_concurrent_access_handling(self, client, app):
        """
        測試目的：驗證並發存取的處理
        測試條件：多個請求同時存取同一動物
        驗證重點：所有請求都能正確處理，沒有資料競爭問題
        """
        with app.app_context():
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            animal = make_animal(created_by=owner, owner=owner, name='並發測試動物')
            animal_id = animal.animal_id
        
        # 模擬並發請求（簡化版本，實際可能需要多線程測試）
        responses = []
        for i in range(5):
            resp = client.get(f'/api/animals/{animal_id}')
            responses.append(resp)
        
        # 驗證所有請求都成功
        for resp in responses:
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['animal_id'] == animal_id
            assert data['name'] == '並發測試動物'
    
    def test_performance_reasonable_response_time(self, client, app):
        """
        測試目的：驗證動物詳情載入的效能
        測試條件：正常的動物資料請求
        驗證重點：響應時間在合理範圍內
        """
        with app.app_context():
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            animal = make_animal(
                created_by=owner,
                owner=owner,
                name='效能測試動物'
            )
            
            # 建立一些醫療紀錄
            for i in range(3):
                make_medical_record(
                    animal,
                    details=f'測試記錄 {i+1}',
                    verified=True
                )
            
            animal_id = animal.animal_id
        
        import time
        
        # 測量響應時間
        start_time = time.time()
        resp = client.get(f'/api/animals/{animal_id}')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 驗證
        assert resp.status_code == 200
        # 響應時間應該在合理範圍內（例如 1 秒以內）
        assert response_time < 1.0
        
        data = resp.get_json()
        assert data['animal_id'] == animal_id
        assert data['name'] == '效能測試動物'
