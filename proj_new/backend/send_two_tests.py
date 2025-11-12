from app.tasks.email_tasks import send_application_notification_email_task

contact_info = {
    'type': 'shelter',
    'name': '測試收容所',
    'email': 'shelter@test.com',
    'phone': '02-12345678'
}

recipient = 'fcdwii45@gmail.com'

# Approved
send_application_notification_email_task.delay(
    recipient,
    '測試郵件 - 已核准',
    'approved',
    '這是已核准的測試訊息，請確認範本顯示內容。',
    contact_info
)
print('Dispatched APPROVED email task to', recipient)

# Rejected
send_application_notification_email_task.delay(
    recipient,
    '測試郵件 - 未通過',
    'rejected',
    '這是未通過的測試訊息，請確認不會出現聯絡與取養提醒。',
    contact_info
)
print('Dispatched REJECTED email task to', recipient)
