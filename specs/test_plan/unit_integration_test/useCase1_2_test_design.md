# Use Case 1.2 — 動物搜尋篩選：測試架構設計

檔案位置：`specs/test_plan/unit_integration_test/useCase1_2_test_design.md`

目的：為「動物搜尋篩選（Use Case 1.2）」撰寫完整的三層測試架構設計，包含 Unit Tests、Controller Tests、Integration Tests，幫助後端開發/測試人員實作 pytest 測試。

前提：後端採用 Flask + SQLAlchemy；專案已有 `TestingConfig`（`sqlite:///:memory:`）與 Flask app factory `create_app` 可用於測試環境。

## 業務需求回顧

**使用案例1.2 動物搜尋篩選**
- 填表人：系統分析師
- 商業流程編號：BP-ANIMAL-003
- 行為者：所有使用者
- 內容概述：本使用案例描述使用者如何搜尋與篩選動物資料。
- 先決條件：使用者在「1.1 動物列表瀏覽」頁面中。
- 後置條件：當搜尋條件無符合結果，顯示「無符合條件的動物」訊息。

**主要流程：**
1. 畫面初始時，所有篩選條件為預設值。
2. 使用者選擇篩選條件，包括物種、年齡、性別、縣市等。
3. 使用者輸入關鍵字進行搜尋。
4. 使用者按下「搜尋」按鈕。
5. 系統依輸入條件的交集，將動物資料以清單方式呈現於螢幕畫面上。
6. 系統顯示符合條件的動物數量。

**輔助說明：**
- 關鍵字搜尋範圍包含動物名稱、品種、描述資訊。
- 多條件搜尋時，系統以AND邏輯處理。
- 搜尋結果最多顯示100筆，建議使用者縮小搜尋範圍。

## 測試架構分層

### Unit Tests（Service 單元測試）
- **測試範圍**：僅測試 `animal_service.py` 中的搜尋篩選業務邏輯
- **測試方法**：使用 `monkeypatch` mock SQLAlchemy ORM (`Animal.query`)，不依賴真實資料庫
- **檔案位置**：`proj_new/backend/tests/unit/test_animals_search_service_useCase1_2.py`
- **測試重點**：
  - 多重篩選條件組合邏輯（AND 邏輯）
  - 關鍵字搜尋範圍（名稱、品種、描述）
  - 年齡範圍篩選邏輯
  - 性別與物種篩選
  - 地區篩選邏輯
  - 結果數量限制（最多100筆）

### Controller Tests（Route 控制器測試）
- **測試範圍**：僅測試 `/api/animals` route 的搜尋參數處理
- **測試方法**：使用 `monkeypatch` mock `animal_service.list_animals`，不依賴真實資料庫或 service 層
- **檔案位置**：`proj_new/backend/tests/unit/test_animals_search_controller_useCase1_2.py`
- **測試重點**：
  - 搜尋參數解析與驗證
  - 複雜查詢字串處理
  - 參數預設值處理
  - 無效參數錯誤回應

### Integration Tests（整合測試）
- **測試範圍**：測試完整的搜尋篩選流程（route → service → ORM → database）
- **測試方法**：建立真實測試資料（使用 SQLite in-memory），驗證端到端搜尋行為
- **檔案位置**：`proj_new/backend/tests/integration/test_animals_search_integration_useCase1_2.py`
- **測試重點**：
  - 多條件組合搜尋（AND 邏輯）
  - 關鍵字全文搜尋功能
  - 空搜尋結果處理
  - 搜尋結果數量統計
  - 複雜查詢效能驗證

## Unit Tests（Service 單元測試）詳細設計

### 測試目標
- **測試對象**：`app.services.animal_service.AnimalService.list_animals()` 的搜尋篩選邏輯
- **Mock 策略**：Mock SQLAlchemy ORM (`Animal.query` 鏈式調用) 和 `db` 對象
- **業務邏輯重點**：多重篩選、關鍵字搜尋、AND 邏輯組合
- **檔案位置**：`proj_new/backend/tests/unit/test_animals_search_service_useCase1_2_clean.py`

### 核心測試案例

