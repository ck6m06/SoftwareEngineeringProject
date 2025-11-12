#!/usr/bin/env python
"""
Celery Worker 啟動腳本
"""
import sys
import os

# 將專案根目錄加入 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.celery import celery
from app.tasks import *  # 導入所有 tasks

if __name__ == '__main__':
    # 啟動 Celery Worker
    # 參數說明:
    # -A: Celery app 實例
    # --loglevel=info: 日誌級別
    # --pool=solo: Windows 專用的 pool (避免 fork 問題)
    # --concurrency=4: 並發數量
    
    celery.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',  # Windows 使用 solo pool
        '--concurrency=4'
    ])
