"""
Animal Service - 動物業務邏輯服務
集中管理所有動物相關的業務邏輯
"""
from datetime import datetime
from typing import Optional, Dict, Any
from app import db
from app.models.animal import Animal, AnimalImage, AnimalStatus, Species, Sex
from app.models.user import User, UserRole
from app.exceptions import (
    PermissionDeniedError, NotFoundError, ValidationError
)
from app.services.permission_service import permission_service


class AnimalService:
    """動物業務邏輯服務類"""
    
    @staticmethod
    def create_animal(user: User, data: Dict[str, Any]) -> Animal:
        """
        創建動物記錄
        
        業務邏輯：
        1. 判斷是收容所動物還是個人送養動物
        2. 收容所成員創建的動物歸屬於其收容所
        3. 一般用戶創建的動物為個人送養
        4. 管理員可以指定收容所
        
        Args:
            user: 創建者
            data: 動物資料
            
        Returns:
            Animal: 創建的動物物件
            
        Raises:
            ValidationError: 資料驗證失敗
        """
        # 決定動物歸屬
        shelter_id = None
        owner_id = None
        
        if user.role == UserRole.SHELTER_MEMBER and user.primary_shelter_id:
            # 收容所會員且有關聯的收容所 -> 設為收容所動物
            shelter_id = user.primary_shelter_id
            owner_id = None
        elif user.role == UserRole.ADMIN and data.get('shelter_id'):
            # 管理員可以指定收容所
            shelter_id = data.get('shelter_id')
            owner_id = None
        else:
            # 一般會員或其他情況 -> 個人送養
            shelter_id = None
            owner_id = user.user_id
        
        # 創建動物
        animal = Animal(
            name=data.get('name'),
            species=Species(data['species']) if data.get('species') else None,
            breed=data.get('breed'),
            color=data.get('color'),
            sex=Sex(data['sex']) if data.get('sex') else None,
            dob=datetime.fromisoformat(data['dob']) if data.get('dob') else None,
            description=data.get('description'),
            status=AnimalStatus.DRAFT,  # 預設為草稿
            shelter_id=shelter_id,
            owner_id=owner_id,
            medical_summary=data.get('medical_summary'),
            created_by=user.user_id
        )
        
        # 防護：確保 owner_id 與 shelter_id 不會同時存在
        if animal.owner_id is not None and animal.shelter_id is not None:
            raise ValidationError('owner_id 與 shelter_id 不能同時存在')
        
        db.session.add(animal)
        db.session.commit()
        
        return animal
    
    @staticmethod
    def update_animal(animal_id: int, user: User, data: Dict[str, Any]) -> Animal:
        """
        更新動物資料
        
        業務邏輯：
        1. 檢查動物是否存在
        2. 檢查用戶權限
        3. 更新允許的欄位
        
        Args:
            animal_id: 動物 ID
            user: 當前用戶
            data: 更新資料
            
        Returns:
            Animal: 更新後的動物物件
            
        Raises:
            NotFoundError: 動物不存在
            PermissionDeniedError: 無權限
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        # 權限檢查
        if not permission_service.can_manage_animal(user, animal):
            raise PermissionDeniedError('只有動物擁有者或收容所成員可以修改此動物資料')
        
        # 更新欄位
        if 'name' in data:
            animal.name = data['name']
        if 'species' in data:
            animal.species = Species(data['species'])
        if 'breed' in data:
            animal.breed = data['breed']
        if 'color' in data:
            animal.color = data['color']
        if 'sex' in data:
            animal.sex = Sex(data['sex'])
        if 'dob' in data:
            animal.dob = datetime.fromisoformat(data['dob']) if data['dob'] else None
        if 'description' in data:
            animal.description = data['description']
        if 'status' in data:
            animal.status = AnimalStatus(data['status'])
        if 'medical_summary' in data:
            animal.medical_summary = data['medical_summary']
        
        # 防護：更新前再檢查互斥條件
        if animal.owner_id is not None and animal.shelter_id is not None:
            raise ValidationError('owner_id 與 shelter_id 不能同時存在')
        
        db.session.commit()
        
        return animal
    
    @staticmethod
    def delete_animal(animal_id: int, user: User) -> None:
        """
        刪除動物（軟刪除）
        
        Args:
            animal_id: 動物 ID
            user: 當前用戶
            
        Raises:
            NotFoundError: 動物不存在
            PermissionDeniedError: 無權限
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        # 權限檢查（管理員也可以刪除）
        if not permission_service.can_manage_animal(user, animal) and user.role != UserRole.ADMIN:
            raise PermissionDeniedError('沒有權限刪除此動物資料')
        
        # 軟刪除
        animal.deleted_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def submit_for_review(animal_id: int, user: User) -> Animal:
        """
        提交動物供審核（DRAFT -> SUBMITTED）
        
        業務邏輯：
        1. 只能提交草稿狀態的動物
        2. 只有擁有者可以提交
        
        Args:
            animal_id: 動物 ID
            user: 當前用戶
            
        Returns:
            Animal: 更新後的動物物件
            
        Raises:
            NotFoundError: 動物不存在
            PermissionDeniedError: 無權限
            ValidationError: 狀態不符
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        # 權限檢查
        if not permission_service.can_submit_animal_for_review(user, animal):
            raise PermissionDeniedError('只能提交自己的動物或所屬收容所的動物')
        
        # 狀態檢查
        if animal.status != AnimalStatus.DRAFT:
            raise ValidationError(f'只能提交草稿狀態的動物,目前狀態: {animal.status.value}')
        
        # 更新狀態
        animal.status = AnimalStatus.SUBMITTED
        db.session.commit()
        
        return animal
    
    @staticmethod
    def publish_animal(animal_id: int, admin: User) -> Animal:
        """
        發布動物（DRAFT/SUBMITTED -> PUBLISHED）
        
        業務邏輯：
        1. 只有管理員可以發布
        2. 已發布的動物不能重複發布
        
        Args:
            animal_id: 動物 ID
            admin: 管理員
            
        Returns:
            Animal: 更新後的動物物件
            
        Raises:
            NotFoundError: 動物不存在
            PermissionDeniedError: 需要管理員權限
            ValidationError: 動物已經是發布狀態
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        # 權限檢查
        if not permission_service.can_publish_animal(admin, animal):
            raise PermissionDeniedError('需要管理員權限')
        
        if animal.status == AnimalStatus.PUBLISHED:
            raise ValidationError('動物已經是發布狀態')
        
        animal.status = AnimalStatus.PUBLISHED
        db.session.commit()
        
        return animal
    
    @staticmethod
    def retire_animal(animal_id: int, user: User) -> Animal:
        """
        下架動物（PUBLISHED -> RETIRED）
        
        Args:
            animal_id: 動物 ID
            user: 當前用戶
            
        Returns:
            Animal: 更新後的動物物件
            
        Raises:
            NotFoundError: 動物不存在
            PermissionDeniedError: 無權限
            ValidationError: 動物已經是下架狀態
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        # 權限檢查（擁有者或管理員可以下架）
        if not permission_service.can_manage_animal(user, animal) and user.role != UserRole.ADMIN:
            raise PermissionDeniedError('無權限下架此動物')
        
        if animal.status == AnimalStatus.RETIRED:
            raise ValidationError('動物已經是下架狀態')
        
        animal.status = AnimalStatus.RETIRED
        db.session.commit()
        
        return animal
    
    @staticmethod
    def reject_animal(animal_id: int, admin: User, rejection_reason: str) -> Animal:
        """
        拒絕批准動物上架（SUBMITTED -> DRAFT）
        
        業務邏輯：
        1. 只有管理員可以拒絕
        2. 只能拒絕待審核狀態的動物
        3. 記錄拒絕原因、時間、操作者
        
        Args:
            animal_id: 動物 ID
            admin: 管理員
            rejection_reason: 拒絕原因
            
        Returns:
            Animal: 更新後的動物物件
            
        Raises:
            NotFoundError: 動物不存在
            PermissionDeniedError: 只有管理員可以拒絕
            ValidationError: 只能拒絕待審核狀態的動物或缺少拒絕原因
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        # 權限檢查
        if not permission_service.can_reject_animal(admin, animal):
            raise PermissionDeniedError('只有管理員可以拒絕批准')
        
        # 狀態檢查
        if animal.status != AnimalStatus.SUBMITTED:
            raise ValidationError(f'只能拒絕待審核狀態的動物,目前狀態: {animal.status.value}')
        
        if not rejection_reason or not rejection_reason.strip():
            raise ValidationError('請提供拒絕原因')
        
        # 更新狀態和拒絕資訊
        animal.status = AnimalStatus.DRAFT
        animal.rejection_reason = rejection_reason
        animal.rejected_at = datetime.utcnow()
        animal.rejected_by = admin.user_id
        
        db.session.commit()
        
        # TODO: 發送通知給動物擁有者
        
        return animal
    
    @staticmethod
    def add_image(animal_id: int, user: User, storage_key: str, url: str, 
                  mime_type: Optional[str] = None) -> AnimalImage:
        """
        新增動物圖片
        
        Args:
            animal_id: 動物 ID
            user: 當前用戶
            storage_key: 儲存鍵值
            url: 圖片 URL
            mime_type: MIME 類型
            
        Returns:
            AnimalImage: 創建的圖片物件
            
        Raises:
            NotFoundError: 動物不存在
            PermissionDeniedError: 無權限
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        if not permission_service.can_manage_animal(user, animal):
            raise PermissionDeniedError('無權限管理此動物的圖片')
        
        # 計算新圖片的順序
        max_order = db.session.query(db.func.max(AnimalImage.order)).filter_by(
            animal_id=animal_id
        ).scalar() or 0
        
        # 創建圖片記錄
        image = AnimalImage(
            animal_id=animal_id,
            storage_key=storage_key,
            url=url,
            mime_type=mime_type or 'image/jpeg',
            order=max_order + 1
        )
        
        db.session.add(image)
        db.session.commit()
        
        return image
    
    @staticmethod
    def delete_image(animal_id: int, image_id: int, user: User) -> None:
        """
        刪除動物圖片
        
        Args:
            animal_id: 動物 ID
            image_id: 圖片 ID
            user: 當前用戶
            
        Raises:
            NotFoundError: 動物或圖片不存在
            PermissionDeniedError: 無權限
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        if not permission_service.can_manage_animal(user, animal):
            raise PermissionDeniedError('無權限管理此動物的圖片')
        
        image = AnimalImage.query.filter_by(
            animal_image_id=image_id,
            animal_id=animal_id
        ).first()
        
        if not image:
            raise NotFoundError('圖片不存在')
        
        db.session.delete(image)
        db.session.commit()
    
    @staticmethod
    def reorder_images(animal_id: int, user: User, image_orders: list) -> None:
        """
        重新排序動物圖片
        
        Args:
            animal_id: 動物 ID
            user: 當前用戶
            image_orders: 圖片順序列表 [{"image_id": 1, "order": 1}, ...]
            
        Raises:
            NotFoundError: 動物不存在
            PermissionDeniedError: 無權限
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        if not permission_service.can_manage_animal(user, animal):
            raise PermissionDeniedError('無權限管理此動物的圖片')
        
        # 更新圖片順序
        for item in image_orders:
            image = AnimalImage.query.filter_by(
                animal_image_id=item['image_id'],
                animal_id=animal_id
            ).first()
            if image:
                image.order = item['order']
        
        db.session.commit()
    
    @staticmethod
    def list_animals(filters: dict, current_user_id: int = None) -> dict:
        """
        獲取動物列表 (支援複雜篩選)
        
        Args:
            filters: 篩選條件字典
                - species: 物種
                - sex: 性別
                - status: 狀態
                - shelter_id: 收容所 ID
                - owner_id: 擁有者 ID
                - created_by: 創建者 ID
                - source_type: 來源類型 (shelter/personal)
                - region: 地區
                - min_age: 最小年齡 (月數)
                - max_age: 最大年齡 (月數)
                - q: 關鍵字搜尋
                - page: 頁碼
                - per_page: 每頁筆數
            current_user_id: 當前用戶 ID (可選)
            
        Returns:
            dict: 包含動物列表和分頁資訊
        """
        from app.models.user import User
        from app.models.shelter import Shelter
        from sqlalchemy import func
        
        # 取得篩選參數
        species = filters.get('species')
        sex = filters.get('sex')
        status = filters.get('status')
        shelter_id = filters.get('shelter_id')
        owner_id = filters.get('owner_id')
        created_by = filters.get('created_by')
        source_type = filters.get('source_type')
        region = filters.get('region')
        min_age = filters.get('min_age')
        max_age = filters.get('max_age')
        q = filters.get('q', '').strip()
        page = filters.get('page', 1)
        per_page = min(filters.get('per_page', 20), 100)
        
        # 建立基礎查詢
        query = Animal.query.filter_by(deleted_at=None)
        
        # 處理 owner_id 篩選的權限邏輯
        if owner_id:
            if current_user_id == owner_id:
                # 查詢自己的動物
                current_user = db.session.get(User, current_user_id)
                
                if current_user and current_user.role == UserRole.SHELTER_MEMBER and current_user.primary_shelter_id:
                    # 收容所成員：查詢個人動物 + 收容所動物
                    query = query.filter(
                        db.or_(
                            Animal.owner_id == owner_id,
                            Animal.shelter_id == current_user.primary_shelter_id
                        )
                    )
                else:
                    # 一般用戶：只查詢個人動物 (包含草稿)
                    query = query.filter_by(owner_id=owner_id)
            elif current_user_id is None:
                # 沒有認證：只能查看已發布的動物
                query = query.filter_by(owner_id=owner_id, status=AnimalStatus.PUBLISHED)
            else:
                # 查詢其他用戶的動物，只能看已發布的
                query = query.filter_by(owner_id=owner_id, status=AnimalStatus.PUBLISHED)
        elif created_by:
            query = query.filter_by(created_by=created_by)
        else:
            # 預設只顯示已發布的動物
            if not status:
                status = AnimalStatus.PUBLISHED.value
        
        # 狀態篩選
        if status:
            try:
                status_enum = AnimalStatus(status) if isinstance(status, str) else status
                query = query.filter_by(status=status_enum)
            except ValueError:
                raise ValidationError('無效的狀態值')
        
        # 物種篩選
        if species:
            try:
                species_enum = Species(species) if isinstance(species, str) else species
                query = query.filter_by(species=species_enum)
            except ValueError:
                raise ValidationError('無效的物種值')
        
        # 性別篩選
        if sex:
            try:
                sex_enum = Sex(sex) if isinstance(sex, str) else sex
                query = query.filter_by(sex=sex_enum)
            except ValueError:
                raise ValidationError('無效的性別值')
        
        # 收容所篩選
        if shelter_id:
            query = query.filter_by(shelter_id=shelter_id)
        
        # 來源類型篩選
        if source_type:
            if source_type == 'shelter':
                query = query.filter(Animal.shelter_id.isnot(None))
            elif source_type == 'personal':
                query = query.filter(Animal.owner_id.isnot(None))
        
        # 地區篩選
        if region:
            shelter_region_condition = db.exists().where(
                db.and_(
                    Animal.shelter_id == Shelter.shelter_id,
                    Shelter.region.like(f'%{region}%')
                )
            )
            
            owner_region_condition = db.exists().where(
                db.and_(
                    Animal.owner_id == User.user_id,
                    User.region.like(f'%{region}%')
                )
            )
            
            query = query.filter(
                db.or_(shelter_region_condition, owner_region_condition)
            )
        
        # 年齡篩選
        if min_age is not None or max_age is not None:
            age_in_months = func.timestampdiff(
                db.text('MONTH'),
                Animal.dob,
                func.curdate()
            )
            
            if min_age is not None:
                query = query.filter(age_in_months >= min_age)
            
            if max_age is not None:
                query = query.filter(age_in_months <= max_age)
        
        # 關鍵字搜尋
        if q:
            query = query.filter(
                db.or_(
                    Animal.name.like(f'%{q}%'),
                    Animal.description.like(f'%{q}%'),
                    Animal.breed.like(f'%{q}%')
                )
            )
        
        # 分頁
        pagination = query.order_by(Animal.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'animals': [animal.to_dict(include_relations=True) for animal in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def get_animal(animal_id: int) -> Animal:
        """
        獲取單一動物詳細資訊
        
        Args:
            animal_id: 動物 ID
            
        Returns:
            Animal: 動物物件
            
        Raises:
            NotFoundError: 動物不存在
        """
        animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
        
        if not animal:
            raise NotFoundError('動物不存在')
        
        return animal


# 創建全局實例
animal_service = AnimalService()