#### TC-U1.2-01: 物種篩選邏輯測試 (test_species_filter_conversion)
- **測試目的**：驗證 species 篩選正確轉換為 enum 並套用
- **Use Case 對應**：主要流程步驟 2 - 選擇篩選條件（物種）
- **測試條件**：`filters={'species': 'DOG'}`
- **Mock 設定**：完整 Mock 鏈 `Animal.query → filter_by → order_by → paginate`
- **驗證點**：
  - `query.filter_by.assert_any_call(deleted_at=None)` (基礎查詢)
  - `filter_by.filter_by.assert_any_call(species=Species.DOG)` (物種篩選)
  - 結果結構包含 'animals', 'total' 等欄位

#### TC-U1.2-02: 年齡範圍篩選邏輯測試 (test_age_range_filter_logic)
- **測試目的**：驗證年齡參數的業務邏輯和年齡範圍邏輯的正確性
- **Use Case 對應**：主要流程步驟 2 - 選擇篩選條件（年齡）
- **測試方法**：純業務邏輯測試，不依賴複雜的 SQLAlchemy Mock
- **驗證點**：
  - `validate_age_parameters(12, None) == True` (有最小年齡)
  - `validate_age_parameters(None, 36) == True` (有最大年齡)
  - `validate_age_parameters(None, None) == False` (無年齡參數)
  - `validate_age_range(12, 36) == True` (合理範圍)
  - `validate_age_range(36, 12) == False` (不合理範圍)

#### TC-U1.2-03: 性別篩選邏輯測試 (test_sex_filter_conversion)
- **測試目的**：驗證 sex 篩選正確轉換為 enum 並套用
- **Use Case 對應**：主要流程步驟 2 - 選擇篩選條件（性別）
- **測試條件**：`filters={'sex': 'FEMALE'}`
- **Mock 設定**：完整 Mock 鏈，包含 pagination 結果
- **驗證點**：
  - `query.filter_by.assert_any_call(deleted_at=None)`
  - `filter_by.filter_by.assert_any_call(sex=Sex.FEMALE)`
  - 結果結構正確

#### TC-U1.2-04: 關鍵字全文搜尋測試 (test_keyword_search_across_multiple_fields)
- **測試目的**：驗證關鍵字搜尋涵蓋名稱、品種、描述（OR 邏輯）
- **Use Case 對應**：主要流程步驟 3 - 輸入關鍵字搜尋；輔助說明 1 - 搜尋範圍
- **測試條件**：`filters={'q': 'Golden Retriever'}`
- **Mock 設定**：
  - 完整 Mock 鏈，支援鏈式 `filter_by` 調用
  - Mock `Animal.name.like`, `Animal.description.like`, `Animal.breed.like`
  - Mock `or_` 函數
  - 使用 `configure_mock` 設定 pagination 屬性
- **驗證點**：
  - `mock_or.called` (使用 OR 邏輯)
  - `mock_animal.name.like.called` (搜尋 name 欄位)
  - `mock_animal.description.like.called` (搜尋 description 欄位)
  - `mock_animal.breed.like.called` (搜尋 breed 欄位)
  - 最終資料處理正確（to_dict 調用）
  - 分頁資訊正確

#### TC-U1.2-05: 多條件AND邏輯測試 (test_multiple_conditions_and_logic)
- **測試目的**：驗證多個篩選條件同時套用（AND 邏輯）
- **Use Case 對應**：輔助說明 2 - 多條件搜尋以AND邏輯處理
- **測試條件**：`filters={'species': 'DOG', 'sex': 'MALE', 'min_age': 1, 'max_age': 3, 'q': 'cute'}`
- **Mock 設定**：
  - 支援多次 `filter_by` 和 `filter` 的 Mock 鏈
  - Mock SQLite 年齡計算（`func.julianday`）
  - Mock Animal 欄位屬性和 OR 邏輯
- **驗證點**：
  - `mock_filter_by.filter_by.call_count >= 3` (多個 filter_by 條件)
  - `mock_func.julianday.called` (年齡篩選邏輯)
  - `mock_or.called` (關鍵字搜尋邏輯)
  - 結果結構完整

