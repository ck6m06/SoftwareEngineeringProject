"""
Custom Exceptions for Business Logic
統一的業務異常處理
"""

class BusinessException(Exception):
    """業務邏輯異常基類"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class PermissionDeniedError(BusinessException):
    """權限不足異常"""
    def __init__(self, message: str = '無權限執行此操作'):
        super().__init__(message, status_code=403)


class NotFoundError(BusinessException):
    """資源不存在異常"""
    def __init__(self, message: str = '資源不存在'):
        super().__init__(message, status_code=404)


class ValidationError(BusinessException):
    """資料驗證異常"""
    def __init__(self, message: str = '資料驗證失敗'):
        super().__init__(message, status_code=400)


class ConflictError(BusinessException):
    """資源衝突異常（如重複申請）"""
    def __init__(self, message: str = '資源衝突'):
        super().__init__(message, status_code=409)


class UnauthorizedError(BusinessException):
    """未授權異常"""
    def __init__(self, message: str = '未授權'):
        super().__init__(message, status_code=401)
