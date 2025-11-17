"""
Animal Service - 動物相關業務邏輯
"""
from flask import current_app
from sqlalchemy import func, or_, exists
from app import db
from app.models.animal import Animal, AnimalStatus, Species, Sex
from app.models.user import User, UserRole
from app.models.shelter import Shelter
from app.services.audit_service import AuditService
from datetime import datetime


class AnimalService:
    """動物業務邏輯服務"""

    @staticmethod
    def search_animals(filters, current_user_id=None):
        """
        搜尋動物列表
        
        Args:
            filters: dict 包含篩選條件
            current_user_id: 當前用戶ID (可選)
        
        Returns:
            dict: 分頁結果
        """
        try:
            # 建立基礎查詢
            query = Animal.query.filter_by(deleted_at=None)
            
            # 權限過濾邏輯
            query = AnimalService._apply_permission_filter(query, filters, current_user_id)
            
            # 應用篩選條件
            query = AnimalService._apply_filters(query, filters)
            
            # 分頁
            page = filters.get('page', 1)
            per_page = min(filters.get('per_page', 20), 100)
            
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
            
        except Exception as e:
            current_app.logger.error(f"Animal search error: {str(e)}")
            raise

    @staticmethod
    def _apply_permission_filter(query, filters, current_user_id):
        """應用權限過濾"""
        owner_id = filters.get('owner_id')
        
        if owner_id:
            if current_user_id == owner_id:
                # 查詢自己的動物
                current_user = User.query.get(current_user_id)
                
                if (current_user and 
                    current_user.role == UserRole.SHELTER_MEMBER and 
                    current_user.primary_shelter_id):
                    # 收容所成員：查詢個人動物 + 收容所動物
                    query = query.filter(
                        or_(
                            Animal.owner_id == owner_id,
                            Animal.shelter_id == current_user.primary_shelter_id
                        )
                    )
                else:
                    # 一般用戶：只查詢個人動物
                    query = query.filter_by(owner_id=owner_id)
            else:
                # 查詢其他用戶的動物，只能看已發布的
                query = query.filter_by(
                    owner_id=owner_id, 
                    status=AnimalStatus.PUBLISHED
                )
        else:
            # 預設只顯示已發布的動物
            status = filters.get('status')
            if not status:
                query = query.filter_by(status=AnimalStatus.PUBLISHED)
        
        return query

    @staticmethod
    def _apply_filters(query, filters):
        """應用各種篩選條件"""
        # 物種篩選
        if filters.get('species'):
            try:
                query = query.filter_by(species=Species(filters['species']))
            except ValueError:
                raise ValueError('無效的物種值')
        
        # 性別篩選
        if filters.get('sex'):
            try:
                query = query.filter_by(sex=Sex(filters['sex']))
            except ValueError:
                raise ValueError('無效的性別值')
        
        # 狀態篩選
        if filters.get('status'):
            try:
                query = query.filter_by(status=AnimalStatus(filters['status']))
            except ValueError:
                raise ValueError('無效的狀態值')
        
        # 收容所篩選
        if filters.get('shelter_id'):
            query = query.filter_by(shelter_id=filters['shelter_id'])
        
        # 來源類型篩選
        if filters.get('source_type'):
            if filters['source_type'] == 'shelter':
                query = query.filter(Animal.shelter_id.isnot(None))
            elif filters['source_type'] == 'personal':
                query = query.filter(Animal.owner_id.isnot(None))
        
        # 地區篩選
        if filters.get('region'):
            query = AnimalService._apply_region_filter(query, filters['region'])
        
        # 年齡篩選
        if filters.get('min_age') is not None or filters.get('max_age') is not None:
            query = AnimalService._apply_age_filter(query, filters)
        
        # 關鍵字搜尋
        if filters.get('q'):
            q = filters['q']
            query = query.filter(
                or_(
                    Animal.name.like(f'%{q}%'),
                    Animal.description.like(f'%{q}%'),
                    Animal.breed.like(f'%{q}%')
                )
            )
        
        return query

    @staticmethod
    def _apply_region_filter(query, region):
        """應用地區篩選"""
        # 使用子查詢檢查收容所或擁有者的地區
        shelter_region_condition = exists().where(
            Animal.shelter_id == Shelter.shelter_id,
            Shelter.region.like(f'%{region}%')
        )
        
        owner_region_condition = exists().where(
            Animal.owner_id == User.user_id,
            User.region.like(f'%{region}%')
        )
        
        return query.filter(
            or_(shelter_region_condition, owner_region_condition)
        )

    @staticmethod
    def _apply_age_filter(query, filters):
        """應用年齡篩選"""
        age_in_months = func.timestampdiff(
            db.text('MONTH'),
            Animal.dob,
            func.curdate()
        )
        
        if filters.get('min_age') is not None:
            query = query.filter(age_in_months >= filters['min_age'])
        
        if filters.get('max_age') is not None:
            query = query.filter(age_in_months <= filters['max_age'])
        
        return query

    @staticmethod
    def get_animal_by_id(animal_id):
        """
        根據ID取得動物
        
        Args:
            animal_id: 動物ID
        
        Returns:
            dict: 動物資料
        
        Raises:
            ValueError: 動物不存在
        """
        animal = Animal.query.filter_by(
            animal_id=animal_id, 
            deleted_at=None
        ).first()
        
        if not animal:
            raise ValueError('動物不存在')
        
        return animal.to_dict(include_relations=True)

    @staticmethod
    def create_animal(data, user_id):
        """
        創建新動物
        
        Args:
            data: 動物資料
            user_id: 創建者ID
        
        Returns:
            dict: 創建的動物資料
        """
        try:
            # 資料驗證
            AnimalService._validate_animal_data(data)
            
            # 創建動物記錄
            animal = Animal(
                name=data['name'],
                species=Species(data['species']),
                sex=Sex(data['sex']),
                breed=data.get('breed'),
                age_months=data.get('age_months'),
                description=data.get('description'),
                owner_id=user_id,
                shelter_id=data.get('shelter_id'),
                status=AnimalStatus.DRAFT,
                created_by=user_id
            )
            
            db.session.add(animal)
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='animal.create',
                actor_id=user_id,
                target_type='animal',
                target_id=animal.animal_id,
                after_state=animal.to_dict()
            )
            
            return animal.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Create animal error: {str(e)}")
            raise

    @staticmethod
    def update_animal(animal_id, data, user_id):
        """
        更新動物資料
        
        Args:
            animal_id: 動物ID
            data: 更新資料
            user_id: 更新者ID
        
        Returns:
            dict: 更新後的動物資料
        """
        try:
            animal = Animal.query.filter_by(
                animal_id=animal_id,
                deleted_at=None
            ).first()
            
            if not animal:
                raise ValueError('動物不存在')
            
            # 權限檢查
            AnimalService._check_animal_permission(animal, user_id)
            
            # 記錄修改前狀態
            before_state = animal.to_dict()
            
            # 更新資料
            for field, value in data.items():
                if hasattr(animal, field) and field not in ['animal_id', 'created_at', 'updated_at']:
                    setattr(animal, field, value)
            
            animal.updated_at = datetime.utcnow()
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='animal.update',
                actor_id=user_id,
                target_type='animal',
                target_id=animal.animal_id,
                before_state=before_state,
                after_state=animal.to_dict()
            )
            
            return animal.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update animal error: {str(e)}")
            raise

    @staticmethod
    def delete_animal(animal_id, user_id):
        """
        刪除動物 (軟刪除)
        
        Args:
            animal_id: 動物ID
            user_id: 刪除者ID
        """
        try:
            animal = Animal.query.filter_by(
                animal_id=animal_id,
                deleted_at=None
            ).first()
            
            if not animal:
                raise ValueError('動物不存在')
            
            # 權限檢查
            AnimalService._check_animal_permission(animal, user_id)
            
            # 軟刪除
            animal.deleted_at = datetime.utcnow()
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='animal.delete',
                actor_id=user_id,
                target_type='animal',
                target_id=animal.animal_id,
                before_state=animal.to_dict()
            )
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Delete animal error: {str(e)}")
            raise

    @staticmethod
    def _validate_animal_data(data):
        """驗證動物資料"""
        required_fields = ['name', 'species', 'sex']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f'缺少必填欄位: {field}')
        
        # 驗證枚舉值
        try:
            Species(data['species'])
            Sex(data['sex'])
        except ValueError as e:
            raise ValueError(f'無效的枚舉值: {str(e)}')

    @staticmethod
    def _check_animal_permission(animal, user_id):
        """檢查動物操作權限"""
        user = User.query.get(user_id)
        
        if not user:
            raise ValueError('用戶不存在')
        
        # 管理員有所有權限
        if user.role == UserRole.ADMIN:
            return True
        
        # 動物擁有者有權限
        if animal.owner_id == user_id:
            return True
        
        # 收容所成員對所屬收容所動物有權限
        if (user.role == UserRole.SHELTER_MEMBER and 
            user.primary_shelter_id and 
            animal.shelter_id == user.primary_shelter_id):
            return True
        
        raise PermissionError('無權限操作此動物')

    @staticmethod
    def update_animal_status(animal_id, new_status, user_id, notes=None):
        """
        更新動物狀態
        
        Args:
            animal_id: 動物ID
            new_status: 新狀態
            user_id: 操作者ID
            notes: 備註
        
        Returns:
            dict: 更新後的動物資料
        """
        try:
            animal = Animal.query.filter_by(
                animal_id=animal_id,
                deleted_at=None
            ).first()
            
            if not animal:
                raise ValueError('動物不存在')
            
            # 權限檢查
            AnimalService._check_animal_permission(animal, user_id)
            
            # 狀態驗證
            try:
                target_status = AnimalStatus(new_status)
            except ValueError:
                raise ValueError('無效的狀態值')
            
            # 狀態轉換邏輯驗證
            AnimalService._validate_status_transition(animal.status, target_status)
            
            # 記錄修改前狀態
            before_state = animal.to_dict()
            
            # 更新狀態
            animal.status = target_status
            if notes:
                # 假設有 admin_notes 欄位，如果沒有可以忽略
                if hasattr(animal, 'admin_notes'):
                    animal.admin_notes = notes
            animal.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 記錄審計日誌
            AuditService.log(
                action='animal.status_update',
                actor_id=user_id,
                target_type='animal',
                target_id=animal.animal_id,
                before_state=before_state,
                after_state=animal.to_dict()
            )
            
            return animal.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update animal status error: {str(e)}")
            raise

    @staticmethod
    def batch_update_animal_status(animal_ids, new_status, user_id, shelter_id=None):
        """
        批次更新動物狀態
        
        Args:
            animal_ids: 動物ID列表
            new_status: 新狀態
            user_id: 操作者ID
            shelter_id: 收容所ID (可選，用於額外權限檢查)
        
        Returns:
            dict: 批次處理結果
        """
        try:
            # 狀態驗證
            try:
                target_status = AnimalStatus(new_status)
            except ValueError:
                raise ValueError('無效的狀態值')
            
            # 獲取要更新的動物
            query = Animal.query.filter(
                Animal.animal_id.in_(animal_ids),
                Animal.deleted_at == None
            )
            
            # 如果指定了收容所，額外檢查
            if shelter_id:
                query = query.filter(Animal.shelter_id == shelter_id)
            
            animals = query.all()
            
            if len(animals) != len(animal_ids):
                found_ids = [a.animal_id for a in animals]
                missing_ids = [aid for aid in animal_ids if aid not in found_ids]
                raise ValueError(f'以下動物不存在或無權限操作: {missing_ids}')
            
            # 批次處理
            success_count = 0
            failed_count = 0
            errors = []
            
            for animal in animals:
                try:
                    # 權限檢查
                    AnimalService._check_animal_permission(animal, user_id)
                    
                    # 狀態轉換驗證
                    AnimalService._validate_status_transition(animal.status, target_status)
                    
                    # 記錄修改前狀態
                    before_state = animal.to_dict()
                    
                    # 更新狀態
                    animal.status = target_status
                    animal.updated_at = datetime.utcnow()
                    
                    # 記錄審計日誌
                    AuditService.log(
                        action='animal.status_update',
                        actor_id=user_id,
                        target_type='animal',
                        target_id=animal.animal_id,
                        before_state=before_state,
                        after_state={'status': target_status.value}
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f'動物 {animal.animal_id} ({animal.name}): {str(e)}')
                    failed_count += 1
            
            # 如果有成功的更新，提交事務
            if success_count > 0:
                db.session.commit()
            
            return {
                'success_count': success_count,
                'failed_count': failed_count,
                'errors': errors,
                'total': len(animal_ids)
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Batch update animal status error: {str(e)}")
            raise

    @staticmethod
    def _validate_status_transition(current_status, new_status):
        """
        驗證狀態轉換是否有效
        
        Args:
            current_status: 當前狀態
            new_status: 目標狀態
        """
        # 狀態轉換規則
        valid_transitions = {
            AnimalStatus.DRAFT: [AnimalStatus.SUBMITTED, AnimalStatus.PUBLISHED],
            AnimalStatus.SUBMITTED: [AnimalStatus.DRAFT, AnimalStatus.PUBLISHED, AnimalStatus.RETIRED],
            AnimalStatus.PUBLISHED: [AnimalStatus.RETIRED, AnimalStatus.ADOPTED],
            AnimalStatus.RETIRED: [AnimalStatus.DRAFT, AnimalStatus.PUBLISHED],
            AnimalStatus.ADOPTED: []  # 已領養的動物無法變更狀態
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            status_map = {
                AnimalStatus.DRAFT: '草稿',
                AnimalStatus.SUBMITTED: '已提交',
                AnimalStatus.PUBLISHED: '已發布',
                AnimalStatus.RETIRED: '已下架',
                AnimalStatus.ADOPTED: '已領養'
            }
            
            raise ValueError(
                f'無法從 {status_map.get(current_status, current_status.value)} '
                f'變更為 {status_map.get(new_status, new_status.value)}'
            )