#### TC-U1.2-06: 地區篩選邏輯測試 (test_region_filter_logic)
- **測試目的**：驗證 region 篩選使用複雜的 subquery 邏輯
- **Use Case 對應**：主要流程步驟 2 - 選擇篩選條件（縣市）
- **測試條件**：`filters={'region': '台北市'}`
- **Mock 設定**：
  - Mock `exists()` 子查詢函數
  - Mock `or_` 和 `and_` 邏輯函數
  - Mock `exists().where()` 鏈式調用
- **驗證點**：
  - `mock_exists.called` (exists 子查詢被調用)
  - `mock_or.called` (合併 shelter 和 user 地區條件)
  - `mock_filter_by.filter.called` (filter 被應用)

#### TC-U1.2-07: 結果數量限制測試 (test_per_page_limit_enforcement)
- **測試目的**：驗證搜尋結果限制在100筆內
- **Use Case 對應**：輔助說明 3 - 搜尋結果最多顯示100筆
- **測試條件**：`filters={'per_page': 200}` (超過限制)
- **Mock 設定**：完整 Mock 鏈，mock_paginate 回傳 per_page=100
- **驗證點**：
  - `mock_order_by.paginate.assert_called_once_with(page=1, per_page=100, error_out=False)`
  - per_page 被正確限制為 100

#### TC-U1.2-08: 空篩選預設行為測試 (test_empty_filters_default_behavior)
- **測試目的**：驗證無篩選條件時只套用預設狀態篩選（PUBLISHED）
- **Use Case 對應**：主要流程步驟 1 - 預設值處理
- **測試條件**：`filters={}` (空篩選條件)
- **Mock 設定**：基本 Mock 鏈
- **驗證點**：
  - `mock_query.filter_by.assert_any_call(deleted_at=None)` (基礎查詢)
  - `mock_filter_by.filter_by.assert_any_call(status=AnimalStatus.PUBLISHED)` (預設狀態)

#### TC-U1.2-09: 無效篩選值處理測試
- **物種測試** (test_invalid_species_validation)：
  - **測試條件**：`filters={'species': 'INVALID_ANIMAL'}`
  - **驗證點**：`pytest.raises(ValidationError)` 且訊息包含 '無效的物種值'
- **性別測試** (test_invalid_sex_validation)：
  - **測試條件**：`filters={'sex': 'UNKNOWN_GENDER'}`
  - **驗證點**：`pytest.raises(ValidationError)` 且訊息包含 '無效的性別值'

#### TC-U1.2-10: 關鍵字特殊字元處理測試 (test_keyword_special_character_handling)
- **測試目的**：驗證關鍵字包含特殊字元時被正確處理
- **測試條件**：`filters={'q': "小白's 100% 可愛貓咪"}` (包含特殊字元)
- **Mock 設定**：
  - 完整 Mock 鏈和 Animal 欄位屬性
  - Mock OR 邏輯函數
- **驗證點**：
  - `mock_or.called` (OR 函數被調用)
  - 各搜尋欄位的 like 方法被調用
  - 不會因特殊字元導致錯誤

## Controller Tests（控制器測試）詳細設計

### 測試目標
- **測試對象**：`/api/animals` route 的搜尋參數處理
- **Mock 策略**：Mock `animal_service.list_animals()` function
- **HTTP 層重點**：複雜查詢字串解析、參數驗證、錯誤回應

### 核心測試案例

#### TC-C1.2-01: 複雜查詢字串解析測試
- **測試目的**：驗證 route 正確解析複雜的搜尋參數
- **測試條件**：`?species=DOG&sex=MALE&min_age=1&max_age=5&q=golden%20retriever&region=台北市`
- **Mock 設定**：捕獲 service 傳入參數
- **驗證點**：filters dict 包含所有正確解析的參數

#### TC-C1.2-02: 參數型別轉換測試
- **測試目的**：驗證年齡參數正確轉換為整數
- **測試條件**：`?min_age=2&max_age=five` (無效整數)
- **Mock 設定**：不需要 mock（參數驗證階段）
- **驗證點**：status_code=400, 錯誤訊息指出無效的年齡參數

