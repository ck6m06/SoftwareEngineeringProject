# Use Case 1.1 — 動物列表瀏覽：測試架構設計

檔案位置：`specs/document/test_plan/unit_integration_test/useCase1_1_test_design.md`

目的：為「動物列表瀏覽（Use Case 1.1）」撰寫完整的三層測試架構設計，包含 Unit Tests、Controller Tests、Integration Tests，幫助後端開發/測試人員實作 pytest 測試。

前提：後端採用 Flask + SQLAlchemy；專案已有 `TestingConfig`（`sqlite:///:memory:`）與 Flask app factory `create_app` 可用於測試環境。

## 測試架構分層

### Unit Tests（Service 單元測試）
- **測試範圍**：僅測試 service 層業務邏輯
- **測試方法**：使用 `monkeypatch` mock SQLAlchemy ORM (`Animal.query`)，不依賴真實資料庫
- **檔案位置**：`proj_new/backend/tests/unit/test_animals_list_service_useCase1_1.py`
- **測試重點**：
  - `animal_service.list_animals()` 業務邏輯
  - 過濾條件轉換（species enum、status 預設值）
  - 權限邏輯（訪客 vs 擁有者 vs 收容所成員）
  - 搜尋/排序/分頁邏輯
  - 異常處理（ValidationError）

### Controller Tests（Route 控制器測試）
- **測試範圍**：僅測試 route/controller 層的邏輯
- **測試方法**：使用 `monkeypatch` mock `animal_service.list_animals`，不依賴真實資料庫或 service 層
- **檔案位置**：`proj_new/backend/tests/unit/test_animals_list_controller_useCase1_1.py`
- **測試重點**：
  - HTTP 狀態碼與回傳結構
  - Query params 解析與傳遞
  - JWT token 處理（optional auth）
  - 錯誤處理（BusinessException vs 一般 Exception）

### Integration Tests（整合測試）
- **測試範圍**：測試完整的請求流程（route → service → ORM → database）
- **測試方法**：建立真實測試資料（使用 SQLite in-memory），驗證端到端行為
- **檔案位置**：`proj_new/backend/tests/integration/test_animals_list_integration_useCase1_1.py`
- **測試重點**：
  - 資料排序（created_at 降冪）
  - 必要欄位完整性  
  - 訪客可見性（僅 PUBLISHED 狀態）
  - 分頁、過濾、搜尋邏輯
  - ORM 查詢正確性

## Unit Tests（Service 單元測試）詳細設計

### 測試目標
- **測試對象**：`app.services.animal_service.AnimalService.list_animals()`
- **Mock 策略**：Mock SQLAlchemy ORM (`Animal.query` 及其鏈式調用)
- **業務邏輯重點**：過濾、權限、搜尋、分頁、排序

### 核心測試案例

#### TC-U1.1-01: 預設狀態過濾測試
- **測試目的**：驗證當未指定 status 時，預設過濾為 PUBLISHED
- **Use Case 對應**：輔助說明 3 - 『已領養』或『下架』動物不顯示
- **測試條件**：`filters={}`, `current_user_id=None`
- **Mock 設定**：`Animal.query` 鏈
- **驗證點**：`query.filter_by.assert_called_with(status=AnimalStatus.PUBLISHED)`

#### TC-U1.1-02: 物種過濾邏輯測試
- **測試目的**：驗證 species 字串正確轉換為 Species enum
- **測試條件**：`filters={'species': 'DOG'}`
- **驗證點**：`query.filter_by.assert_called_with(species=Species.DOG)`

#### TC-U1.1-03: 無效物種驗證測試
- **測試目的**：驗證無效 species 拋出 ValidationError
- **測試條件**：`filters={'species': 'INVALID_SPECIES'}`
- **驗證點**：`pytest.raises(ValidationError)` 且錯誤訊息包含「無效的物種值」

#### TC-U1.1-04: 分頁限制測試
- **測試目的**：驗證 per_page 被限制在 100 以內
- **測試條件**：`filters={'per_page': 150}`
- **驗證點**：`query.paginate.assert_called_with(per_page=100, ...)`

