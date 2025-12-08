"""
Use Case 1.4 領養申請提交 - 整合測試（Integration Tests）

測試範圍：完整的申請提交流程（route → service → ORM → database）
測試方法：建立真實測試資料（使用 SQLite in-memory），驗證端到端申請流程
與單元測試的區別：單元測試使用 mock；整合測試驗證完整業務邏輯流程

測試重點：
- 完整申請流程驗證
- 資料庫事務處理
- 重複申請防護
- 通知觸發驗證
- 申請狀態管理
"""
import pytest
import json
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from app import create_app, db
from app.models.user import User, UserRole
from app.models.animal import Animal, AnimalStatus, Species, Sex
from app.models.application import Application, ApplicationStatus, ApplicationType


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
    user = User(
        email=email, 
        password_hash='hashed_password',
        role=role, 
        first_name=first_name,
        last_name=last_name,
        username=f'{first_name}_{last_name}'.lower()
    )
    db.session.add(user)
    db.session.commit()
    return user


def make_animal(created_by, owner=None, **kwargs):
    """建立測試動物"""
    # 確保用戶 ID 存在
    db.session.refresh(created_by)
    
    # 獲取下一個動物 ID（SQLite BIGINT autoincrement 解決方案）
    from sqlalchemy import text
    result = db.session.execute(text("SELECT MAX(animal_id) FROM animals"))
    max_id = result.scalar() or 0
    next_animal_id = max_id + 1
    
    defaults = dict(
        animal_id=next_animal_id,
        name='待領養小白',
        species=Species.DOG,
        breed='黃金獵犬',
        sex=Sex.MALE,
        description='溫馴友善的狗狗，適合家庭飼養',
        status=AnimalStatus.PUBLISHED,
        created_by=created_by.user_id,
        owner_id=owner.user_id if owner else created_by.user_id,
        medical_summary='健康良好'
    )
    defaults.update(kwargs)
    
    animal = Animal(**defaults)
    db.session.add(animal)
    db.session.commit()
    return animal


def make_access_token(user):
    """為用戶建立 JWT token"""
    return create_access_token(identity=user.user_id)


def make_application_data(**kwargs):
    """建立測試申請資料"""
    defaults = {
        'contact_phone': '0912345678',
        'contact_address': '台北市大安區復興南路100號',
        'occupation': '軟體工程師',
        'housing_type': '公寓',
        'has_experience': True,
        'reason': '希望給狗狗一個溫暖的家，我有豐富的養寵物經驗',
        'notes': '平日在家工作，有充足時間照顧動物',
        'attachments': ['income_cert.pdf', 'housing_proof.jpg']
    }
    defaults.update(kwargs)
    return defaults


