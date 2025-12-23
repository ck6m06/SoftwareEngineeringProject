"""
Permission Service - 權限檢查服務
集中管理所有權限邏輯，避免重複代碼
"""
from app.models.user import User, UserRole
from app.models.animal import Animal
from app.models.application import Application
from typing import Optional


class PermissionService:
    """權限服務類"""
    
    @staticmethod
    def can_manage_animal(user: User, animal: Animal) -> bool:
        """
        檢查用戶是否可以管理動物（編輯、刪除等）
        
        規則：
        1. 個人送養動物：只有動物擁有者可以管理
        2. 收容所動物：該收容所的成員可以管理
        3. 管理員可以管理收容所動物（但不能編輯個人送養動物）
        
        Args:
            user: 當前用戶
            animal: 要管理的動物
            
        Returns:
            bool: 是否有權限
        """
        if not user or not animal:
            return False
        
        # 個人送養動物：只有擁有者可以管理
        if animal.owner_id:
            return animal.owner_id == user.user_id
        
        # 收容所動物：收容所成員或管理員可以管理
        if animal.shelter_id:
            # 收容所成員必須屬於同一個收容所
            if user.role == UserRole.SHELTER_MEMBER:
                return user.primary_shelter_id == animal.shelter_id
            # 管理員可以管理收容所動物
            if user.role == UserRole.ADMIN:
                return True
        
        return False
    
    @staticmethod
    def can_view_animal(user: Optional[User], animal: Animal) -> bool:
        """
        檢查用戶是否可以查看動物詳情
        
        規則：
        1. 已發布的動物：所有人可見
        2. 草稿/待審核動物：只有擁有者/收容所成員/管理員可見
        
        Args:
            user: 當前用戶（可為 None 表示未登入）
            animal: 要查看的動物
            
        Returns:
            bool: 是否有權限
        """
        from app.models.animal import AnimalStatus
        
        # 已發布的動物所有人可見
        if animal.status == AnimalStatus.PUBLISHED:
            return True
        
        # 未登入用戶只能看已發布的
        if not user:
            return False
        
        # 擁有者/管理員可以查看所有狀態
        return PermissionService.can_manage_animal(user, animal)
    
    @staticmethod
    def can_review_application(user: User, application: Application) -> bool:
        """
        檢查用戶是否可以審核申請
        
        規則：
        1. 個人送養：只有動物擁有者可以審核
        2. 收容所送養：該收容所的成員可以審核
        3. 管理員不能審核（應由送養人審核）
        
        Args:
            user: 當前用戶
            application: 要審核的申請
            
        Returns:
            bool: 是否有權限
        """
        if not user or not application:
            return False
        
        animal = application.animal
        if not animal:
            return False
        
        # 個人送養：只有動物擁有者可以審核
        if animal.owner_id:
            return animal.owner_id == user.user_id
        
        # 收容所送養：該收容所的成員可以審核
        if animal.shelter_id:
            if user.role == UserRole.SHELTER_MEMBER:
                return user.primary_shelter_id == animal.shelter_id
        
        return False
    
    @staticmethod
    def can_view_application(user: User, application: Application) -> bool:
        """
        檢查用戶是否可以查看申請詳情
        
        規則：
        1. 申請人本人可以查看
        2. 動物擁有者/收容所成員可以查看
        3. 管理員可以查看所有申請
        
        Args:
            user: 當前用戶
            application: 要查看的申請
            
        Returns:
            bool: 是否有權限
        """
        if not user or not application:
            return False
        
        # 申請人本人
        if application.applicant_id == user.user_id:
            return True
        
        # 管理員可以查看所有
        if user.role == UserRole.ADMIN:
            return True
        
        # 動物擁有者/收容所成員
        animal = application.animal
        if animal:
            return PermissionService.can_manage_animal(user, animal)
        
        return False
    
    @staticmethod
    def can_submit_animal_for_review(user: User, animal: Animal) -> bool:
        """
        檢查用戶是否可以提交動物供審核
        
        規則：只有動物的管理者可以提交
        
        Args:
            user: 當前用戶
            animal: 要提交的動物
            
        Returns:
            bool: 是否有權限
        """
        return PermissionService.can_manage_animal(user, animal)
    
    @staticmethod
    def can_publish_animal(user: User, animal: Animal) -> bool:
        """
        檢查用戶是否可以發布動物
        
        規則：只有管理員可以發布動物
        
        Args:
            user: 當前用戶
            animal: 要發布的動物
            
        Returns:
            bool: 是否有權限
        """
        return user and user.role == UserRole.ADMIN
    
    @staticmethod
    def can_reject_animal(user: User, animal: Animal) -> bool:
        """
        檢查用戶是否可以拒絕動物上架
        
        規則：只有管理員可以拒絕
        
        Args:
            user: 當前用戶
            animal: 要拒絕的動物
            
        Returns:
            bool: 是否有權限
        """
        return user and user.role == UserRole.ADMIN


# 創建全局實例
permission_service = PermissionService()
