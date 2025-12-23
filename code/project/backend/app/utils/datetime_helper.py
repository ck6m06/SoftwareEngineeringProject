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


def format_taipei_time(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """格式化台北時間"""
    if dt is None:
        return None
    taipei_dt = utc_to_taipei(dt)
    return taipei_dt.strftime(format_str)