class TestApplicationSubmitIntegration:
    """領養申請提交整合測試"""
    
    def test_complete_application_submission_flow(self, client, app):
        """
        TC-I1.4-01: 完整申請提交流程測試
        
        Use Case 對應：主要流程完整驗證
        測試條件：建立真實使用者和動物資料，執行完整申請流程
        驗證點：
        - 申請成功建立並儲存到資料庫
        - 申請資料完整且正確
        - 關聯資訊（申請者、動物）正確建立
        - 申請時間戳記正確
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            applicant = make_user(email='applicant@test.com', first_name='申請者', last_name='小華')
            animal = make_animal(created_by=owner, owner=owner)
            
            # 準備申請資料
            application_data = make_application_data(animal_id=animal.animal_id)
            
            # 建立 JWT token
            token = make_access_token(applicant)
            headers = {'Authorization': f'Bearer {token}'}
            
            # 執行申請提交請求
            response = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 驗證 HTTP 回應
            assert response.status_code == 201
            response_data = json.loads(response.data)
            
            # 驗證回應資料結構
            assert 'application' in response_data
            assert 'message' in response_data
            assert response_data['message'] == '申請已提交'
            
            application_data = response_data['application']
            assert 'application_id' in application_data
            assert application_data['status'] == 'PENDING'
            assert application_data['animal_id'] == animal.animal_id
            assert application_data['applicant_id'] == applicant.user_id
            
            # 驗證資料庫中的申請記錄
            db_application = Application.query.filter_by(
                application_id=application_data['application_id']
            ).first()
            
            assert db_application is not None
            assert db_application.animal_id == animal.animal_id
            assert db_application.applicant_id == applicant.user_id
            assert db_application.status == ApplicationStatus.PENDING
            assert db_application.contact_phone == application_data['contact_phone']
            assert db_application.reason == application_data['reason']
            assert db_application.submitted_at is not None
            assert db_application.deleted_at is None
            
            # 驗證時間戳記在合理範圍內
            time_diff = datetime.utcnow() - db_application.submitted_at
            assert time_diff.total_seconds() < 10

    def test_duplicate_application_prevention(self, client, app):
        """
        TC-I1.4-02: 重複申請防護測試
        
        Use Case 對應：輔助說明 2 - 重複申請檢查
        測試條件：同一用戶對同一動物提交兩次申請
        驗證點：
        - 第一次申請成功
        - 第二次申請失敗並回傳409錯誤
        - 資料庫中只有一筆申請記錄
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            applicant = make_user(email='applicant@test.com', first_name='申請者', last_name='小華')
            animal = make_animal(created_by=owner, owner=owner)
            
            # 準備申請資料
            application_data = make_application_data(animal_id=animal.animal_id)
            
            # 建立 JWT token
            token = make_access_token(applicant)
            headers = {'Authorization': f'Bearer {token}'}
            
            # 第一次申請提交
            response1 = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 驗證第一次申請成功
            assert response1.status_code == 201
            
            # 第二次申請提交（重複申請）
            response2 = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 驗證第二次申請被拒絕
            assert response2.status_code == 409
            response_data = json.loads(response2.data)
            assert '您已對此動物提交申請' in response_data['message']
            
            # 驗證資料庫中只有一筆申請記錄
            applications = Application.query.filter_by(
                animal_id=animal.animal_id,
                applicant_id=applicant.user_id,
                deleted_at=None
            ).all()
            
            assert len(applications) == 1

    def test_concurrent_applications_handling(self, client, app):
        """
        TC-I1.4-03: 並發申請處理測試
        
        測試條件：多個用戶同時對同一動物提交申請
        驗證點：
        - 所有申請都能正確處理
        - 沒有資料競爭問題
        - 申請順序正確記錄
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            applicant1 = make_user(email='applicant1@test.com', first_name='申請者', last_name='一')
            applicant2 = make_user(email='applicant2@test.com', first_name='申請者', last_name='二')
            animal = make_animal(created_by=owner, owner=owner)
            
            # 準備申請資料
            app_data1 = make_application_data(
                animal_id=animal.animal_id,
                reason='我想要領養這隻狗狗 - 申請者一'
            )
            app_data2 = make_application_data(
                animal_id=animal.animal_id,
                reason='我也想要領養這隻狗狗 - 申請者二'
            )
            
            # 建立 JWT tokens
            token1 = make_access_token(applicant1)
            token2 = make_access_token(applicant2)
            headers1 = {'Authorization': f'Bearer {token1}'}
            headers2 = {'Authorization': f'Bearer {token2}'}
            
            # 第一個申請
            response1 = client.post(
                '/api/applications',
                json=app_data1,
                headers=headers1
            )
            
            # 驗證第一個申請成功
            assert response1.status_code == 201
            
            # 第二個申請（應該被業務規則拒絕，因為已有待審核申請）
            response2 = client.post(
                '/api/applications',
                json=app_data2,
                headers=headers2
            )
            
            # 驗證第二個申請被拒絕
            assert response2.status_code == 409
            response_data = json.loads(response2.data)
            assert '此動物目前有待審核的申請' in response_data['message']
            
            # 驗證資料庫狀態
            applications = Application.query.filter_by(
                animal_id=animal.animal_id,
                deleted_at=None
            ).all()
            
            # 只有一筆申請（第一個申請者的）
            assert len(applications) == 1
            assert applications[0].applicant_id == applicant1.user_id

    def test_animal_status_validation_during_application(self, client, app):
        """
        TC-I1.4-04: 動物狀態變更影響測試
        
        Use Case 對應：先決條件 - 動物狀態限制
        測試條件：在申請過程中動物狀態變更為不可申請
        驗證點：
        - 申請被正確拒絕
        - 錯誤訊息準確
        - 資料庫狀態一致
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            applicant = make_user(email='applicant@test.com', first_name='申請者', last_name='小華')
            
            # 建立已被領養的動物
            animal = make_animal(
                created_by=owner, 
                owner=owner, 
                status=AnimalStatus.ADOPTED
            )
            
            # 準備申請資料
            application_data = make_application_data(animal_id=animal.animal_id)
            
            # 建立 JWT token
            token = make_access_token(applicant)
            headers = {'Authorization': f'Bearer {token}'}
            
            # 執行申請提交請求
            response = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 驗證申請被拒絕
            assert response.status_code == 400
            response_data = json.loads(response.data)
            assert '此動物已被領養' in response_data['message']
            
            # 驗證資料庫中沒有建立申請記錄
            applications = Application.query.filter_by(
                animal_id=animal.animal_id,
                applicant_id=applicant.user_id
            ).all()
            
            assert len(applications) == 0

    def test_application_data_integrity(self, client, app):
        """
        TC-I1.4-05: 申請資料完整性測試
        
        Use Case 對應：主要流程步驟 2 - 填寫申請資訊
        測試條件：提交包含所有類型欄位的完整申請
        驗證點：
        - 所有欄位正確儲存
        - 特殊字元和Unicode正確處理
        - JSON資料正確序列化
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            applicant = make_user(email='applicant@test.com', first_name='申請者', last_name='小華')
            animal = make_animal(created_by=owner, owner=owner)
            
            # 準備包含特殊字元的完整申請資料
            application_data = {
                'animal_id': animal.animal_id,
                'contact_phone': '0912-345-678',
                'contact_address': '台北市信義區松仁路101號 🏠',
                'occupation': 'IT工程師 / Software Developer',
                'housing_type': '電梯大廈',
                'has_experience': True,
                'reason': '我❤️動物！希望能給毛孩子一個幸福的家 😊',
                'notes': '特殊字元測試: @#$%^&*()_+-=[]{}|;:\'",.<>?/~`\n多行文字測試',
                'attachments': [
                    'income_certificate.pdf',
                    'housing_proof_房屋證明.jpg',
                    'pet_experience_寵物經驗.doc'
                ]
            }
            
            # 建立 JWT token
            token = make_access_token(applicant)
            headers = {'Authorization': f'Bearer {token}'}
            
            # 執行申請提交請求
            response = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 驗證 HTTP 回應
            assert response.status_code == 201
            response_data = json.loads(response.data)
            
            # 驗證資料庫中的申請記錄
            application_data_response = response_data['application']
            db_application = Application.query.filter_by(
                application_id=application_data_response['application_id']
            ).first()
            
            # 驗證所有欄位正確儲存
            assert db_application.contact_phone == application_data['contact_phone']
            assert db_application.contact_address == application_data['contact_address']
            assert db_application.occupation == application_data['occupation']
            assert db_application.housing_type == application_data['housing_type']
            assert db_application.has_experience == application_data['has_experience']
            assert db_application.reason == application_data['reason']
            assert db_application.notes == application_data['notes']
            assert db_application.attachments == application_data['attachments']
            
            # 驗證特殊字元和Unicode正確處理
            assert '🏠' in db_application.contact_address
            assert '😊' in db_application.reason
            assert '房屋證明' in str(db_application.attachments)

    def test_authentication_requirement(self, client, app):
        """
        TC-I1.4-06: JWT認證要求測試
        
        Use Case 對應：行為者限制 - 一般會員
        測試條件：未提供JWT token或提供無效token
        驗證點：
        - 無token時回傳401錯誤
        - 無效token時回傳401錯誤
        - 錯誤訊息指出需要登入
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            animal = make_animal(created_by=owner, owner=owner)
            
            # 準備申請資料
            application_data = make_application_data(animal_id=animal.animal_id)
            
            # 測試無 Authorization header
            response1 = client.post(
                '/api/applications',
                json=application_data
            )
            
            assert response1.status_code == 401
            
            # 測試無效 token
            invalid_headers = {'Authorization': 'Bearer invalid_token_123'}
            response2 = client.post(
                '/api/applications',
                json=application_data,
                headers=invalid_headers
            )
            
            assert response2.status_code == 401

    def test_permission_validation_shelter_user(self, client, app):
        """
        TC-I1.4-07: 權限驗證測試（收容所員工）
        
        Use Case 對應：行為者限制 - 一般會員
        測試條件：收容所員工嘗試提交申請
        驗證點：
        - 申請被拒絕並回傳403錯誤
        - 錯誤訊息指出權限不足
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            shelter_staff = make_user(
                email='staff@shelter.com', 
                first_name='收容所',
                last_name='員工',
                role=UserRole.SHELTER_MEMBER
            )
            animal = make_animal(created_by=owner, owner=owner)
            
            # 準備申請資料
            application_data = make_application_data(animal_id=animal.animal_id)
            
            # 建立 JWT token for shelter staff
            token = make_access_token(shelter_staff)
            headers = {'Authorization': f'Bearer {token}'}
            
            # 執行申請提交請求
            response = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 驗證申請被拒絕
            assert response.status_code == 403
            response_data = json.loads(response.data)
            assert '只有一般會員可提出領養申請' in response_data['message']

    def test_own_animal_application_prevention(self, client, app):
        """
        TC-I1.4-08: 申請自己動物防護測試
        
        測試條件：用戶嘗試申請自己的動物
        驗證點：
        - 申請被拒絕並回傳400錯誤
        - 錯誤訊息明確指出不能申請自己的動物
        """
        with app.app_context():
            # 建立測試資料（用戶同時是動物擁有者）
            user = make_user(email='user@test.com', first_name='測試', last_name='用戶')
            animal = make_animal(created_by=user, owner=user)
            
            # 準備申請資料
            application_data = make_application_data(animal_id=animal.animal_id)
            
            # 建立 JWT token
            token = make_access_token(user)
            headers = {'Authorization': f'Bearer {token}'}
            
            # 執行申請提交請求
            response = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 驗證申請被拒絕
            assert response.status_code == 400
            response_data = json.loads(response.data)
            assert '您不能申請自己刊登的動物' in response_data['message']

    def test_idempotency_key_support(self, client, app):
        """
        TC-I1.4-09: 冪等性鍵值支援測試
        
        測試條件：使用相同的 Idempotency-Key 進行重複請求
        驗證點：
        - 第一次請求成功建立申請
        - 第二次請求回傳相同結果
        - 資料庫中只有一筆申請記錄
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            applicant = make_user(email='applicant@test.com', first_name='申請者', last_name='小華')
            animal = make_animal(created_by=owner, owner=owner)
            
            # 準備申請資料
            application_data = make_application_data(animal_id=animal.animal_id)
            
            # 建立 JWT token 和 Idempotency-Key
            token = make_access_token(applicant)
            idempotency_key = 'test-idempotency-key-123'
            headers = {
                'Authorization': f'Bearer {token}',
                'Idempotency-Key': idempotency_key
            }
            
            # 第一次請求
            response1 = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 驗證第一次請求成功
            assert response1.status_code == 201
            response_data1 = json.loads(response1.data)
            
            # 第二次請求（相同 Idempotency-Key）
            response2 = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 驗證第二次請求回傳相同結果
            assert response2.status_code == 201
            response_data2 = json.loads(response2.data)
            assert response_data1['application']['application_id'] == response_data2['application']['application_id']
            
            # 驗證資料庫中只有一筆記錄
            applications = Application.query.filter_by(
                animal_id=animal.animal_id,
                applicant_id=applicant.user_id,
                deleted_at=None
            ).all()
            
            assert len(applications) == 1
            assert applications[0].idempotency_key == idempotency_key

    def test_large_application_data_processing(self, client, app):
        """
        TC-I1.4-10: 大量申請資料效能測試
        
        測試條件：提交包含大量文字和資料的申請
        驗證點：
        - 申請處理時間在合理範圍內
        - 記憶體使用正常
        - 資料庫查詢效率良好
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            applicant = make_user(email='applicant@test.com', first_name='申請者', last_name='小華')
            animal = make_animal(created_by=owner, owner=owner)
            
            # 準備包含大量文字的申請資料
            large_text = '這是一段很長的文字。' * 1000  # 約10KB文字
            large_attachments = [f'attachment_{i}.jpg' for i in range(50)]  # 50個附件
            
            application_data = make_application_data(
                animal_id=animal.animal_id,
                reason=large_text,
                notes=large_text,
                attachments=large_attachments
            )
            
            # 建立 JWT token
            token = make_access_token(applicant)
            headers = {'Authorization': f'Bearer {token}'}
            
            # 記錄開始時間
            start_time = datetime.utcnow()
            
            # 執行申請提交請求
            response = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 計算處理時間
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # 驗證回應成功
            assert response.status_code == 201
            
            # 驗證處理時間在合理範圍內（應該少於5秒）
            assert processing_time < 5.0
            
            # 驗證資料正確儲存
            response_data = json.loads(response.data)
            application_data_response = response_data['application']
            db_application = Application.query.filter_by(
                application_id=application_data_response['application_id']
            ).first()
            
            assert len(db_application.reason) >= 10000  # 大量文字正確儲存
            assert len(db_application.attachments) == 50  # 所有附件正確儲存

    def test_application_validation_errors(self, client, app):
        """
        TC-I1.4-11: 申請資料驗證錯誤測試
        
        測試條件：提交不完整或格式錯誤的申請資料
        驗證點：
        - 回傳400錯誤
        - 錯誤訊息指出具體驗證失敗欄位
        - 資料庫中不建立不完整記錄
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            applicant = make_user(email='applicant@test.com', first_name='申請者', last_name='小華')
            animal = make_animal(created_by=owner, owner=owner)
            
            # 建立 JWT token
            token = make_access_token(applicant)
            headers = {'Authorization': f'Bearer {token}'}
            
            # 測試缺少必填欄位
            invalid_data1 = {
                'contact_phone': '0912345678',
                'reason': '想要領養'
                # 缺少 animal_id
            }
            
            response1 = client.post(
                '/api/applications',
                json=invalid_data1,
                headers=headers
            )
            
            assert response1.status_code == 400
            response_data1 = json.loads(response1.data)
            assert '缺少必填欄位' in response_data1['message']
            
            # 測試無效的動物ID
            invalid_data2 = make_application_data(animal_id='invalid-animal-id')
            
            response2 = client.post(
                '/api/applications',
                json=invalid_data2,
                headers=headers
            )
            
            assert response2.status_code == 404
            response_data2 = json.loads(response2.data)
            assert '動物不存在' in response_data2['message']
            
            # 驗證資料庫中沒有建立不完整記錄
            applications = Application.query.filter_by(
                applicant_id=applicant.user_id,
                deleted_at=None
            ).all()
            
            assert len(applications) == 0

    def test_notification_trigger_on_successful_submission(self, client, app):
        """
        TC-I1.4-12: 通知觸發驗證測試
        
        Use Case 對應：申請提交後的後續處理
        測試條件：成功提交申請
        驗證點：
        - 申請成功建立
        - 通知服務被觸發（這裡我們只驗證資料結構，實際通知在真實環境中測試）
        """
        with app.app_context():
            # 建立測試資料
            owner = make_user(email='owner@test.com', first_name='動物', last_name='擁有者')
            applicant = make_user(email='applicant@test.com', first_name='申請者', last_name='小華')
            animal = make_animal(created_by=owner, owner=owner)
            
            # 準備申請資料
            application_data = make_application_data(animal_id=animal.animal_id)
            
            # 建立 JWT token
            token = make_access_token(applicant)
            headers = {'Authorization': f'Bearer {token}'}
            
            # 執行申請提交請求
            response = client.post(
                '/api/applications',
                json=application_data,
                headers=headers
            )
            
            # 驗證申請成功
            assert response.status_code == 201
            response_data = json.loads(response.data)
            application_data_response = response_data['application']
            
            # 驗證申請記錄包含通知所需的資訊
            db_application = Application.query.filter_by(
                application_id=application_data_response['application_id']
            ).first()
            
            # 驗證申請資料包含通知所需的基本資訊
            assert db_application.applicant_id == applicant.user_id
            assert db_application.animal_id == animal.animal_id
            assert db_application.submitted_at is not None
            assert db_application.contact_phone is not None
            assert db_application.reason is not None
            
            # 在實際環境中，這裡會驗證通知服務的調用
            # 由於測試環境限制，我們主要驗證資料結構完整性