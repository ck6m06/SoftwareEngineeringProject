"""
Celery Tasks
"""
from app.celery import celery

# Import tasks to register them with Celery
from app.tasks.animal_tasks import (
    process_animal_batch_import,
    process_animal_batch_export
)
from app.tasks.email_tasks import (
    send_verification_email_task,
    send_password_reset_email_task,
    send_application_notification_email_task,
    send_bulk_notification_email_task
)

__all__ = [
    'celery',
    'process_animal_batch_import',
    'process_animal_batch_export',
    'send_verification_email_task',
    'send_password_reset_email_task',
    'send_application_notification_email_task',
    'send_bulk_notification_email_task'
]