#### TC-C1.2-03: URL編碼處理測試
- **測試目的**：驗證中文和特殊字元的 URL 編碼處理
- **測試條件**：`?q=%E9%BB%83%E9%87%91%E7%8D%B5%E7%8A%AC&region=%E5%8F%B0%E5%8C%97%E5%B8%82`
- **Mock 設定**：捕獲解碼後的參數
- **驗證點**：中文字元正確解碼

#### TC-C1.2-04: 空參數處理測試
- **測試目的**：驗證空字串參數的處理
- **測試條件**：`?species=&q=&min_age=`
- **Mock 設定**：捕獲處理後的參數
- **驗證點**：空參數被正確忽略

#### TC-C1.2-05: 分頁參數組合測試
- **測試目的**：驗證搜尋結合分頁的參數處理
- **測試條件**：`?q=cute&page=2&per_page=10`
- **Mock 設定**：捕獲完整參數組合
- **驗證點**：搜尋和分頁參數同時正確傳遞

#### TC-C1.2-06: 重複參數處理測試
- **測試目的**：驗證重複查詢參數的處理方式
- **測試條件**：`?species=DOG&species=CAT`
- **Mock 設定**：檢查最終參數值
- **驗證點**：取最後一個值或回傳適當錯誤

## Integration Tests（整合測試）詳細設計

### 測試目標
- **測試範圍**：完整的搜尋篩選流程
- **資料庫**：SQLite in-memory
- **資料準備**：建立多樣化測試資料
- **端到端驗證**：搜尋邏輯正確性

### 核心測試案例

#### TC-I1.2-01: 基本關鍵字搜尋功能
- **Use Case 對應**：主要流程步驟 3&4 - 關鍵字搜尋；輔助說明 1 - 搜尋範圍
- **測試條件**：建立動物 name="Golden", breed="Retriever", description="friendly dog", 搜尋 `?q=golden`
- **驗證點**：
  - 能正確找到該動物
  - 搜尋不區分大小寫
  - 搜尋涵蓋名稱、品種、描述

#### TC-I1.2-02: 物種篩選功能
- **Use Case 對應**：主要流程步驟 2&5 - 物種篩選
- **測試條件**：建立 DOG/CAT/RABBIT 各 2 筆, 搜尋 `?species=DOG`
- **驗證點**：只回傳 2 筆 DOG，排除其他物種

#### TC-I1.2-03: 年齡範圍篩選功能
- **Use Case 對應**：主要流程步驟 2&5 - 年齡篩選
- **測試條件**：建立年齡 1,3,5,7,9 歲各 1 筆, 搜尋 `?min_age=3&max_age=7`
- **驗證點**：只回傳 3,5,7 歲共 3 筆

#### TC-I1.2-04: 性別篩選功能
- **Use Case 對應**：主要流程步驟 2&5 - 性別篩選
- **測試條件**：建立 MALE/FEMALE 各 3 筆, 搜尋 `?sex=FEMALE`
- **驗證點**：只回傳 3 筆 FEMALE

#### TC-I1.2-05: 多重條件AND邏輯測試
- **Use Case 對應**：輔助說明 2 - 多條件AND邏輯
- **測試條件**：建立多樣動物，搜尋 `?species=DOG&sex=MALE&min_age=2&max_age=4&q=friendly`
- **驗證點**：
  - 只回傳同時符合所有條件的動物
  - 驗證AND邏輯正確運作
  - 確認搜尋結果數量正確

#### TC-I1.2-06: 地區篩選功能
- **Use Case 對應**：主要流程步驟 2&5 - 縣市篩選
- **測試條件**：建立不同地區動物，搜尋 `?region=台北市`
- **驗證點**：只回傳台北市的動物

#### TC-I1.2-07: 空搜尋結果處理
- **Use Case 對應**：後置條件 - 無符合條件顯示訊息
- **測試條件**：搜尋不存在的條件組合 `?species=DOG&q=notexist`
- **驗證點**：
  - 回傳空陣列
  - total=0
  - 結構完整（不會出錯）

#### TC-I1.2-08: 結果數量限制測試
- **Use Case 對應**：輔助說明 3 - 最多100筆限制
- **測試條件**：建立 120 筆符合條件的動物
- **驗證點**：
  - 最多回傳 100 筆
  - total 顯示實際總數 120
  - 分頁資訊正確

