from app import create_app

app = create_app()

ctx = {
    'animal_name': '預覽動物',
    'status': 'approved',
    'message': 'Approved via automated test (preview)',
    'contact_info': {
        'type': 'shelter',
        'name': '測試收容所',
        'email': 'shelter@test.com',
        'phone': '02-12345678'
    }
}

with app.app_context():
    env = app.jinja_env
    render_ctx = dict(ctx)
    # expose app config for templates that reference current_app
    render_ctx['current_app'] = app

    print('--- Rendered TXT template (email/application_notification.txt) ---')
    try:
        t = env.get_template('email/application_notification.txt')
        print(t.render(**render_ctx))
    except Exception as e:
        print('TXT template render error:', e)

    print('\n--- Rendered HTML template (email/application_notification.html) ---')
    try:
        h = env.get_template('email/application_notification.html')
        print(h.render(**render_ctx))
    except Exception as e:
        print('HTML template render error:', e)
