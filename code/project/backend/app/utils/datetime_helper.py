"""
DateTime Utility Functions for Taipei Timezone
"""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# 台北時區
TAIPEI_TZ = ZoneInfo("Asia/Taipei")


def now_taipei():
    """獲取當前台北時間"""
    return datetime.now(TAIPEI_TZ)


def utc_to_taipei(dt):
    """將 UTC 時間轉換為台北時間"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # 假設是 UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TAIPEI_TZ)


def taipei_to_utc(dt):
    """將台北時間轉換為 UTC"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # 假設是台北時間
        dt = dt.replace(tzinfo=TAIPEI_TZ)
    return dt.astimezone(timezone.utc)


def get_naive_taipei_now():
    """
    取得當前台北時間（naive datetime，不含時區資訊）
    用於 SQLAlchemy 的 default 參數
    
    Returns:
        datetime: 台北時間的 naive datetime
    """
    return datetime.now(TAIPEI_TZ).replace(tzinfo=None)


def format_taipei_time(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """格式化台北時間"""
    if dt is None:
        return None
    taipei_dt = utc_to_taipei(dt)
    return taipei_dt.strftime(format_str)


def to_taipei_isoformat(dt):
    """
    將 naive datetime（假設為台北時間）轉換為帶時區的 ISO 格式字串
    用於 API 序列化，讓前端能正確解析時區
    
    Args:
        dt: naive datetime 對象（假設為台北時間）
        
    Returns:
        str: ISO 格式字串，包含時區信息（如 "2025-11-02T17:06:44+08:00"）
    """
    if dt is None:
        return None
    # 為 naive datetime 添加台北時區信息
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TAIPEI_TZ)
    return dt.isoformat()