#### TC-I1.2-09: 關鍵字部分匹配測試
- **測試條件**：建立動物 name="小黑", 搜尋 `?q=黑`
- **驗證點**：部分關鍵字也能找到動物

#### TC-I1.2-10: 複雜組合搜尋測試
- **測試條件**：建立 30 筆多樣動物，執行複雜搜尋 `?species=DOG&sex=MALE&min_age=1&max_age=3&q=可愛&region=台北&page=1&per_page=5`
- **驗證點**：
  - 所有條件正確套用
  - 分頁功能正常
  - 回傳結果符合期望
  - 效能在合理範圍內

#### TC-I1.2-11: 中文關鍵字搜尋測試
- **測試條件**：建立中文名稱動物，搜尋中文關鍵字
- **驗證點**：中文搜尋功能正常運作

#### TC-I1.2-12: 特殊字元關鍵字測試
- **測試條件**：搜尋包含 SQL 特殊字元的關鍵字 `?q=%test_char[bracket]`
- **驗證點**：
  - 不會造成 SQL injection
  - 特殊字元被正確處理
  - 搜尋結果正確

## 測試資料準備策略

### 動物測試資料工廠

```python
@pytest.fixture
def diverse_animals(db):
    """建立多樣化動物測試資料"""
    animals = [
        # 不同物種
        Animal(name="小黑", species=Species.DOG, sex=Sex.MALE, age=3, breed="黃金獵犬", 
               description="活潑可愛的狗狗", region="台北市", status=AnimalStatus.PUBLISHED),
        Animal(name="小白", species=Species.CAT, sex=Sex.FEMALE, age=2, breed="波斯貓", 
               description="溫和親人的貓咪", region="新北市", status=AnimalStatus.PUBLISHED),
        Animal(name="咖啡", species=Species.DOG, sex=Sex.MALE, age=5, breed="柴犬", 
               description="忠誠的夥伴", region="台中市", status=AnimalStatus.PUBLISHED),
        
        # 不同年齡範圍
        Animal(name="小小", species=Species.DOG, sex=Sex.FEMALE, age=1, breed="貴賓犬", 
               description="幼犬很可愛", region="台北市", status=AnimalStatus.PUBLISHED),
        Animal(name="老大", species=Species.DOG, sex=Sex.MALE, age=8, breed="拉布拉多", 
               description="成熟穩重", region="高雄市", status=AnimalStatus.PUBLISHED),
        
        # 關鍵字搜尋測試用
        Animal(name="Golden", species=Species.DOG, sex=Sex.MALE, age=3, breed="Golden Retriever", 
               description="friendly and loyal dog", region="台北市", status=AnimalStatus.PUBLISHED),
        Animal(name="皮皮", species=Species.CAT, sex=Sex.FEMALE, age=2, breed="英國短毛貓", 
               description="golden color fur", region="桃園市", status=AnimalStatus.PUBLISHED),
    ]
    
    for animal in animals:
        db.session.add(animal)
    db.session.commit()
    return animals
```

## Mock 策略詳細指南

### Unit Tests Mock 範例