#### TC-U1.1-05: 關鍵字搜尋測試
- **測試目的**：驗證 q 參數觸發多欄位 OR 搜尋
- **測試條件**：`filters={'q': 'fluffy'}`
- **Mock 額外設定**：`db.or_()` function
- **驗證點**：`query.filter.assert_called_with(or_condition)`

#### TC-U1.1-06: 排序規則測試
- **測試目的**：驗證固定依照 created_at 降冪排序
- **Use Case 對應**：主要流程步驟 3 - 依『最新上架』順序
- **Mock 設定**：`Animal.created_at.desc()`
- **驗證點**：`query.order_by.assert_called_with(desc_expression)`

#### TC-U1.1-07: 訪客權限測試
- **測試目的**：驗證訪客查看他人動物的權限限制
- **Use Case 對應**：輔助說明 1 - 訪客僅能瀏覽公開動物
- **測試條件**：`filters={'owner_id': 123}`, `current_user_id=None`
- **驗證點**：同時過濾 owner_id 和 status=PUBLISHED

#### TC-U1.1-08: 收容所成員權限測試
- **測試目的**：驗證收容所成員查看自己動物時的擴展權限
- **測試條件**：current_user 是 SHELTER_MEMBER 且查詢自己
- **Mock 設定**：`db.session.get()` 回傳 mock user, `db.or_()` function
- **驗證點**：使用 OR 條件查詢個人+收容所動物

#### TC-U1.1-09: 回傳結構測試
- **測試目的**：驗證 service 回傳正確的 JSON 結構
- **Mock 設定**：pagination.items 包含 mock animal objects
- **驗證點**：
  - 回傳包含 'animals', 'total', 'page', 'per_page', 'pages' keys
  - animal.to_dict(include_relations=True) 被正確呼叫

## Controller Tests（控制器測試）詳細設計

### 測試目標
- **測試對象**：`/api/animals` route handler  
- **Mock 策略**：Mock `animal_service.list_animals()` function
- **HTTP 層重點**：狀態碼、JSON 結構、參數解析、錯誤處理

### 核心測試案例

#### TC-C1.1-01: 正常回應測試
- **測試目的**：驗證 route 正確處理 service 回傳並產生 HTTP 200
- **Mock 設定**：`animal_service.list_animals` 回傳固定結構
- **驗證點**：status_code=200, 回傳 JSON 與 mock 一致

#### TC-C1.1-02: 參數傳遞測試
- **測試目的**：驗證 route 正確解析 query params 並傳遞給 service
- **測試條件**：`?species=DOG&page=2&per_page=10&q=fluffy`
- **Mock 設定**：捕獲 service 傳入參數
- **驗證點**：filters dict 包含正確的參數值

#### TC-C1.1-03: JWT 處理測試
- **測試目的**：驗證 route 正確處理可選的 JWT token
- **測試條件**：無 Authorization header
- **Mock 設定**：捕獲 current_user_id 參數
- **驗證點**：current_user_id=None

#### TC-C1.1-04: 一般例外處理測試
- **測試目的**：驗證 route 正確處理 service 拋出的 RuntimeError
- **Mock 設定**：service 拋出 RuntimeError
- **驗證點**：status_code=500, 回傳 JSON 包含錯誤訊息

#### TC-C1.1-05: 業務例外處理測試
- **測試目的**：驗證 route 正確處理 BusinessException
- **Mock 設定**：service 拋出 ValidationError
- **驗證點**：status_code=400, 錯誤訊息正確傳遞

## Integration Tests（整合測試）詳細設計

### 測試目標
- **測試範圍**：完整的 route → service → ORM → database 流程
- **資料庫**：SQLite in-memory
- **資料準備**：建立真實測試資料
- **端到端驗證**：業務邏輯正確性

### 核心測試案例

#### TC-I1.1-01: 基本列表功能
- **Use Case 對應**：主要流程步驟 2 - 顯示動物清單
- **測試條件**：建立 3 筆 PUBLISHED 動物
- **驗證點**：
  - 回傳 3 筆動物
  - 依 created_at 降冪排序
  - 包含必要欄位 (name, species, age, sex)

#### TC-I1.1-02: 狀態過濾功能
- **Use Case 對應**：輔助說明 3 - 排除已領養/下架動物
- **測試條件**：建立 PUBLISHED/ADOPTED/DRAFT 各 1 筆
- **驗證點**：訪客只能看到 PUBLISHED (1 筆)

