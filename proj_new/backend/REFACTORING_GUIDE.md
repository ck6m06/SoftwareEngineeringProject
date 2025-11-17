# 🔧 Backend 架構重構指南

## 📋 概述

本次重構將後端架構從「業務邏輯混雜在 Blueprint 中」改為「標準的三層架構」，實現了清晰的關注點分離。

## ✅ 已完成的工作

### 1. 創建統一異常處理 (`app/exceptions.py`)

```python
- BusinessException           # 業務異常基類
- PermissionDeniedError       # 權限不足 (403)
- NotFoundError              # 資源不存在 (404)
- ValidationError            # 資料驗證失敗 (400)
- ConflictError              # 資源衝突 (409)
- UnauthorizedError          # 未授權 (401)
```

**優點：**
- 統一的異常處理機制
- 語義化的異常類型
- 自動包含 HTTP 狀態碼

---

### 2. 創建權限服務 (`app/services/permission_service.py`)

集中管理所有權限檢查邏輯：

```python
- can_manage_animal()          # 是否可以管理動物
- can_view_animal()            # 是否可以查看動物
- can_review_application()     # 是否可以審核申請
- can_view_application()       # 是否可以查看申請
- can_submit_animal_for_review() # 是否可以提交動物供審核
- can_publish_animal()         # 是否可以發布動物
- can_reject_animal()          # 是否可以拒絕動物上架
```

**優點：**
- 避免權限邏輯重複
- 單一真相來源 (Single Source of Truth)
- 易於維護和測試

---

### 3. 創建動物服務 (`app/services/animal_service.py`)

集中管理所有動物相關的業務邏輯：

```python
- create_animal()       # 創建動物
- update_animal()       # 更新動物
- delete_animal()       # 刪除動物（軟刪除）
- submit_for_review()   # 提交審核
- publish_animal()      # 發布動物
- retire_animal()       # 下架動物
- reject_animal()       # 拒絕動物上架
- add_image()          # 新增圖片
- delete_image()       # 刪除圖片
- reorder_images()     # 重新排序圖片
```

**優點：**
- 業務邏輯集中管理
- 可獨立測試
- 易於復用

---

### 4. 創建申請服務 (`app/services/application_service.py`)

集中管理所有申請相關的業務邏輯：

```python
- create_application()   # 創建申請
- review_application()   # 審核申請（批准/拒絕）
- withdraw_application() # 撤回申請
- assign_application()   # 指派申請給處理人員
```

**業務邏輯包含：**
- 冪等性處理
- 樂觀鎖檢查
- 權限驗證
- 狀態管理
- 審計日誌記錄
- 通知發送

---

## 📁 新的架構結構

```
app/
├── blueprints/              # API 路由層（薄控制器）
│   ├── animals.py          # ⚠️ 需要重構
│   ├── applications.py     # ⚠️ 需要重構
│   └── ...
├── services/               # 業務邏輯層 ✅
│   ├── animal_service.py     # ✅ 新增
│   ├── application_service.py # ✅ 新增
│   ├── permission_service.py  # ✅ 新增
│   ├── audit_service.py      # ✅ 已存在
│   ├── email_service.py      # ✅ 已存在
│   └── notification_service.py # ✅ 已存在
├── models/                 # 資料模型層
│   └── ...
├── exceptions.py           # ✅ 新增：統一異常處理
└── ...
```

---

## 🔄 下一步：重構 Blueprints

### 重構原則：薄控制器模式

Blueprint 應該只負責：
1. 請求參數解析
2. 調用 Service
3. 返回響應
4. 異常處理

### 重構前 vs 重構後對比

#### ❌ 重構前（不良範例）

```python
@animals_bp.route('/<int:animal_id>', methods=['PATCH'])
@jwt_required()
def update_animal(animal_id):
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)
    animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
    
    if not animal:
        abort(404, message='動物不存在')
    
    # ❌ 複雜的權限檢查邏輯
    has_permission = False
    if animal.owner_id and animal.owner_id == current_user_id:
        has_permission = True
    elif animal.shelter_id and user.role == UserRole.SHELTER_MEMBER:
        has_permission = True
    
    if not has_permission:
        abort(403, message='無權限')
    
    # ❌ 更新邏輯也在這裡
    data = request.get_json()
    if 'name' in data:
        animal.name = data['name']
    # ... 更多更新邏輯
    
    db.session.commit()
    return jsonify(animal.to_dict()), 200
```

#### ✅ 重構後（良好範例）

```python
@animals_bp.route('/<int:animal_id>', methods=['PATCH'])
@jwt_required()
def update_animal(animal_id):
    """更新動物資料（薄控制器）"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        data = request.get_json()
        
        # ✅ 業務邏輯委派給 Service
        animal = animal_service.update_animal(
            animal_id=animal_id,
            user=current_user,
            data=data
        )
        
        return jsonify({
            'message': '動物資料更新成功',
            'animal': animal.to_dict(include_relations=True)
        }), 200
        
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except ValidationError as e:
        abort(400, message=str(e))
    except NotFoundError as e:
        abort(404, message=str(e))
    except Exception as e:
        abort(500, message=f'伺服器錯誤: {str(e)}')
```

---

## 📝 重構步驟（針對每個 Blueprint 路由）

### Step 1: 識別業務邏輯

找出以下代碼：
- 權限檢查
- 資料驗證
- 狀態管理
- 資料庫操作
- 通知/郵件發送

### Step 2: 將業務邏輯移至 Service

