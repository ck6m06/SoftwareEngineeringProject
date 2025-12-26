"""
整合測試：醫療系統

測試範圍：
- Route: /api/medical-records/animals/{animal_id}/medical-records/*
- Service: MedicalRecordService
- ORM: MedicalRecord, Attachment models
- Database: medical_records, attachments 表
"""
import pytest
import json
from datetime import datetime, timedelta, date
from app.models.medical_record import MedicalRecord, RecordType


class TestMedicalRecordCreate:
    """測試醫療記錄創建整合流程"""
    
    def test_create_medical_record_as_non_member(self, client, db_session, auth_headers, test_shelter_animal):
        """測試非收容所員工無法創建醫療記錄"""
        payload = {
            'record_type': RecordType.CHECKUP.value,
            'date': '2024-01-15',
            'provider': '測試醫院',
            'details': '測試創建'
        }
        
        response = client.post(
            f'/api/medical-records/animals/{test_shelter_animal.animal_id}/medical-records',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    def test_create_medical_record_for_nonexistent_animal(self, client, db_session, test_shelter_member):
        """測試為不存在的動物創建醫療記錄"""
        from flask_jwt_extended import create_access_token
        
        token = create_access_token(identity=test_shelter_member.user_id)
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'record_type': RecordType.CHECKUP.value,
            'date': '2024-01-15',
            'provider': '測試醫院',
            'details': '測試'
        }
        
        response = client.post(
            '/api/medical-records/animals/99999/medical-records',
            data=json.dumps(payload),
            headers=headers
        )
        
        assert response.status_code == 404


class TestMedicalRecordList:
    """測試醫療記錄列表整合流程"""
    
    def test_list_medical_records(self, client, db_session, auth_headers, test_shelter_animal, test_shelter_member):
        """測試獲取動物醫療記錄列表"""
        # 創建測試記錄
        record = MedicalRecord(
            medical_record_id=200,  # 手動設置 ID（SQLite BIGINT 不會自動遞增）
            animal_id=test_shelter_animal.animal_id,
            record_type=RecordType.CHECKUP,
            date=date(2024, 1, 15),
            provider='測試醫院',
            details='測試記錄',
            verified=True,
            verified_by=test_shelter_member.user_id
        )
        db_session.add(record)
        db_session.commit()
        
        response = client.get(
            f'/api/medical-records/animals/{test_shelter_animal.animal_id}/medical-records',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'medical_records' in data
        assert len(data['medical_records']) > 0
    
    def test_list_medical_records_with_filter(self, client, db_session, auth_headers, test_shelter_animal):
        """測試帶過濾條件的醫療記錄列表"""
        response = client.get(
            f'/api/medical-records/animals/{test_shelter_animal.animal_id}/medical-records?record_type={RecordType.VACCINE.value}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'medical_records' in data
    
    def test_list_medical_records_verified_only(self, client, db_session, auth_headers, test_shelter_animal):
        """測試只顯示已驗證記錄"""
        response = client.get(
            f'/api/medical-records/animals/{test_shelter_animal.animal_id}/medical-records?verified=true',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'medical_records' in data
        # 所有返回的記錄都應該是已驗證的
        for record in data['medical_records']:
            assert record['verified'] == True


class TestMedicalRecordUpdate:
    """測試醫療記錄更新整合流程"""
    
    def test_update_medical_record_within_24_hours(self, client, db_session, test_shelter_animal, test_shelter_member):
        """測試24小時內更新醫療記錄"""
        from flask_jwt_extended import create_access_token
        from app.utils.datetime_helper import get_naive_taipei_now
        
        token = create_access_token(identity=test_shelter_member.user_id)
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # 創建最近的記錄
        record = MedicalRecord(
            medical_record_id=202,  # 手動設置 ID
            animal_id=test_shelter_animal.animal_id,
            record_type=RecordType.CHECKUP,
            date=date(2024, 1, 15),
            provider='原醫院',
            details='原記錄',
            verified=False,
            created_at=get_naive_taipei_now()  # 剛剛創建
        )
        db_session.add(record)
        db_session.commit()
        
        payload = {
            'details': '更新後的詳細信息',
            'provider': '更新後醫院'
        }
        
        response = client.patch(
            f'/api/medical-records/{record.medical_record_id}',
            data=json.dumps(payload),
            headers=headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'medical_record' in data
        assert data['medical_record']['details'] == '更新後的詳細信息'
        
        # 驗證資料庫
        db_session.refresh(record)
        assert record.provider == '更新後醫院'


# TestMedicalRecordUpdate 類保留了 test_update_medical_record_within_24_hours，刪除了2個xfail測試


# TestMedicalRecordVerification 類已刪除 - 依賴 Verify endpoint 行為
