# Use Case 1.4 — 領養申請提交：測試架構設計

檔案位置：`specs/test_plan/unit_integration_test/useCase1_4_test_design.md`

目的：為「領養申請提交（Use Case 1.4）」撰寫完整的三層測試架構設計，包含 Unit Tests、Controller Tests、Integration Tests，幫助後端開發/測試人員實作 pytest 測試。

前提：後端採用 Python Flask + SQLAlchemy；專案已有測試配置與 ApplicationService 可用於測試環境。

## 業務需求回顧

**使用案例1.4 領養申請提交**
- 填表人：系統分析師
- 商業流程編號：BP-ANIMAL-005
- 行為者：一般會員
- 內容概述：本使用案例描述一般會員如何建立一筆領養申請資料。
- 先決條件：使用者的角色為一般會員，要申請的動物狀態必須是「已發布」，並且使用者在「1.3 動物詳情檢視」的頁面中點選「提出申請」。

**主要流程：**
1. 畫面初始時，帶入動物基本資料與申請者基本資料。
2. 使用者填寫申請資訊，包括聯絡方式、居住環境、養寵物經驗等欄位。
3. 使用者按下「提交申請」。
4. 系統出現提交成功的提示訊息，並將使用者填寫資料存進資料庫。
5. 系統顯示「申請已提交」的提示訊息。
6. 在提示訊息畫面中按下「確定」按鈕，畫面回到「我的申請」介面，可檢視剛剛提出的申請，並且也可以將申請撤回。

**輔助說明：**
- 必填欄位未填寫時，「提交申請」按鈕是失能(disable)狀態。
- 系統會檢查是否會有一個以上的使用者對同一動物提交申請。

## 測試架構分層

### Unit Tests（Service 單元測試）
- **測試範圍**：僅測試 `application_service.py` 中的申請提交業務邏輯
- **測試方法**：使用 pytest + unittest.mock mock SQLAlchemy ORM，不依賴真實資料庫
- **檔案位置**：`backend/tests/unit/test_application_service_useCase1_4.py`
- **測試重點**：
  - 申請資料驗證與儲存邏輯
  - 重複申請檢查邏輯
  - 動物狀態驗證
  - 使用者權限驗證
  - 申請資料完整性檢查

### Controller Tests（Route 控制器測試）
- **測試範圍**：僅測試 `POST /api/applications` route 的 Flask 路由層處理
- **測試方法**：使用 Flask test client mock `ApplicationService.create_application`，不依賴真實資料庫或 service 層
- **檔案位置**：`backend/tests/controller/test_application_controller_useCase1_4.py`
- **測試重點**：
  - HTTP 狀態碼與回傳結構
  - 請求JSON驗證（request validation）
  - JWT token處理（必要驗證）
  - 錯誤處理（重複申請、無效動物等）
  - Idempotency-Key支援

### Integration Tests（整合測試）
- **測試範圍**：測試完整的申請提交流程（route → service → SQLAlchemy → database）
- **測試方法**：建立真實測試資料庫，驗證端到端申請流程
- **檔案位置**：`backend/tests/integration/test_application_submit_integration.py`
- **測試重點**：
  - 完整申請流程驗證
  - 資料庫事務處理
  - 重複申請防護
  - 通知觸發驗證
  - 申請狀態管理

## Unit Tests（Service 單元測試）詳細設計

### 測試目標
- **測試對象**：`ApplicationService.create_application(applicant: User, data: Dict, idempotency_key: Optional[str])`
- **Mock 策略**：Mock SQLAlchemy ORM 查詢方法和 db.session，使用 monkeypatch 和 unittest.mock
- **業務邏輯重點**：申請驗證、重複檢查、資料儲存

### 核心測試案例

#### TC-U1.4-01: 正常申請提交測試
- **測試目的**：驗證正常情況下的申請建立（無冪等性鍵）
- **Use Case 對應**：主要流程步驟 3&4 - 提交申請並儲存
- **測試條件**：合法用戶、可申請動物、完整申請資料
- **Mock 設定**：
  - `Animal.query.filter_by().first()` 回傳PUBLISHED狀態動物
  - `Application.query.filter_by().filter().first()` 回傳None（無重複申請）
  - `db.session.add()` 和 `db.session.commit()` 成功執行
  - `notification_service.notify_application_submitted()` mock調用
- **驗證點**：
  - 申請資料正確儲存
  - 返回完整申請物件
  - 包含申請者和動物關聯資訊

