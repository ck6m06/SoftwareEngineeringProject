"""
Celery Application Configuration
"""
from celery import Celery
from app import create_app

# 創建 Flask 應用實例
flask_app = create_app()

# 創建 Celery 實例
celery = Celery(
    flask_app.import_name,
    broker=flask_app.config['CELERY_BROKER_URL'],
    backend=flask_app.config['CELERY_RESULT_BACKEND'],
    include=['app.tasks.animal_tasks', 'app.tasks.email_tasks']  # 明確指定 task 模組
)

# 更新 Celery 配置
celery.conf.update(flask_app.config)

class ContextTask(celery.Task):
    """Make celery tasks work with Flask app context"""
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask
