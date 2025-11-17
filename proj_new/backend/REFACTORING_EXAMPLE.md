# 🔄 重構示例：從舊代碼到新架構

本文檔展示如何將現有的 Blueprint 路由重構為使用新的 Service 層。

---

## 示例 1: 創建動物 (POST /animals)

### ❌ 重構前（animals.py）

```python
@animals_bp.route('', methods=['POST'])
@jwt_required()
def create_animal():
    """建立動物資料 (需登入)"""
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)
    
    if not user:
        abort(404, message='使用者不存在')
    
    data = request.get_json()
    
    # ❌ 業務邏輯：決定是收容所動物還是個人送養動物
    shelter_id = None
    owner_id = None
    
    if user.role == UserRole.SHELTER_MEMBER and user.primary_shelter_id:
        shelter_id = user.primary_shelter_id
        owner_id = None
    elif user.role == UserRole.ADMIN and data.get('shelter_id'):
        shelter_id = data.get('shelter_id')
        owner_id = None
    else:
        shelter_id = None
        owner_id = current_user_id
    
    # ❌ 業務邏輯：創建動物
    animal = Animal(
        name=data.get('name'),
        species=Species(data['species']) if data.get('species') else None,
        breed=data.get('breed'),
        color=data.get('color'),
        sex=Sex(data['sex']) if data.get('sex') else None,
        dob=datetime.fromisoformat(data['dob']) if data.get('dob') else None,
        description=data.get('description'),
        status=AnimalStatus.DRAFT,
        shelter_id=shelter_id,
        owner_id=owner_id,
        medical_summary=data.get('medical_summary'),
        created_by=current_user_id
    )
    
    # ❌ 業務邏輯：防護檢查
    if animal.owner_id is not None and animal.shelter_id is not None:
        abort(400, message='owner_id 與 shelter_id 不能同時存在')
    
    db.session.add(animal)
    db.session.commit()
    
    return jsonify({
        'message': '動物資料建立成功',
        'animal': animal.to_dict(include_relations=True)
    }), 201
```

**問題：**
1. ❌ 業務邏輯混雜在 Blueprint 中（50+ 行代碼）
2. ❌ 權限判斷邏輯寫在路由中
3. ❌ 資料庫操作直接在路由中
4. ❌ 無法獨立測試業務邏輯
5. ❌ 代碼難以復用

---

### ✅ 重構後

#### 1. Service 層（animal_service.py）- 已完成 ✅

業務邏輯已經移至 `animal_service.create_animal()`

#### 2. Blueprint 層（animals.py）- 需要更新

```python
from app.services.animal_service import animal_service
from app.exceptions import ValidationError

@animals_bp.route('', methods=['POST'])
@jwt_required()
def create_animal():
    """建立動物資料 (需登入) - 薄控制器"""
    try:
        # 1. 獲取當前用戶
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            abort(404, message='使用者不存在')
        
        # 2. 解析請求資料
        data = request.get_json()
        
        # 3. ✅ 調用 Service 層處理業務邏輯
        animal = animal_service.create_animal(current_user, data)
        
        # 4. 返回響應
        return jsonify({
            'message': '動物資料建立成功',
            'animal': animal.to_dict(include_relations=True)
        }), 201
        
    except ValidationError as e:
        abort(400, message=str(e))
    except Exception as e:
        abort(500, message=f'伺服器錯誤: {str(e)}')
```

**改善：**
1. ✅ Blueprint 只有 30 行，清晰簡潔
2. ✅ 業務邏輯在 Service 層，可獨立測試
3. ✅ 統一的異常處理
4. ✅ 代碼可復用

---

## 示例 2: 更新動物 (PATCH /animals/<id>)

### ❌ 重構前（animals.py）

```python
@animals_bp.route('/<int:animal_id>', methods=['PATCH'])
@jwt_required()
def update_animal(animal_id):
    """更新動物資料 (需為擁有者或管理員)"""
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)
    
    animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
    
    if not animal:
        abort(404, message='動物不存在')
    
    # ❌ 複雜的權限檢查邏輯（重複出現在多個路由）
    has_permission = False
    
    if animal.owner_id and animal.owner_id == current_user_id:
        has_permission = True
    elif animal.shelter_id and user.role == UserRole.SHELTER_MEMBER and user.primary_shelter_id == animal.shelter_id:
        has_permission = True
    elif animal.shelter_id and user.role == UserRole.ADMIN:
        has_permission = True
    
    if not has_permission:
        abort(403, message='只有動物擁有者或收容所成員可以修改此動物資料')
    
    # ❌ 更新邏輯
    data = request.get_json()
    
    if 'name' in data:
        animal.name = data['name']
    if 'species' in data:
        animal.species = Species(data['species'])
    if 'breed' in data:
        animal.breed = data['breed']
    # ... 更多欄位更新
    
    # ❌ 防護檢查
    if animal.owner_id is not None and animal.shelter_id is not None:
        abort(400, message='owner_id 與 shelter_id 不能同時存在')

    db.session.commit()
    
    return jsonify({
        'message': '動物資料更新成功',
        'animal': animal.to_dict(include_relations=True)
    }), 200
```

**問題：**
1. ❌ 權限檢查邏輯重複（在多個路由中都有類似代碼）
2. ❌ 更新邏輯冗長且難以維護
3. ❌ 違反 DRY 原則

---

### ✅ 重構後

```python
from app.services.animal_service import animal_service
from app.exceptions import PermissionDeniedError, NotFoundError, ValidationError

@animals_bp.route('/<int:animal_id>', methods=['PATCH'])
@jwt_required()
def update_animal(animal_id):
    """更新動物資料 - 薄控制器"""
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

**改善：**
1. ✅ 代碼從 60+ 行減少到 25 行
2. ✅ 權限檢查邏輯統一在 `permission_service` 中
3. ✅ 更新邏輯統一在 `animal_service` 中
4. ✅ 清晰的異常處理

---

## 示例 3: 提交動物審核 (POST /animals/<id>/submit)

### ❌ 重構前

```python
@animals_bp.route('/<int:animal_id>/submit', methods=['POST'])
@jwt_required()
def submit_animal(animal_id):
    """提交動物供審核 (狀態: DRAFT -> SUBMITTED)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        if not animal:
            abort(404, message='動物不存在')
        
        # ❌ 權限檢查邏輯（又重複了）
        user = db.session.get(User, current_user_id)
        
        has_permission = False
        if animal.owner_id and animal.owner_id == current_user_id:
            has_permission = True
        elif animal.shelter_id and user.role == UserRole.SHELTER_MEMBER and user.primary_shelter_id == animal.shelter_id:
            has_permission = True
        
        if not has_permission:
            abort(403, message='只能提交自己的動物或所屬收容所的動物')
        
        # ❌ 狀態檢查
        if animal.status != AnimalStatus.DRAFT:
            abort(400, message=f'只能提交草稿狀態的動物,目前狀態: {animal.status.value}')
        
        # ❌ 更新狀態
        animal.status = AnimalStatus.SUBMITTED
        db.session.commit()
        
        return jsonify({
            'message': '動物已提交審核,管理員將儘快處理',
            'animal': animal.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
```

---

### ✅ 重構後

```python
from app.services.animal_service import animal_service
from app.exceptions import PermissionDeniedError, NotFoundError, ValidationError

@animals_bp.route('/<int:animal_id>/submit', methods=['POST'])
@jwt_required()
def submit_animal(animal_id):
    """提交動物供審核 - 薄控制器"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # ✅ 調用 Service
        animal = animal_service.submit_for_review(animal_id, current_user)
        
        return jsonify({
            'message': '動物已提交審核,管理員將儘快處理',
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

**改善：**
1. ✅ 代碼從 40+ 行減少到 20 行
2. ✅ 所有業務邏輯在 Service 層
3. ✅ 統一的異常處理模式

---

## 示例 4: 審核申請 (POST /applications/<id>/review)

### ❌ 重構前（applications.py）

```python
@applications_bp.route('/<int:application_id>/review', methods=['POST'])
@jwt_required()
def review_application(application_id):
    """審核申請 (核准/拒絕)"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            abort(404, message='用戶不存在')
        
        application = Application.query.filter_by(
            application_id=application_id,
            deleted_at=None
        ).first()
        
        if not application:
            abort(404, message='申請不存在')
        
        # ❌ 複雜的權限檢查
        from app.models.animal import Animal
        animal = Animal.query.get(application.animal_id)
        if not animal:
            abort(404, message='動物不存在')
        
        has_permission = False
        if animal.owner_id and animal.owner_id == current_user_id:
            has_permission = True
        elif animal.shelter_id and current_user.role == UserRole.SHELTER_MEMBER and current_user.primary_shelter_id == animal.shelter_id:
            has_permission = True
        
        if not has_permission:
            if current_user.role == UserRole.ADMIN:
                abort(403, message='領養申請應由送養人或收容所成員審核,管理員無權審核')
            else:
                abort(403, message='只有送養人或收容所成員可以審核此申請')
        
        data = request.get_json()
        action = data.get('action')
        
        if action not in ['approve', 'reject']:
            abort(400, message='action 必須為 approve 或 reject')
        
        # ❌ 狀態檢查
        if application.status not in [ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW]:
            abort(400, message='此申請無法審核')
        
        # ❌ 樂觀鎖檢查
        if 'version' in data:
            if application.version != data['version']:
                abort(409, message='申請已被其他人修改，請重新載入')
        
        # ❌ 業務邏輯：更新狀態
        old_status = application.status
        
        if action == 'approve':
            application.status = ApplicationStatus.APPROVED
            if animal:
                from app.models.animal import AnimalStatus
                animal.status = AnimalStatus.ADOPTED
                animal.updated_at = datetime.utcnow()
        else:
            application.status = ApplicationStatus.REJECTED
        
        application.assignee_id = current_user_id
        application.reviewed_at = datetime.utcnow()
        application.review_notes = data.get('review_notes')
        application.version += 1
        
        db.session.commit()
        
        # ❌ 審計日誌（在 Blueprint 中）
        try:
            audit_service.log_application_review(
                application_id,
                current_user_id,
                old_status.value,
                application.status.value
            )
        except Exception as audit_error:
            print(f'審計日誌記錄失敗: {audit_error}')
        
        # ❌ 發送通知（在 Blueprint 中）
        try:
            notification_service.notify_application_reviewed(...)
            # 發送 Email
            from app.tasks.email_tasks import send_application_notification_email_task
            send_application_notification_email_task.delay(...)
        except Exception as notify_error:
            print(f'通知發送失敗: {notify_error}')
        
        return jsonify({
            'message': f'申請已{("核准" if action == "approve" else "拒絕")}',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        print(f"審核申請時發生錯誤: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
```

**問題：**
1. ❌ 超過 100 行的路由函數
2. ❌ 複雜的業務邏輯混雜
3. ❌ 審計日誌和通知發送在 Blueprint 中
4. ❌ 難以測試和維護

---

### ✅ 重構後

```python
from app.services.application_service import application_service
from app.exceptions import PermissionDeniedError, NotFoundError, ValidationError, ConflictError

@applications_bp.route('/<int:application_id>/review', methods=['POST'])
@jwt_required()
def review_application(application_id):
    """審核申請 - 薄控制器"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            abort(404, message='用戶不存在')
        
        data = request.get_json()
        action = data.get('action')
        review_notes = data.get('review_notes')
        expected_version = data.get('version')
        
        # ✅ 所有業務邏輯在 Service 中
        application = application_service.review_application(
            application_id=application_id,
            reviewer=current_user,
            action=action,
            review_notes=review_notes,
            expected_version=expected_version
        )
        
        return jsonify({
            'message': f'申請已{("核准" if action == "approve" else "拒絕")}',
            'application': application.to_dict()
        }), 200
        
    except PermissionDeniedError as e:
        abort(403, message=str(e))
    except ValidationError as e:
        abort(400, message=str(e))
    except NotFoundError as e:
        abort(404, message=str(e))
    except ConflictError as e:
        abort(409, message=str(e))
    except Exception as e:
        abort(500, message=f'伺服器錯誤: {str(e)}')
```

**改善：**
1. ✅ 代碼從 100+ 行減少到 35 行
2. ✅ 所有業務邏輯（權限、狀態、審計、通知）在 Service 中
3. ✅ 清晰的異常處理流程
4. ✅ Blueprint 只負責路由層職責

---

## 📊 重構前後對比總結

| 指標 | 重構前 | 重構後 | 改善 |
|------|--------|--------|------|
| 代碼行數（單個路由） | 60-100+ 行 | 20-35 行 | ✅ 減少 60-70% |
| 業務邏輯位置 | 混雜在 Blueprint | 集中在 Service | ✅ 關注點分離 |
| 權限檢查 | 重複在多處 | 統一在 permission_service | ✅ DRY 原則 |
| 可測試性 | 難以測試 | 易於單元測試 | ✅ 測試覆蓋率提升 |
| 可維護性 | 低 | 高 | ✅ 易於修改和擴展 |
| 代碼復用 | 困難 | 容易 | ✅ Service 可在多處調用 |

---

## 🎯 重構檢查清單

在重構每個路由時，確認以下事項：

- [ ] 業務邏輯已移至 Service 層
- [ ] 權限檢查使用 `permission_service`
- [ ] 拋出語義化的異常（而非 abort）
- [ ] Blueprint 只負責請求/響應處理
- [ ] 添加適當的異常處理
- [ ] 保持原有功能不變
- [ ] 測試通過

---

## 💡 最佳實踐提醒

### ✅ 做什麼
1. 在 Service 層拋出業務異常
2. 在 Blueprint 層捕獲並轉換為 HTTP 響應
3. 保持 Service 方法的純粹性（不依賴 Flask）
4. 使用依賴注入（通過參數傳遞依賴）

### ❌ 不做什麼
1. 不要在 Service 中直接訪問 `request` 對象
2. 不要在 Service 中使用 `abort()` 或返回 Flask 響應
3. 不要在 Blueprint 中包含業務邏輯
4. 不要重複權限檢查代碼

---

**重構示例完成日期**: 2025-11-17