```python
def test_multiple_conditions_and_logic(self, app_context, mock_db):
    """測試多條件AND邏輯組合"""
    # 使用成功模式設置Mock鏈
    mock_query = Mock()
    mock_filter_by = Mock()
    mock_filter = Mock()
    mock_order_by = Mock()
    mock_paginate = Mock()
    
    # 正確設置Mock鏈 - 關鍵：支援多次調用
    mock_query.filter_by.return_value = mock_filter_by
    mock_filter_by.filter_by.return_value = mock_filter_by  # 支持多次filter_by
    mock_filter_by.filter.return_value = mock_filter
    mock_filter.filter.return_value = mock_filter  # 支持多次filter
    mock_filter.order_by.return_value = mock_order_by
    mock_order_by.paginate.return_value = mock_paginate
    
    # 設置Mock pagination結果 - 使用configure_mock避免重新Mock化
    mock_paginate.configure_mock(**{
        'items': [],
        'total': 0,
        'page': 1,
        'per_page': 20,
        'pages': 1
    })

    with patch('app.services.animal_service.Animal') as mock_animal, \
         patch('app.services.animal_service.func') as mock_func, \
         patch('app.services.animal_service.or_') as mock_or:

        mock_animal.query = mock_query
        mock_db.engine.name = 'sqlite'  # 指定資料庫引擎
        
        # Mock SQLAlchemy func 操作 - 處理年齡計算
        mock_age_calc = Mock()
        mock_func.julianday.return_value = Mock()
        age_expression = Mock()
        age_expression.__ge__ = Mock(return_value=Mock())
        age_expression.__le__ = Mock(return_value=Mock())
        mock_age_calc.__truediv__ = Mock(return_value=age_expression)
        mock_func.julianday.return_value.__sub__ = Mock(return_value=mock_age_calc)
        
        # Mock Animal 的欄位屬性
        mock_animal.name.like = Mock(return_value=Mock())
        mock_animal.description.like = Mock(return_value=Mock())
        mock_animal.breed.like = Mock(return_value=Mock())

        filters = {
            'species': 'DOG',
            'sex': 'MALE', 
            'min_age': 1,
            'max_age': 3,
            'q': 'cute'
        }
        result = AnimalService.list_animals(filters)

        # 驗證多個篩選條件都被應用
        assert mock_filter_by.filter_by.call_count >= 3
        assert mock_func.julianday.called  # 年齡篩選
        assert mock_or.called  # 關鍵字搜尋
        assert 'animals' in result
```

### 重要Mock技巧

1. **自引用Mock鏈**：`mock_filter_by.filter_by.return_value = mock_filter_by`
2. **configure_mock使用**：避免屬性被重新Mock化
3. **SQLAlchemy func操作**：需要Mock複雜的數學運算鏈
4. **多層patch**：使用context manager同時Mock多個模組

## 測試執行與覆蓋率

### 執行指令

```bash
# 執行所有 Use Case 1.2 相關測試
pytest proj_new/backend/tests/ -k "useCase1_2" -v

# 只執行 Unit Tests (Service 層搜尋功能)
pytest proj_new/backend/tests/unit/test_animals_search_service_useCase1_2.py -v

# 只執行 Controller Tests (搜尋參數處理)  
pytest proj_new/backend/tests/unit/test_animals_search_controller_useCase1_2.py -v

# 只執行 Integration Tests (端到端搜尋)
pytest proj_new/backend/tests/integration/test_animals_search_integration_useCase1_2.py -v

# 執行並顯示覆蓋率
pytest proj_new/backend/tests/ -k "useCase1_2" --cov=app.services.animal_service --cov=app.blueprints.animals --cov-report=html -v

# 搜尋功能壓力測試
pytest proj_new/backend/tests/integration/test_animals_search_integration_useCase1_2.py::TC_I1_2_10 -v --benchmark-only
```

### 覆蓋率目標

- **Service 層搜尋邏輯**: > 95%
- **Controller 層參數處理**: > 90% 
- **整合測試場景覆蓋**: > 85%

## 測試優先順序

### P0（核心功能）
- 基本關鍵字搜尋 (TC-I1.2-01)
- 物種篩選 (TC-I1.2-02) 
- 多條件AND邏輯 (TC-I1.2-05)
- 複雜查詢字串解析 (TC-C1.2-01)
- 關鍵字全文搜尋 (TC-U1.2-04)

### P1（重要功能）  
- 年齡範圍篩選 (TC-I1.2-03)
- 性別篩選 (TC-I1.2-04)
- 地區篩選 (TC-I1.2-06)
- 結果數量限制 (TC-I1.2-08)
- 參數型別轉換 (TC-C1.2-02)

### P2（穩定性）
- 空搜尋結果處理 (TC-I1.2-07)
- 特殊字元處理 (TC-I1.2-12)
- 無效篩選值處理 (TC-U1.2-09)
- URL編碼處理 (TC-C1.2-03)

## 效能測試考量

對於搜尋篩選功能，建議加入效能測試：

```python
@pytest.mark.benchmark
def test_complex_search_performance(client, diverse_animals):
    """複雜搜尋查詢效能測試"""
    response = client.get('/api/animals?species=DOG&sex=MALE&min_age=1&max_age=5&q=friendly&region=台北')
    
    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 1.0  # 1秒內完成
```