#### TC-U1.4-02: 非一般會員權限檢查測試
- **測試目的**：驗證只有一般會員可以提交領養申請
- **Use Case 對應**：行為者限制 - 一般會員
- **測試條件**：收容所員工嘗試提交申請
- **Mock 設定**：不需要Mock，直接傳入SHELTER_MEMBER角色用戶
- **驗證點**：拋出 `PermissionDeniedError`，錯誤訊息指出只有一般會員可申請

#### TC-U1.4-03: 重複申請檢查測試
- **測試目的**：驗證防止同一用戶重複申請同一動物
- **Use Case 對應**：輔助說明 2 - 重複申請檢查
- **測試條件**：用戶已對該動物提交過申請
- **Mock 設定**：`Application.query.filter_by().filter().first()` 回傳既有申請記錄
- **驗證點**：拋出 `ConflictError`，錯誤訊息明確指出重複申請

#### TC-U1.4-04: 申請自己動物檢查測試
- **測試目的**：驗證用戶不能申請自己的動物
- **測試條件**：申請者ID等於動物擁有者ID
- **Mock 設定**：動物資料中ownerId與申請者ID相同
- **驗證點**：拋出 `BadRequestException`，錯誤訊息指出不能申請自己的動物

#### TC-U1.4-05: 必填欄位驗證測試
- **測試目的**：驗證申請資料必填欄位檢查
- **Use Case 對應**：輔助說明 1 - 必填欄位驗證
- **測試條件**：申請資料缺少必填欄位
- **Mock 設定**：不完整的CreateApplicationDto
- **驗證點**：拋出 `BadRequestException`，指出缺少的必填欄位

#### TC-U1.4-06: 動物不存在處理測試
- **測試目的**：驗證申請不存在動物的錯誤處理
- **測試條件**：無效的動物ID
- **Mock 設定**：`findUnique()` 回傳null
- **驗證點**：拋出 `NotFoundException`

#### TC-U1.4-07: 申請資料格式驗證測試
- **測試目的**：驗證申請問答資料格式正確性
- **測試條件**：answers欄位包含複雜JSON結構
- **Mock 設定**：包含多種問答格式的申請資料
- **驗證點**：
  - JSON格式正確儲存
  - 特殊字元正確處理
  - 資料長度限制檢查

#### TC-U1.4-08: 事務處理測試
- **測試目的**：驗證申請建立過程的事務完整性
- **測試條件**：申請建立過程中發生錯誤
- **Mock 設定**：模擬資料庫事務失敗
- **驗證點**：事務回滾，不留下不完整資料

## Controller Tests（控制器測試）詳細設計

### 測試目標
- **測試對象**：`POST /applications` route handler
- **Mock 策略**：Mock `ApplicationsService.create()` method
- **HTTP 層重點**：狀態碼、JSON結構、DTO驗證、錯誤處理

### 核心測試案例

#### TC-C1.4-01: 正常申請提交HTTP回應測試
- **測試目的**：驗證成功申請的HTTP回應
- **測試條件**：合法JWT token、完整申請資料
- **Mock 設定**：`applicationsService.create` 回傳成功申請
- **驗證點**：
  - status_code = 201
  - 回傳申請完整資訊
  - Content-Type 正確

#### TC-C1.4-02: DTO驗證測試
- **測試目的**：驗證請求Body的資料驗證
- **測試條件**：不完整或格式錯誤的申請資料
- **Mock 設定**：不調用service（DTO驗證階段阻止）
- **驗證點**：
  - status_code = 400
  - 錯誤訊息指出具體驗證失敗欄位

#### TC-C1.4-03: JWT token驗證測試
- **測試目的**：驗證必須登入才能提交申請
- **Use Case 對應**：行為者限制 - 一般會員
- **測試條件**：無Authorization header或無效token
- **Mock 設定**：不調用service（認證階段阻止）
- **驗證點**：
  - status_code = 401
  - 錯誤訊息指出需要登入

#### TC-C1.4-04: 重複申請錯誤處理測試
- **測試目的**：驗證重複申請的HTTP錯誤回應
- **測試條件**：合法請求但service拋出ConflictException
- **Mock 設定**：service拋出重複申請錯誤
- **驗證點**：
  - status_code = 409
  - 錯誤訊息用戶友好

