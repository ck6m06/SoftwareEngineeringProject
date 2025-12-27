"""
整合測試：申請系統

測試範圍：
- Route: /api/applications/*
- Service: ApplicationService
- ORM: Application model
- Database: applications 表
"""
import pytest
import json
from app.models.application import Application, ApplicationStatus, ApplicationType
from app.models.animal import Animal, AnimalStatus, Species, Sex
from datetime import date


class TestApplicationCreate:
    """測試申請創建整合流程"""
    
    def test_create_adoption_application_success(self, client, db_session, auth_headers, test_user, test_animal):
        """測試成功創建領養申請"""
        # 創建另一個用戶作為申請人（不能申請自己的動物）
        from app.models.user import User, UserRole
        from app.utils.security import hash_password
        from flask_jwt_extended import create_access_token
        
        applicant = User(
            email='applicant@test.com',
            username='applicant',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        db_session.add(applicant)
        db_session.commit()
        
        # 使用申請人的 token
        applicant_token = create_access_token(identity=str(applicant.user_id))
        applicant_headers = {
            'Authorization': f'Bearer {applicant_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'animal_id': test_animal.animal_id,
            'type': 'ADOPTION',
            'contact_phone': '0912345678',
            'contact_address': '台北市中正區',
            'occupation': '工程師',
            'housing_type': '公寓',
            'has_experience': True,
            'reason': '想要給動物一個溫暖的家'
        }
        
        response = client.post(
            '/api/applications',
            data=json.dumps(payload),
            headers=applicant_headers
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.data.decode()}"
        data = json.loads(response.data)
        assert 'application' in data
        application_data = data['application']
        assert application_data['animal_id'] == test_animal.animal_id
        assert application_data['applicant_id'] == applicant.user_id
        assert application_data['type'] == 'ADOPTION'
        assert application_data['status'] == 'PENDING'
        
        # 驗證資料庫
        application = Application.query.filter_by(
            applicant_id=applicant.user_id,
            animal_id=test_animal.animal_id
        ).first()
        assert application is not None
        assert application.contact_phone == '0912345678'
    
    def test_create_application_without_auth(self, client, db_session, test_animal):
        """測試未認證用戶創建申請"""
        payload = {
            'animal_id': test_animal.animal_id,
            'type': 'ADOPTION'
        }
        
        response = client.post(
            '/api/applications',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_create_application_for_nonexistent_animal(self, client, db_session, auth_headers):
        """測試為不存在的動物創建申請"""
        payload = {
            'animal_id': 999999,
            'type': 'ADOPTION'
        }
        
        response = client.post(
            '/api/applications',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_create_duplicate_application(self, client, db_session, auth_headers, test_user, test_animal):
        """測試創建重複申請"""
        # 創建另一個申請人
        from app.models.user import User, UserRole
        from app.utils.security import hash_password
        from flask_jwt_extended import create_access_token
        
        applicant = User(
            email='applicant_dup@test.com',
            username='applicant_dup',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        db_session.add(applicant)
        db_session.commit()
        
        # 創建第一個申請
        application = Application(
            application_id=100,  # 手動設置 ID（SQLite BIGINT 不會自動遞增）
            applicant_id=applicant.user_id,
            animal_id=test_animal.animal_id,
            type=ApplicationType.ADOPTION,
            status=ApplicationStatus.PENDING
        )
        db_session.add(application)
        db_session.commit()
        
        # 使用申請人的 token
        applicant_token = create_access_token(identity=str(applicant.user_id))
        applicant_headers = {
            'Authorization': f'Bearer {applicant_token}',
            'Content-Type': 'application/json'
        }
        
        # 嘗試創建第二個申請
        payload = {
            'animal_id': test_animal.animal_id,
            'type': 'ADOPTION',
            'contact_phone': '0912345678',
            'contact_address': '台北市',
            'reason': '想領養'
        }
        
        response = client.post(
            '/api/applications',
            data=json.dumps(payload),
            headers=applicant_headers
        )
        
        assert response.status_code == 409  # Conflict


class TestApplicationList:
    """測試申請列表整合流程"""
    
    def test_get_my_applications(self, client, db_session, auth_headers, test_user, test_animal):
        """測試獲取我的申請列表"""
        # 創建測試申請
        application = Application(
            application_id=101,  # 手動設置 ID
            applicant_id=test_user.user_id,
            animal_id=test_animal.animal_id,
            type=ApplicationType.ADOPTION,
            status=ApplicationStatus.PENDING
        )
        db_session.add(application)
        db_session.commit()
        
        response = client.get(
            '/api/applications',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'items' in data
        assert len(data['items']) > 0
        assert data['items'][0]['applicant_id'] == test_user.user_id
    
    def test_filter_applications_by_status(self, client, db_session, auth_headers, test_user, test_animal):
        """測試按狀態過濾申請"""
        # 創建不同狀態的申請
        app1 = Application(
            application_id=102,  # 手動設置 ID
            applicant_id=test_user.user_id,
            animal_id=test_animal.animal_id,
            type=ApplicationType.ADOPTION,
            status=ApplicationStatus.PENDING
        )
        db_session.add(app1)
        db_session.commit()
        
        response = client.get(
            '/api/applications?status=PENDING',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'items' in data
        for app in data['items']:
            assert app['status'] == 'PENDING'


class TestApplicationReview:
    """測試申請審核整合流程"""
    
    def test_approve_application_as_owner(self, client, db_session, auth_headers, test_user, test_animal):
        """測試動物擁有者批准申請"""
        # 創建另一個用戶作為申請人
        from app.models.user import User, UserRole
        from app.utils.security import hash_password
        
        applicant = User(
            email='applicant@test.com',
            username='applicant',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        db_session.add(applicant)
        db_session.commit()
        
        # 創建申請
        application = Application(
            application_id=103,  # 手動設置 ID
            applicant_id=applicant.user_id,
            animal_id=test_animal.animal_id,
            type=ApplicationType.ADOPTION,
            status=ApplicationStatus.PENDING
        )
        db_session.add(application)
        db_session.commit()
        
        # 審核申請
        payload = {
            'action': 'approve',
            'review_notes': '申請通過'
        }
        
        response = client.post(
            f'/api/applications/{application.application_id}/review',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'application' in data or 'status' in data
        # 檢查應用程式狀態（可能在 'application' 物件中或直接在回應中）
        app_status = data.get('application', {}).get('status') or data.get('status')
        assert app_status == 'APPROVED'
        
        # 驗證資料庫
        db_session.refresh(application)
        assert application.status == ApplicationStatus.APPROVED
        assert application.review_notes == '申請通過'
    
    def test_reject_application_with_reason(self, client, db_session, auth_headers, test_user, test_animal):
        """測試拒絕申請並提供原因"""
        from app.models.user import User, UserRole
        from app.utils.security import hash_password
        
        applicant = User(
            email='applicant2@test.com',
            username='applicant2',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        db_session.add(applicant)
        db_session.commit()
        
        application = Application(
                    application_id=109,  # 手動設置 ID
            applicant_id=applicant.user_id,
            animal_id=test_animal.animal_id,
            type=ApplicationType.ADOPTION,
            status=ApplicationStatus.PENDING
        )
        db_session.add(application)
        db_session.commit()
        
        payload = {
            'action': 'reject',
            'review_notes': '申請條件不符'
        }
        
        response = client.post(
            f'/api/applications/{application.application_id}/review',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'application' in data or 'status' in data
        # 檢查應用程式狀態（可能在 'application' 物件中或直接在回應中）
        app_status = data.get('application', {}).get('status') or data.get('status')
        assert app_status == 'REJECTED'
        
        db_session.refresh(application)
        assert application.status == ApplicationStatus.REJECTED
    
    def test_review_application_without_permission(self, client, db_session, test_user, test_animal):
        """測試無權限審核申請"""
        from flask_jwt_extended import create_access_token
        from app.models.user import User, UserRole
        from app.utils.security import hash_password
        
        # 創建另一個用戶
        other_user = User(
            email='other3@test.com',
            username='other3',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        # 創建申請
        application = Application(
            application_id=105,  # 手動設置 ID
            applicant_id=other_user.user_id,
            animal_id=test_animal.animal_id,
            type=ApplicationType.ADOPTION,
            status=ApplicationStatus.PENDING
        )
        db_session.add(application)
        db_session.commit()
        
        # 使用無權限的用戶嘗試審核
        token = create_access_token(identity=str(other_user.user_id))
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {'action': 'approve'}
        
        response = client.post(
            f'/api/applications/{application.application_id}/review',
            data=json.dumps(payload),
            headers=headers
        )
        
        assert response.status_code == 403  # Forbidden


class TestApplicationDetail:
    """測試申請詳情整合流程"""
    
    def test_get_own_application_detail(self, client, db_session, auth_headers, test_user, test_animal):
        """測試獲取自己的申請詳情"""
        application = Application(
            application_id=106,  # 手動設置 ID
            applicant_id=test_user.user_id,
            animal_id=test_animal.animal_id,
            type=ApplicationType.ADOPTION,
            status=ApplicationStatus.PENDING,
            contact_phone='0912345678'
        )
        db_session.add(application)
        db_session.commit()
        
        response = client.get(
            f'/api/applications/{application.application_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['application_id'] == application.application_id
        assert data['contact_phone'] == '0912345678'
    
    def test_get_application_detail_as_animal_owner(self, client, db_session, auth_headers, test_user, test_animal):
        """測試動物擁有者查看申請詳情"""
        from app.models.user import User, UserRole
        from app.utils.security import hash_password
        
        applicant = User(
            email='applicant3@test.com',
            username='applicant3',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        db_session.add(applicant)
        db_session.commit()
        
        application = Application(
                    application_id=110,  # 手動設置 ID
            applicant_id=applicant.user_id,
            animal_id=test_animal.animal_id,
            type=ApplicationType.ADOPTION,
            status=ApplicationStatus.PENDING
        )
        db_session.add(application)
        db_session.commit()
        
        # test_user 是 test_animal 的擁有者
        response = client.get(
            f'/api/applications/{application.application_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_get_application_without_permission(self, client, db_session, test_animal):
        """測試查看無權限的申請"""
        from flask_jwt_extended import create_access_token
        from app.models.user import User, UserRole
        from app.utils.security import hash_password
        
        user1 = User(
            email='user4@test.com',
            username='user4',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        user2 = User(
            email='user5@test.com',
            username='user5',
            password_hash=hash_password('Password123'),
            role=UserRole.GENERAL_MEMBER,
            verified=True
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # user1 的申請
        application = Application(
            application_id=108,  # 手動設置 ID
            applicant_id=user1.user_id,
            animal_id=test_animal.animal_id,
            type=ApplicationType.ADOPTION,
            status=ApplicationStatus.PENDING
        )
        db_session.add(application)
        db_session.commit()
        
        # user2 嘗試查看
        token = create_access_token(identity=str(user2.user_id))
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = client.get(
            f'/api/applications/{application.application_id}',
            headers=headers
        )
        
        assert response.status_code == 403
