"""
Use Case 1.4 領養申請提交 - Service 單元測試

測試範圍：僅測試 application_service.create_application() 的業務邏輯
測試方法：使用 monkeypatch mock ORM 操作，不依賴真實資料庫
與其他測試的區別：
- Unit Tests: 測試 service 業務邏輯，mock ORM
- Controller Tests: 測試 route 層邏輯，mock service  
- Integration Tests: 測試完整流程，使用真實 DB
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from uuid import uuid4

from app import create_app
from app.services.application_service import ApplicationService
from app.models.application import Application, ApplicationStatus, ApplicationType
from app.models.animal import Animal, AnimalStatus, Species, Sex
from app.models.user import User, UserRole
from app.exceptions import (
    PermissionDeniedError, NotFoundError, ValidationError, ConflictError
)


@pytest.fixture
def app():
    """創建測試應用程式"""
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    """創建應用程式上下文"""
    with app.app_context():
        yield app


@pytest.fixture
def mock_general_user():
    """模擬一般會員用戶"""
    user = Mock(spec=User)
    user.user_id = str(uuid4())
    user.role = UserRole.GENERAL_MEMBER
    user.username = 'test_user'
    user.email = 'test@example.com'
    user.primary_shelter_id = None
    return user


@pytest.fixture
def mock_owner_user():
    """模擬動物擁有者"""
    user = Mock(spec=User)
    user.user_id = str(uuid4())
    user.role = UserRole.GENERAL_MEMBER
    user.username = 'animal_owner'
    user.email = 'owner@example.com'
    return user


@pytest.fixture
def mock_shelter_user():
    """模擬收容所員工"""
    user = Mock(spec=User)
    user.user_id = str(uuid4())
    user.role = UserRole.SHELTER_MEMBER
    user.username = 'shelter_staff'
    user.email = 'shelter@example.com'
    user.primary_shelter_id = 'shelter-123'
    return user


@pytest.fixture
def mock_available_animal(mock_owner_user):
    """模擬可領養的動物"""
    animal = Mock(spec=Animal)
    animal.animal_id = 'animal-123'
    animal.name = '小白'
    animal.species = Species.DOG
    animal.status = AnimalStatus.PUBLISHED
    animal.owner_id = mock_owner_user.user_id
    animal.created_by = mock_owner_user.user_id
    animal.deleted_at = None
    return animal


@pytest.fixture
def mock_adopted_animal(mock_owner_user):
    """模擬已被領養的動物"""
    animal = Mock(spec=Animal)
    animal.animal_id = 'adopted-animal'
    animal.name = '小黑'
    animal.species = Species.DOG
    animal.status = AnimalStatus.ADOPTED
    animal.owner_id = mock_owner_user.user_id
    animal.created_by = mock_owner_user.user_id
    animal.deleted_at = None
    return animal


@pytest.fixture
def mock_valid_application_data():
    """模擬有效的申請資料"""
    return {
        'animal_id': 'animal-123',
        'type': 'ADOPTION',
        'contact_phone': '0912345678',
        'contact_address': '台北市大安區復興南路100號',
        'occupation': '軟體工程師',
        'housing_type': '公寓',
        'has_experience': True,
        'reason': '希望給狗狗一個溫暖的家，我有豐富的養寵物經驗',
        'notes': '平日在家工作，有充足時間照顧動物',
        'attachments': ['photo1.jpg', 'cert.pdf']
    }


class TestApplicationServiceCreateApplication:
    """測試 application_service.create_application() 的業務邏輯"""
    
    def test_successful_application_creation_without_idempotency(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal, mock_valid_application_data
    ):
        """
        TC-U1.4-01a: 正常申請提交測試（無冪等性鍵）
        
        測試目的：驗證正常情況下的申請建立（不使用冪等性鍵）
        Use Case 對應：主要流程步驟 3&4 - 提交申請並儲存
        測試條件：合法用戶、可申請動物、完整申請資料、無冪等性鍵
        """
        # Mock Application.query
        mock_app_query = Mock()
        
        # 正確設置鏈式調用：filter_by().filter().first() 和 filter_by().first()
        def mock_filter_by(*args, **kwargs):
            mock_chain = Mock()
            
            # 設置 .filter() 方法
            def mock_filter(*filter_args, **filter_kwargs):
                mock_result = Mock()
                mock_result.first.return_value = None  # 沒有找到重複申請
                return mock_result
            
            mock_chain.filter = mock_filter
            mock_chain.first.return_value = None  # 針對簡單的 .first() 調用（冪等性檢查）
            return mock_chain
        
        mock_app_query.filter_by = mock_filter_by
        
        # Mock Application 構造函數
        mock_application_instance = Mock(spec=Application)
        mock_application_instance.animal_id = mock_valid_application_data['animal_id']
        mock_application_instance.applicant_id = mock_general_user.user_id
        mock_application_instance.status = ApplicationStatus.PENDING
        mock_application_instance.type = 'ADOPTION'
        
        # Mock Animal.query.filter_by().first() 返回可申請動物
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_available_animal
        
        # 直接 patch Animal 和 Application 在 application_service 模組內的引用
        with patch('app.services.application_service.Animal') as mock_animal_class, \
             patch('app.services.application_service.Application') as mock_application_class:
             
            # 設置 Animal.query.filter_by().first() 返回可申請動物
            mock_animal_class.query.filter_by.return_value.first.return_value = mock_available_animal
            
            # 設置 Application.query 的複雜鏈式調用
            mock_application_class.query.filter_by = mock_filter_by
            mock_application_class.return_value = mock_application_instance            # Mock db.session
            mock_session = Mock()
            mock_session.add = Mock()
            mock_session.commit = Mock()
            # Mock MAX ID 查詢
            mock_session.execute.return_value.scalar.return_value = 5  # 模擬現有最大ID
            monkeypatch.setattr('app.services.application_service.db.session', mock_session)
            monkeypatch.setattr('app.services.application_service.db.text', Mock(return_value='SELECT MAX(application_id) FROM applications'))
            
            # Mock notification_service.notify_application_submitted
            mock_notification_service = Mock()
            monkeypatch.setattr(
                'app.services.application_service.notification_service',
                mock_notification_service
            )
            
            # 執行測試（沒有 idempotency_key）
            result = ApplicationService.create_application(
                applicant=mock_general_user,
                data=mock_valid_application_data
            )
            
            # 驗證結果
            assert result == mock_application_instance
            assert result.animal_id == mock_valid_application_data['animal_id']
            assert result.applicant_id == mock_general_user.user_id
            assert result.status == ApplicationStatus.PENDING
            
            # 驗證 Application 構造函數被正確調用
            mock_application_class.assert_called_once()
            call_args = mock_application_class.call_args
            assert call_args.kwargs['animal_id'] == mock_valid_application_data['animal_id']
            assert call_args.kwargs['applicant_id'] == mock_general_user.user_id
            assert call_args.kwargs['status'] == ApplicationStatus.PENDING
            
            # 驗證資料庫操作
            mock_session.add.assert_called_once_with(mock_application_instance)
            mock_session.commit.assert_called_once()
            
            # 驗證通知服務被調用（實際調用包含額外參數）
            mock_notification_service.notify_application_submitted.assert_called_once()
    
    def test_idempotency_returns_existing_application(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal, mock_valid_application_data
    ):
        """
        TC-U1.4-01b: 冪等性測試 - 返回現有申請
        
        測試目的：驗證相同冪等性鍵重複提交時返回現有申請
        Use Case 對應：業務邏輯 - 冪等性檢查
        測試條件：合法用戶、現有申請、相同冪等性鍵
        """
        # Mock Application.query
        mock_app_query = Mock()
        
        # 創建現有申請的 Mock
        existing_application = Mock(spec=Application)
        existing_application.animal_id = mock_valid_application_data['animal_id']
        existing_application.applicant_id = mock_general_user.user_id
        existing_application.status = ApplicationStatus.PENDING
        existing_application.type = 'ADOPTION'
        
        def mock_filter_by(*args, **kwargs):
            # 檢查是否為冪等性查詢
            if 'idempotency_key' in str(kwargs):
                # 冪等性查詢返回現有申請
                idempotency_chain = Mock()
                idempotency_chain.first.return_value = existing_application
                return idempotency_chain
            else:
                # 其他查詢返回 None
                basic_chain = Mock()
                basic_chain.filter.return_value.first.return_value = None
                return basic_chain
        
        mock_app_query.filter_by = mock_filter_by
        
        # Mock Animal.query.filter_by().first() 返回可申請動物
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_available_animal
        
        # 直接 patch Animal 和 Application 在 application_service 模組內的引用
        with patch('app.services.application_service.Animal') as mock_animal_class, \
             patch('app.services.application_service.Application') as mock_application_class:
             
            # 設置 Animal.query.filter_by().first() 返回可申請動物
            mock_animal_class.query.filter_by.return_value.first.return_value = mock_available_animal
            
            # 設置 Application.query 的複雜鏈式調用
            mock_application_class.query.filter_by = mock_filter_by
             
            # Mock db.session（不應該被調用寫操作）
            mock_session = Mock()
            mock_session.add = Mock()
            mock_session.commit = Mock()
            monkeypatch.setattr('app.services.application_service.db.session', mock_session)
            
            # 執行測試（有 idempotency_key 且找到重複）
            result = ApplicationService.create_application(
                applicant=mock_general_user,
                data=mock_valid_application_data,
                idempotency_key='test-key-123'
            )
            
            # 驗證返回的是現有申請
            assert result == existing_application
            
            # 驗證沒有進行數據庫寫操作
            mock_session.add.assert_not_called()
            mock_session.commit.assert_not_called()

    def test_non_general_member_permission_denied(
        self, app_context, mock_shelter_user, mock_valid_application_data
    ):
        """
        TC-U1.4-02: 非一般會員權限檢查測試
        
        測試目的：驗證只有一般會員可以提交領養申請
        Use Case 對應：行為者限制 - 一般會員
        測試條件：收容所員工嘗試提交申請
        """
        with pytest.raises(PermissionDeniedError) as exc_info:
            ApplicationService.create_application(
                applicant=mock_shelter_user,
                data=mock_valid_application_data
            )
        
        assert '只有一般會員可提出領養申請' in str(exc_info.value)

    def test_missing_animal_id_validation(
        self, app_context, mock_general_user
    ):
        """
        TC-U1.4-03: 必填欄位驗證測試
        
        測試目的：驗證申請資料必填欄位檢查
        Use Case 對應：輔助說明 1 - 必填欄位驗證
        測試條件：申請資料缺少必填的 animal_id
        """
        invalid_data = {
            'contact_phone': '0912345678',
            'reason': '想要領養動物'
            # 缺少 animal_id
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ApplicationService.create_application(
                applicant=mock_general_user,
                data=invalid_data
            )
        
        assert '缺少必填欄位: animal_id' in str(exc_info.value)

    def test_animal_not_found(
        self, app_context, monkeypatch, mock_general_user, mock_valid_application_data
    ):
        """
        TC-U1.4-04: 動物不存在處理測試
        
        測試目的：驗證申請不存在動物的錯誤處理
        測試條件：無效的動物ID
        """
        # Mock Animal.query 返回 None
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = None
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        with pytest.raises(NotFoundError) as exc_info:
            ApplicationService.create_application(
                applicant=mock_general_user,
                data=mock_valid_application_data
            )
        
        assert '動物不存在' in str(exc_info.value)

    def test_adopted_animal_validation(
        self, app_context, monkeypatch, mock_general_user, 
        mock_adopted_animal, mock_valid_application_data
    ):
        """
        TC-U1.4-05: 動物狀態驗證測試（已被領養）
        
        測試目的：驗證不能對已被領養的動物提交申請
        Use Case 對應：先決條件 - 動物狀態必須是「已發布」
        測試條件：動物狀態為ADOPTED
        """
        # Mock Animal.query 返回已被領養的動物
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_adopted_animal
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        with pytest.raises(ValidationError) as exc_info:
            ApplicationService.create_application(
                applicant=mock_general_user,
                data=mock_valid_application_data
            )
        
        assert '此動物已被領養' in str(exc_info.value)

    def test_unpublished_animal_validation(
        self, app_context, monkeypatch, mock_general_user, 
        mock_owner_user, mock_valid_application_data
    ):
        """
        TC-U1.4-06: 動物狀態驗證測試（未發布）
        
        測試目的：驗證只能對「已發布」狀態的動物提交申請
        Use Case 對應：先決條件 - 動物狀態必須是「已發布」
        測試條件：動物狀態為PENDING
        """
        # 創建未發布的動物
        mock_unpublished_animal = Mock(spec=Animal)
        mock_unpublished_animal.animal_id = 'unpublished-animal'
        mock_unpublished_animal.status = AnimalStatus.DRAFT
        mock_unpublished_animal.owner_id = mock_owner_user.user_id
        mock_unpublished_animal.created_by = mock_owner_user.user_id
        mock_unpublished_animal.deleted_at = None
        
        # Mock Animal.query
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_unpublished_animal
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        with pytest.raises(ValidationError) as exc_info:
            ApplicationService.create_application(
                applicant=mock_general_user,
                data=mock_valid_application_data
            )
        
        assert '此動物目前無法申請領養' in str(exc_info.value)

    def test_own_animal_application_denied(
        self, app_context, monkeypatch, mock_general_user, mock_valid_application_data
    ):
        """
        TC-U1.4-07: 申請自己動物檢查測試
        
        測試目的：驗證用戶不能申請自己的動物
        測試條件：申請者ID等於動物擁有者ID
        """
        # 創建申請者自己的動物
        mock_own_animal = Mock(spec=Animal)
        mock_own_animal.animal_id = 'own-animal'
        mock_own_animal.status = AnimalStatus.PUBLISHED
        mock_own_animal.owner_id = mock_general_user.user_id  # 同一個用戶
        mock_own_animal.created_by = mock_general_user.user_id
        mock_own_animal.deleted_at = None
        
        # Mock Animal.query
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_own_animal
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        with pytest.raises(ValidationError) as exc_info:
            ApplicationService.create_application(
                applicant=mock_general_user,
                data=mock_valid_application_data
            )
        
        assert '您不能申請自己刊登的動物' in str(exc_info.value)

    def test_pending_application_conflict(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal, mock_valid_application_data
    ):
        """
        TC-U1.4-08: 重複申請檢查測試（系統層面）
        
        測試目的：驗證防止對有待審核申請的動物提交新申請
        Use Case 對應：輔助說明 2 - 重複申請檢查
        測試條件：動物已有其他用戶的待審核申請
        """
        # Mock Animal.query
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_available_animal
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        # Mock 有其他用戶的待審核申請
        mock_pending_app = Mock(spec=Application)
        mock_pending_app.application_id = 'pending-123'
        mock_pending_app.status = ApplicationStatus.PENDING
        mock_pending_app.applicant_id = 'other-user-id'
        
        mock_app_query = Mock()
        
        # 第一次調用：檢查當前用戶重複申請 - 返回None（無重複）
        first_filter = Mock()
        first_filter.filter.return_value.first.return_value = None
        
        # 第二次調用：檢查其他用戶待審核申請 - 返回待審核申請
        second_filter = Mock()
        second_filter.filter.return_value.first.return_value = mock_pending_app
        
        mock_app_query.filter_by.side_effect = [first_filter, second_filter]
        monkeypatch.setattr('app.models.application.Application.query', mock_app_query)
        
        with pytest.raises(ConflictError) as exc_info:
            ApplicationService.create_application(
                applicant=mock_general_user,
                data=mock_valid_application_data
            )
        
        assert '此動物目前有待審核的申請,請等待審核結果後再提出申請' in str(exc_info.value)

    def test_user_duplicate_application(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal, mock_valid_application_data
    ):
        """
        TC-U1.4-09: 用戶重複申請檢查測試
        
        測試目的：驗證防止同一用戶重複申請同一動物
        Use Case 對應：輔助說明 2 - 重複申請檢查  
        測試條件：用戶已對該動物提交過申請
        """
        # Mock Animal.query
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_available_animal
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        # Mock Application.query 設置複雜的調用序列
        mock_app_query = Mock()
        
        # 第一次調用：檢查當前用戶重複申請 - 有重複
        mock_existing_app = Mock(spec=Application)
        mock_existing_app.application_id = 'existing-123'
        mock_existing_app.status = ApplicationStatus.PENDING
        mock_existing_app.applicant_id = mock_general_user.user_id
        
        first_call_mock = Mock()
        first_call_mock.filter.return_value.first.return_value = mock_existing_app
        
        # 設置 side_effect 來模擬調用
        mock_app_query.filter_by.return_value = first_call_mock
        monkeypatch.setattr('app.models.application.Application.query', mock_app_query)
        
        with pytest.raises(ConflictError) as exc_info:
            ApplicationService.create_application(
                applicant=mock_general_user,
                data=mock_valid_application_data
            )
        
        assert '您已對此動物提交申請' in str(exc_info.value)

    def test_idempotency_key_returns_existing(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal, mock_valid_application_data
    ):
        """
        TC-U1.4-10: 冪等性鍵值測試
        
        測試目的：驗證相同冪等性鍵值返回現有申請
        測試條件：使用相同的 idempotency_key
        """
        # Mock Animal.query
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_available_animal
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        # Mock 現有冪等性申請
        mock_existing_app = Mock(spec=Application)
        mock_existing_app.application_id = 'idempotent-123'
        mock_existing_app.applicant_id = mock_general_user.user_id
        mock_existing_app.idempotency_key = 'same-key-123'
        
        # 設置多個 query mock
        mock_app_query = Mock()
        
        # 第一次調用：檢查冪等性（現在是最優先的）
        first_filter = Mock()
        first_filter.first.return_value = mock_existing_app
        
        # 只需要第一次調用，因為冪等性檢查會直接返回
        mock_app_query.filter_by.side_effect = [first_filter]
        monkeypatch.setattr('app.models.application.Application.query', mock_app_query)
        
        # 執行測試
        result = ApplicationService.create_application(
            applicant=mock_general_user,
            data=mock_valid_application_data,
            idempotency_key='same-key-123'
        )
        
        # 驗證返回現有申請
        assert result == mock_existing_app
        assert result.idempotency_key == 'same-key-123'

    def test_notification_failure_does_not_affect_creation(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal, mock_valid_application_data
    ):
        """
        TC-U1.4-11: 通知失敗不影響申請建立測試
        
        測試目的：驗證通知發送失敗不會影響申請建立的主流程
        測試條件：通知服務拋出異常
        """
        # Mock Animal.query
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_available_animal
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        # Mock Application.query 檢查重複申請，返回無重複
        mock_app_query = Mock()
        
        # 第一次調用：檢查任何待審核申請
        first_filter = Mock()
        first_filter.filter.return_value.first.return_value = None
        
        # 第二次調用：檢查用戶重複申請
        second_filter = Mock()
        second_filter.filter.return_value.first.return_value = None
        
        # 第三次調用：檢查冪等性
        third_filter = Mock()
        third_filter.first.return_value = None
        
        mock_app_query.filter_by.side_effect = [first_filter, second_filter, third_filter]
        monkeypatch.setattr('app.models.application.Application.query', mock_app_query)
        
        # Mock db.session
        mock_session = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        # Mock MAX ID 查詢
        mock_session.execute.return_value.scalar.return_value = 5  # 模擬現有最大ID
        monkeypatch.setattr('app.services.application_service.db.session', mock_session)
        monkeypatch.setattr('app.services.application_service.db.text', Mock(return_value='SELECT MAX(application_id) FROM applications'))
        
        # Mock notification_service 拋出異常
        mock_notification_service = Mock()
        mock_notification_service.notify_application_submitted.side_effect = Exception('通知服務故障')
        monkeypatch.setattr(
            'app.services.application_service.notification_service',
            mock_notification_service
        )
        
        # 執行測試 - 應該成功完成，不會因通知失敗而拋出異常
        result = ApplicationService.create_application(
            applicant=mock_general_user,
            data=mock_valid_application_data
        )
        
        # 驗證申請仍然成功建立
        assert isinstance(result, Application)
        assert result.applicant_id == mock_general_user.user_id
        
        # 驗證資料庫操作正常執行
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_application_with_minimal_data(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal
    ):
        """
        TC-U1.4-12: 最小資料申請測試
        
        測試目的：驗證只包含必填欄位的申請可以成功建立
        測試條件：只提供 animal_id 和基本聯絡資訊
        """
        minimal_data = {
            'animal_id': 'animal-123',
            'contact_phone': '0912345678',
            'reason': '想領養'
        }
        
        # Mock Animal.query
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_available_animal
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        # Mock Application.query 檢查重複申請，返回無重複
        mock_app_query = Mock()
        
        # 模擬三次查詢都返回 None
        mock_filter1 = Mock()
        mock_filter1.filter.return_value.first.return_value = None
        
        mock_filter2 = Mock()
        mock_filter2.filter.return_value.first.return_value = None
        
        mock_filter3 = Mock()
        mock_filter3.first.return_value = None
        
        mock_app_query.filter_by.side_effect = [mock_filter1, mock_filter2, mock_filter3]
        monkeypatch.setattr('app.models.application.Application.query', mock_app_query)
        
        # Mock db.session
        mock_session = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        # Mock MAX ID 查詢
        mock_session.execute.return_value.scalar.return_value = 5  # 模擬現有最大ID
        monkeypatch.setattr('app.services.application_service.db.session', mock_session)
        monkeypatch.setattr('app.services.application_service.db.text', Mock(return_value='SELECT MAX(application_id) FROM applications'))
        
        # Mock notification_service
        mock_notification_service = Mock()
        monkeypatch.setattr(
            'app.services.application_service.notification_service',
            mock_notification_service
        )
        
        # 執行測試
        result = ApplicationService.create_application(
            applicant=mock_general_user,
            data=minimal_data
        )
        
        # 驗證結果
        assert isinstance(result, Application)
        assert result.animal_id == minimal_data['animal_id']
        assert result.contact_phone == minimal_data['contact_phone']
        assert result.reason == minimal_data['reason']
        
        # 驗證可選欄位使用預設值
        assert result.type == 'ADOPTION'  # 預設值
        assert result.has_experience == False  # 預設值

    def test_application_data_with_special_characters(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal
    ):
        """
        TC-U1.4-13: 特殊字元處理測試
        
        測試目的：驗證申請資料包含特殊字元和Unicode的正確處理
        測試條件：申請資料包含中文、emoji、特殊符號
        """
        special_data = {
            'animal_id': 'animal-123',
            'contact_phone': '0912-345-678',
            'contact_address': '台北市信義區松仁路101號 🏠',
            'reason': '我❤️動物！希望能給毛孩子一個幸福的家 😊',
            'notes': '特殊字元測試: @#$%^&*()_+-=[]{}|;:\'",.<>?/~`',
            'occupation': 'IT工程師 / Software Developer'
        }
        
        # Mock Animal.query
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_available_animal
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        # Mock Application.query 檢查重複申請，返回無重複
        mock_app_query = Mock()
        
        # 模擬三次查詢都返回 None
        mock_filter1 = Mock()
        mock_filter1.filter.return_value.first.return_value = None
        
        mock_filter2 = Mock()
        mock_filter2.filter.return_value.first.return_value = None
        
        mock_filter3 = Mock()
        mock_filter3.first.return_value = None
        
        mock_app_query.filter_by.side_effect = [mock_filter1, mock_filter2, mock_filter3]
        monkeypatch.setattr('app.models.application.Application.query', mock_app_query)
        
        # Mock db.session
        mock_session = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        # Mock MAX ID 查詢
        mock_session.execute.return_value.scalar.return_value = 5  # 模擬現有最大ID
        monkeypatch.setattr('app.services.application_service.db.session', mock_session)
        monkeypatch.setattr('app.services.application_service.db.text', Mock(return_value='SELECT MAX(application_id) FROM applications'))
        
        # Mock notification_service
        mock_notification_service = Mock()
        monkeypatch.setattr(
            'app.services.application_service.notification_service',
            mock_notification_service
        )
        
        # 執行測試
        result = ApplicationService.create_application(
            applicant=mock_general_user,
            data=special_data
        )
        
        # 驗證特殊字元正確保存
        assert result.contact_address == special_data['contact_address']
        assert result.reason == special_data['reason'] 
        assert result.notes == special_data['notes']
        assert result.occupation == special_data['occupation']

    def test_application_attachments_handling(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal
    ):
        """
        TC-U1.4-14: 附件處理測試
        
        測試目的：驗證申請附件的正確處理
        測試條件：申請包含多種附件類型
        """
        attachment_data = {
            'animal_id': 'animal-123',
            'contact_phone': '0912345678',
            'reason': '想領養',
            'attachments': [
                'profile_photo.jpg',
                'income_certificate.pdf', 
                'housing_proof.doc',
                'veterinary_record.png'
            ]
        }
        
        # Mock Animal.query
        mock_animal_query = Mock()
        mock_animal_query.filter_by.return_value.first.return_value = mock_available_animal
        monkeypatch.setattr('app.models.animal.Animal.query', mock_animal_query)
        
        # Mock Application.query 檢查重複申請，返回無重複  
        mock_app_query = Mock()
        
        # 模擬三次查詢都返回 None
        mock_filter1 = Mock()
        mock_filter1.filter.return_value.first.return_value = None
        
        mock_filter2 = Mock()
        mock_filter2.filter.return_value.first.return_value = None
        
        mock_filter3 = Mock()
        mock_filter3.first.return_value = None
        
        mock_app_query.filter_by.side_effect = [mock_filter1, mock_filter2, mock_filter3]
        monkeypatch.setattr('app.models.application.Application.query', mock_app_query)
        
        # Mock db.session
        mock_session = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        # Mock MAX ID 查詢
        mock_session.execute.return_value.scalar.return_value = 5  # 模擬現有最大ID
        monkeypatch.setattr('app.services.application_service.db.session', mock_session)
        monkeypatch.setattr('app.services.application_service.db.text', Mock(return_value='SELECT MAX(application_id) FROM applications'))
        
        # Mock notification_service
        mock_notification_service = Mock()
        monkeypatch.setattr(
            'app.services.application_service.notification_service',
            mock_notification_service
        )
        
        # 執行測試
        result = ApplicationService.create_application(
            applicant=mock_general_user,
            data=attachment_data
        )
        
        # 驗證附件正確保存
        assert result.attachments == attachment_data['attachments']
        assert len(result.attachments) == 4
        assert 'profile_photo.jpg' in result.attachments