#### TC-C1.4-05: 動物不可申請錯誤處理測試
- **測試目的**：驗證動物狀態不符時的錯誤回應
- **測試條件**：動物已被領養或其他不可申請狀態
- **Mock 設定**：service拋出BadRequestException
- **驗證點**：
  - status_code = 400
  - 錯誤訊息說明動物狀態問題

#### TC-C1.4-06: Idempotency-Key支援測試
- **測試目的**：驗證重複請求的冪等性支援
- **測試條件**：相同Idempotency-Key的重複請求
- **Mock 設定**：模擬重複請求處理邏輯
- **驗證點**：
  - 第二次請求回傳相同結果
  - 不重複建立申請記錄

#### TC-C1.4-07: 大型請求資料處理測試
- **測試目的**：驗證大量申請資料的處理能力
- **測試條件**：包含大量文字的申請資料
- **Mock 設定**：正常service回應
- **驗證點**：
  - 請求成功處理
  - 響應時間合理
  - 記憶體使用正常

## Integration Tests（整合測試）詳細設計

### 測試目標
- **測試範圍**：完整的申請提交流程
- **資料庫**：測試資料庫
- **資料準備**：建立真實使用者、動物、申請資料
- **端到端驗證**：業務流程完整性

### 核心測試案例

#### TC-I1.4-01: 完整申請提交流程測試
- **Use Case 對應**：主要流程完整驗證
- **測試條件**：建立真實使用者和動物資料，執行完整申請流程
- **驗證點**：
  - 申請成功建立並儲存到資料庫
  - 申請資料完整且正確
  - 關聯資訊（申請者、動物）正確建立
  - 申請時間戳記正確

#### TC-I1.4-02: 重複申請防護測試
- **Use Case 對應**：輔助說明 2 - 重複申請檢查
- **測試條件**：同一用戶對同一動物提交兩次申請
- **驗證點**：
  - 第一次申請成功
  - 第二次申請失敗並回傳409錯誤
  - 資料庫中只有一筆申請記錄

#### TC-I1.4-03: 並發申請處理測試
- **測試條件**：多個用戶同時對同一動物提交申請
- **驗證點**：
  - 所有申請都能正確處理
  - 沒有資料競爭問題
  - 申請順序正確記錄

#### TC-I1.4-04: 動物狀態變更影響測試
- **Use Case 對應**：先決條件 - 動物狀態限制
- **測試條件**：在申請過程中動物狀態變更為不可申請
- **驗證點**：
  - 申請被正確拒絕
  - 錯誤訊息準確
  - 資料庫狀態一致

#### TC-I1.4-05: 申請資料完整性測試
- **Use Case 對應**：主要流程步驟 2 - 填寫申請資訊
- **測試條件**：提交包含所有類型欄位的完整申請
- **驗證點**：
  - 所有欄位正確儲存
  - JSON資料正確序列化
  - 特殊字元和Unicode正確處理

#### TC-I1.4-06: 申請後動物狀態更新測試
- **測試條件**：成功提交申請後，檢查動物狀態是否適當更新
- **驗證點**：
  - 動物狀態可能變更為PENDING（依業務規則）
  - 狀態變更時間正確記錄
  - 其他欄位保持不變

#### TC-I1.4-07: 通知觸發驗證測試
- **Use Case 對應**：申請提交後的後續處理
- **測試條件**：成功提交申請
- **驗證點**：
  - 動物擁有者收到申請通知
  - 申請者收到確認通知
  - 通知內容正確

#### TC-I1.4-08: 申請撤回功能測試
- **Use Case 對應**：主要流程步驟 6 - 申請撤回功能
- **測試條件**：提交申請後立即測試撤回功能
- **驗證點**：
  - 申請可以成功撤回
  - 申請狀態變更為WITHDRAWN
  - 動物狀態恢復為AVAILABLE

#### TC-I1.4-09: 大量申請資料效能測試
- **測試條件**：提交包含大量文字和資料的申請
- **驗證點**：
  - 申請處理時間在合理範圍內
  - 記憶體使用正常
  - 資料庫查詢效率良好

#### TC-I1.4-10: 異常情況恢復測試
- **測試條件**：申請過程中模擬各種異常（網路中斷、資料庫錯誤）
- **驗證點**：
  - 系統能正確處理異常
  - 資料一致性保持
  - 用戶得到適當錯誤訊息

## 測試資料準備策略

### 申請測試資料工廠