將步驟 1 識別的邏輯移至對應的 Service 方法中。

### Step 3: 簡化 Blueprint

將 Blueprint 改為薄控制器：
- 解析請求參數
- 調用 Service
- 處理異常
- 返回響應

### Step 4: 測試

確保重構後功能正常。

---

## 🎯 重構優先級

### 高優先級（立即重構）
- ✅ `animals.py` - update_animal()
- ✅ `animals.py` - create_animal()
- ✅ `animals.py` - submit_animal()
- ✅ `animals.py` - publish_animal()
- ✅ `animals.py` - reject_animal()
- ✅ `applications.py` - create_application()
- ✅ `applications.py` - review_application()

### 中優先級
- `animals.py` - 其他圖片管理方法
- `applications.py` - withdraw_application()
- `applications.py` - assign_application()

### 低優先級
- 其他 Blueprint 的重構

---

## 🧪 測試建議

### 單元測試（針對 Service 層）

```python
# tests/services/test_animal_service.py
def test_create_animal_as_general_user():
    user = create_general_user()
    data = {'name': 'Test Animal', 'species': 'DOG'}
    
    animal = animal_service.create_animal(user, data)
    
    assert animal.owner_id == user.user_id
    assert animal.shelter_id is None
    assert animal.status == AnimalStatus.DRAFT

def test_cannot_manage_other_user_animal():
    owner = create_general_user()
    other_user = create_general_user()
    animal = create_animal(owner)
    
    with pytest.raises(PermissionDeniedError):
        animal_service.update_animal(animal.animal_id, other_user, {})
```

### 整合測試（針對 Blueprint）

```python
# tests/blueprints/test_animals.py
def test_update_animal_endpoint(client, auth_headers):
    response = client.patch(
        f'/animals/{animal_id}',
        json={'name': 'Updated Name'},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['animal']['name'] == 'Updated Name'
```

---

## 📚 參考資料

### 設計模式
- **Service Layer Pattern**: 將業務邏輯集中在 Service 層
- **Repository Pattern**: 資料訪問抽象（目前使用 SQLAlchemy ORM）
- **Dependency Injection**: 透過參數傳遞依賴（而非全局導入）

### SOLID 原則
- **S**ingle Responsibility: 每個類別只有一個職責
- **O**pen/Closed: 對擴展開放，對修改關閉
- **L**iskov Substitution: 子類別可以替換父類別
- **I**nterface Segregation: 使用多個專用介面
- **D**ependency Inversion: 依賴抽象而非具體實現

---

## 🎓 最佳實踐

### 1. Service 方法應該：
- ✅ 接受必要的參數（User, data, etc.）
- ✅ 執行業務邏輯驗證
- ✅ 拋出語義化的異常
- ✅ 返回領域模型（Model）
- ❌ 不直接訪問 request 對象
- ❌ 不直接返回 HTTP 響應

### 2. Blueprint 應該：
- ✅ 解析 request 參數
- ✅ 調用 Service 方法
- ✅ 捕獲並轉換異常
- ✅ 構建 HTTP 響應
- ❌ 不包含業務邏輯
- ❌ 不直接操作資料庫

### 3. 異常處理：
- ✅ 在 Service 層拋出業務異常
- ✅ 在 Blueprint 層捕獲並轉換為 HTTP 狀態碼
- ✅ 提供清晰的錯誤訊息

---

## 🚀 使用方式

### 在 Blueprint 中使用 Service

```python
from app.services.animal_service import animal_service
from app.services.application_service import application_service
from app.services.permission_service import permission_service
from app.exceptions import (
    PermissionDeniedError, NotFoundError, ValidationError, ConflictError
)

@animals_bp.route('', methods=['POST'])
@jwt_required()
def create_animal():
    try:
        current_user = User.query.get(int(get_jwt_identity()))
        data = request.get_json()
        
        animal = animal_service.create_animal(current_user, data)
        
        return jsonify({
            'message': '動物資料建立成功',
            'animal': animal.to_dict(include_relations=True)
        }), 201
        
    except ValidationError as e:
        abort(400, message=str(e))
    except Exception as e:
        abort(500, message=f'伺服器錯誤: {str(e)}')
```

---

## 📊 重構進度追蹤

### 已完成 ✅
- [x] 創建 exceptions.py
- [x] 創建 permission_service.py
- [x] 創建 animal_service.py
- [x] 創建 application_service.py

### 待完成 ⏳
- [ ] 重構 animals.py 所有路由
- [ ] 重構 applications.py 所有路由
- [ ] 添加 Service 層單元測試
- [ ] 添加 Blueprint 整合測試
- [ ] 更新 API 文檔

---

## 💡 常見問題

### Q: 為什麼要重構？
A: 原代碼將業務邏輯混雜在 Blueprint 中，違反單一職責原則，導致代碼難以測試和維護。

### Q: 重構會影響現有功能嗎？
A: 不會。重構只改變代碼結構，不改變功能行為。建議在重構後進行完整測試。

### Q: Service 層是否應該返回 JSON？
A: 不應該。Service 層應該返回領域模型（Model 對象），由 Blueprint 層負責序列化為 JSON。

### Q: 如何處理事務？
A: Service 層方法內部使用 `db.session.commit()`。如果需要多個 Service 調用共享一個事務，可以在外層使用 `db.session.begin()`。

---

## 📞 聯繫與支援

如有問題或建議，請聯繫開發團隊。

**重構完成日期**: 2025-11-17  
**版本**: 1.0.0