#### TC-I1.1-03: 物種過濾功能
- **測試條件**：建立 DOG/CAT 各 2 筆, `?species=DOG`
- **驗證點**：只回傳 2 筆 DOG

#### TC-I1.1-04: 分頁功能
- **測試條件**：建立 25 筆動物, `?page=2&per_page=10`
- **驗證點**：
  - 回傳 10 筆 (第 2 頁)
  - total=25, page=2, pages=3

#### TC-I1.1-05: 關鍵字搜尋功能
- **測試條件**：建立動物 name="Fluffy", description="cute dog", `?q=fluffy`
- **驗證點**：能找到該動物 (case-insensitive)

#### TC-I1.1-06: 會員vs訪客權限
- **Use Case 對應**：輔助說明 1&2 - 登入角色差異
- **測試條件**：建立動物包含敏感資訊
- **驗證點**：會員能看到更多欄位

#### TC-I1.1-07: 排序功能
- **Use Case 對應**：主要流程步驟 3 - 依最新上架排序
- **測試條件**：建立 3 筆動物，不同 created_at
- **驗證點**：按 created_at 降冪排序

#### TC-I1.1-08: 空結果處理
- **測試條件**：無符合條件的動物
- **驗證點**：回傳空陣列但結構正確

## 測試實作指南

### 共通 Fixture 建議

```python
@pytest.fixture
def app():
    """建立測試 Flask app"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """測試客戶端"""
    return app.test_client()

@pytest.fixture
def animal_factory():
    """動物資料工廠"""
    def _create_animal(**kwargs):
        defaults = {
            'name': 'TestAnimal',
            'species': Species.DOG,
            'age': 2,
            'sex': Sex.MALE,
            'status': AnimalStatus.PUBLISHED,
            'owner_id': 1
        }
        defaults.update(kwargs)
        animal = Animal(**defaults)
        db.session.add(animal)
        db.session.commit()
        return animal
    return _create_animal
```

### Mock 策略指南

**Unit Tests (Service層)**：
```python
# Mock SQLAlchemy ORM
mock_query = Mock()
mock_query.filter_by.return_value = mock_query
mock_query.order_by.return_value = mock_query
mock_query.paginate.return_value = mock_pagination
monkeypatch.setattr('app.models.animal.Animal.query', mock_query)
```

**Controller Tests**：
```python
# Mock service function
def mock_list_animals(filters, current_user_id=None):
    return {'animals': [], 'total': 0, 'page': 1, 'per_page': 20, 'pages': 0}
monkeypatch.setattr('app.blueprints.animals.animal_service.list_animals', mock_list_animals)
```

## 測試優先順序

### P0（必要）
- 基本列表功能 (TC-I1.1-01)
- 狀態過濾 (TC-I1.1-02) 
- 排序功能 (TC-I1.1-07)
- 正常回應 (TC-C1.1-01)
- 預設狀態過濾 (TC-U1.1-01)

### P1（重要）  
- 分頁功能 (TC-I1.1-04)
- 物種過濾 (TC-I1.1-03)
- 關鍵字搜尋 (TC-I1.1-05)
- 參數傳遞 (TC-C1.1-02)
- 物種過濾邏輯 (TC-U1.1-02)

### P2（優化）
- 會員權限差異 (TC-I1.1-06)
- 錯誤處理 (TC-C1.1-04, TC-C1.1-05)
- 無效物種驗證 (TC-U1.1-03)
- 空結果處理 (TC-I1.1-08)

## 執行指令

```bash
# 執行所有 Use Case 1.1 相關測試
pytest proj_new/backend/tests/ -k "useCase1_1" -v

# 只執行 Unit Tests (Service 層)
pytest proj_new/backend/tests/unit/test_animals_list_service_useCase1_1.py -v

# 只執行 Controller Tests  
pytest proj_new/backend/tests/unit/test_animals_list_controller_useCase1_1.py -v

# 只執行 Integration Tests
pytest proj_new/backend/tests/integration/test_animals_list_integration_useCase1_1.py -v

# 執行並顯示覆蓋率
pytest proj_new/backend/tests/ -k "useCase1_1" --cov=app.services.animal_service --cov=app.blueprints.animals -v
```
