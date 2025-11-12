"""
Security Utilities
"""
import bcrypt
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from typing import Optional
import hmac
import hashlib
import secrets


def hash_password(password: str) -> str:
    """
    將密碼進行雜湊
    
    Args:
        password: 明文密碼
    
    Returns:
        雜湊後的密碼
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    驗證密碼
    
    Args:
        password: 明文密碼
        password_hash: 雜湊後的密碼
    
    Returns:
        是否匹配
    """
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def generate_verification_token(user_id: int, purpose: str = 'email-verify') -> str:
    """
    生成驗證 token
    
    Args:
        user_id: 用戶 ID
        purpose: token 用途 (email-verify, password-reset)
    
    Returns:
        token 字符串
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps({'user_id': user_id, 'purpose': purpose}, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def verify_token(token: str, purpose: str = 'email-verify', max_age: int = 86400) -> Optional[int]:
    """
    驗證 token 並返回用戶 ID
    
    Args:
        token: token 字符串
        purpose: 預期的 token 用途
        max_age: token 有效期（秒），預設 24 小時
    
    Returns:
        用戶 ID，如果無效則返回 None
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=max_age
        )
        if data.get('purpose') != purpose:
            return None
        return data.get('user_id')
    except Exception:
        return None


def generate_numeric_code(length: int = 6) -> str:
    """
    產生 numeric 驗證碼 (預設 6 位)
    """
    # 使用 cryptographically secure generator
    if length <= 0:
        raise ValueError('length must be a positive integer')
    max_value = 10 ** length
    # secrets.randbelow(max_value) 回傳 0..max_value-1
    code = str(secrets.randbelow(max_value)).zfill(length)
    return code


def hash_verification_code(code: str) -> str:
    """
    使用 HMAC-SHA256 對驗證碼做簽章，返回 hex 字串
    """
    key = current_app.config.get('SECRET_KEY', 'dev-secret').encode('utf-8')
    mac = hmac.new(key, code.encode('utf-8'), hashlib.sha256)
    return mac.hexdigest()


def verify_verification_code(code: str, code_hash: str) -> bool:
    """
    驗證提供的 code 是否與存放的 hash 相符
    """
    expected = hash_verification_code(code)
    # 使用 hmac.compare_digest 避免 timing attack
    return hmac.compare_digest(expected, code_hash)
