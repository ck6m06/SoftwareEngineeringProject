from app.tasks.email_tasks import send_application_notification_email_task

contact_info = {
    'type': 'shelter',
    'name': '測試收容所',
    'email': 'shelter@test.com',
    'phone': '02-12345678'
}

send_application_notification_email_task.delay(
    'fcdwii56@gmail.com',
    '測試郵件 - 老貓',
    'approved',
    '由測試觸發的審核通知',
    contact_info
)

print('Dispatched email task to fcdwii56@gmail.com')