```python
from unittest.mock import Mock
from uuid import uuid4
from app.models.user import User, UserRole
from app.models.animal import Animal, AnimalStatus, Species
from app.models.application import Application, ApplicationStatus

def create_test_application_data(options=None):
    """創建測試申請資料工廠"""
    default_options = {
        'create_user': True,
        'create_animal': True,
        'animal_status': AnimalStatus.PUBLISHED,
        'user_role': UserRole.GENERAL_MEMBER,
    }
    if options:
        default_options.update(options)
    
    # 建立申請者Mock
    applicant = None
    if default_options['create_user']:
        applicant = Mock(spec=User)
        applicant.user_id = str(uuid4())
        applicant.role = default_options['user_role']
        applicant.username = 'test_user'
        applicant.email = 'applicant@test.com'
        applicant.primary_shelter_id = None
    
    # 建立動物擁有者Mock
    owner = Mock(spec=User)
    owner.user_id = str(uuid4())
    owner.role = UserRole.GENERAL_MEMBER
    owner.username = 'animal_owner'
    owner.email = 'owner@test.com'
    
    # 建立動物Mock
    animal = None
    if default_options['create_animal']:
        animal = Mock(spec=Animal)
        animal.animal_id = str(uuid4())
        animal.name = '小白'
        animal.species = Species.DOG
        animal.status = default_options['animal_status']
        animal.owner_id = owner.user_id
        animal.created_by = owner.user_id
        animal.deleted_at = None
    
    # 申請資料範本
    application_data = {
        'animal_id': animal.animal_id if animal else str(uuid4()),
        'type': 'ADOPTION',
        'contact_phone': '0912345678',
        'contact_address': '台北市大安區復興南路100號',
        'occupation': '軟體工程師',
        'housing_type': '公寓',
        'has_experience': True,
        'reason': '希望給狗狗一個溫暖的家',
        'notes': '平日在家工作，有充足時間照顧動物',
        'attachments': ['photo1.jpg', 'cert.pdf']
    }
    
    return {
        'applicant': applicant,
        'owner': owner,
        'animal': animal,
        'application_data': application_data
    }
```

## Mock 策略詳細指南

### Unit Tests Mock 範例

```python
import pytest
from unittest.mock import Mock, patch
from app.services.application_service import ApplicationService
from app.models.application import Application, ApplicationStatus
from app.models.animal import Animal, AnimalStatus
from app.exceptions import ConflictError

class TestApplicationServiceCreateApplication:
    """測試 ApplicationService.create_application() 的業務邏輯"""
    
    def test_successful_application_creation(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal, mock_valid_application_data
    ):
        """正常申請提交測試"""
        # Mock Application.query 的複雜鏈式調用
        mock_app_query = Mock()
        
        def mock_filter_by(*args, **kwargs):
            mock_chain = Mock()
            mock_chain.filter.return_value.first.return_value = None  # 無重複申請
            mock_chain.first.return_value = None  # 冪等性檢查
            return mock_chain
        
        mock_app_query.filter_by = mock_filter_by
        
        # Mock Application 構造函數
        mock_application_instance = Mock(spec=Application)
        mock_application_instance.animal_id = mock_valid_application_data['animal_id']
        mock_application_instance.applicant_id = mock_general_user.user_id
        mock_application_instance.status = ApplicationStatus.PENDING
        
        # Mock Animal.query 和 Application.query
        with patch('app.services.application_service.Animal') as mock_animal_class, \
             patch('app.services.application_service.Application') as mock_application_class:
             
            # 設置 Animal 查詢回傳可申請動物
            mock_animal_class.query.filter_by.return_value.first.return_value = mock_available_animal
            
            # 設置 Application 查詢回傳無重複
            mock_application_class.query.filter_by = mock_filter_by
            mock_application_class.return_value = mock_application_instance
            
            # Mock db.session
            mock_session = Mock()
            mock_session.add = Mock()
            mock_session.commit = Mock()
            mock_session.execute.return_value.scalar.return_value = 5  # MAX ID
            monkeypatch.setattr('app.services.application_service.db.session', mock_session)
            
            # Mock notification service
            mock_notification_service = Mock()
            monkeypatch.setattr(
                'app.services.application_service.notification_service',
                mock_notification_service
            )
            
            # 執行測試
            result = ApplicationService.create_application(
                applicant=mock_general_user,
                data=mock_valid_application_data
            )
            
            # 驗證結果
            assert result == mock_application_instance
            assert result.animal_id == mock_valid_application_data['animal_id']
            assert result.applicant_id == mock_general_user.user_id
            
            # 驗證資料庫操作
            mock_session.add.assert_called_once_with(mock_application_instance)
            mock_session.commit.assert_called_once()
    
    def test_prevent_duplicate_application(
        self, app_context, monkeypatch, mock_general_user,
        mock_available_animal, mock_valid_application_data
    ):
        """重複申請檢查測試"""
        # Mock 既有申請
        existing_application = Mock(spec=Application)
        existing_application.application_id = 'existing-123'
        existing_application.applicant_id = mock_general_user.user_id
        
        # Mock Application.query 返回重複申請
        with patch('app.services.application_service.Application') as mock_application_class:
            mock_filter_chain = Mock()
            mock_filter_chain.filter.return_value.first.return_value = existing_application
            mock_application_class.query.filter_by.return_value = mock_filter_chain
            
            # Mock Animal.query
            with patch('app.services.application_service.Animal') as mock_animal_class:
                mock_animal_class.query.filter_by.return_value.first.return_value = mock_available_animal
                
                # 測試應該拋出衝突錯誤
                with pytest.raises(ConflictError) as exc_info:
                    ApplicationService.create_application(
                        applicant=mock_general_user,
                        data=mock_valid_application_data
                    )
                
                assert '您已對此動物提交申請' in str(exc_info.value)
```
```

## 測試執行與覆蓋率

### 執行指令

```bash
# 執行所有 Use Case 1.4 相關測試
python -m pytest tests/ -k "useCase1_4" -v

# 只執行 Unit Tests (Service 層)
python -m pytest tests/unit/test_application_service_useCase1_4.py -v

# 只執行 Controller Tests
python -m pytest tests/controller/test_application_controller_useCase1_4.py -v

# 只執行 Integration Tests
python -m pytest tests/integration/test_application_submit_integration.py -v

# 執行並顯示覆蓋率
python -m pytest tests/ -k "useCase1_4" --cov=app --cov-report=html

# 執行特定優先級測試（P0測試）
python -m pytest tests/ -k "test_successful_application_creation or test_prevent_duplicate" -v

# 執行所有測試並顯示詳細輸出
python -m pytest tests/ -v --tb=short
```

### 覆蓋率目標

- **Service 層申請邏輯**: > 95%
- **Controller 層HTTP處理**: > 90% 
- **整合測試場景覆蓋**: > 85%

## 測試優先順序

### P0（核心功能）
- 正常申請提交 (TC-U1.4-01, TC-C1.4-01, TC-I1.4-01)
- 重複申請防護 (TC-U1.4-03, TC-C1.4-04, TC-I1.4-02)
- 動物狀態驗證 (TC-U1.4-02, TC-C1.4-05)
- JWT認證驗證 (TC-C1.4-03)

### P1（重要功能）  
- 申請資料完整性 (TC-I1.4-05)
- DTO驗證 (TC-C1.4-02)
- 必填欄位驗證 (TC-U1.4-05)
- 動物不存在處理 (TC-U1.4-06)

### P2（穩定性）
- 並發申請處理 (TC-I1.4-03)
- Idempotency支援 (TC-C1.4-06)
- 事務處理 (TC-U1.4-08)
- 通知觸發 (TC-I1.4-07)

### P3（效能與特殊情況）
- 大量資料處理 (TC-C1.4-07, TC-I1.4-09)
- 異常情況恢復 (TC-I1.4-10)
- 申請撤回功能 (TC-I1.4-08)

## 安全性測試考量

對於申請提交功能，建議加入安全性測試：

```typescript
describe('Application Security Tests', () => {
  it('should prevent SQL injection in application data', async () => {
    const maliciousData = {
      listingId: 'valid-uuid',
      answers: JSON.stringify({
        reason: "'; DROP TABLE applications; --"
      })
    };

    await expect(service.create('user-uuid', maliciousData))
      .resolves.not.toThrow();
    // 驗證資料正確儲存，沒有執行惡意SQL
  });

  it('should sanitize XSS attempts in application text', async () => {
    const xssData = {
      listingId: 'valid-uuid', 
      answers: JSON.stringify({
        reason: '<script>alert("xss")</script>'
      })
    };

    const result = await service.create('user-uuid', xssData);
    const parsedAnswers = JSON.parse(result.answers);
    
    // 驗證惡意腳本被適當處理
    expect(parsedAnswers.reason).not.toContain('<script>');
  });
});
```