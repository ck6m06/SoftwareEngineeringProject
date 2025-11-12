import sys
from datetime import datetime

try:
    # create_app is expected at backend/app/__init__.py as create_app()
    from app import create_app, db
    from app.models import Application, Animal, User
    from app.tasks.email_tasks import send_application_notification_email_task
except Exception as e:
    print('Import error:', e)
    sys.exit(2)


APP_ID = 7


def main():
    app = create_app()
    with app.app_context():
        # Print SMTP-related runtime config (no passwords)
        smtp_host = app.config.get('SMTP_HOST')
        smtp_port = app.config.get('SMTP_PORT')
        smtp_use_tls = app.config.get('SMTP_USE_TLS')
        smtp_use_ssl = app.config.get('SMTP_USE_SSL')
        smtp_from = app.config.get('SMTP_FROM')
        print(f"[RUNTIME SMTP] HOST={smtp_host} PORT={smtp_port} USE_TLS={smtp_use_tls} USE_SSL={smtp_use_ssl} FROM={smtp_from}")

        # Load application
        app_obj = Application.query.get(APP_ID)
        if not app_obj:
            print(f'Application id={APP_ID} not found')
            return

        # Update status to APPROVED if not already
        try:
            app_obj.status = 'APPROVED'
            app_obj.reviewed_at = datetime.utcnow()
            app_obj.review_notes = 'Approved via automated test'
            db.session.add(app_obj)
            db.session.commit()
            print(f'Application {APP_ID} set to APPROVED')
        except Exception as e:
            db.session.rollback()
            print('DB update error:', e)
            return

        # Build contact_info from animal owner or shelter
        animal = Animal.query.get(app_obj.animal_id)
        contact_info = {}
        if animal is None:
            print('Animal for application not found')
        else:
            owner = getattr(animal, 'owner', None)
            shelter = getattr(animal, 'shelter', None)
            if owner:
                contact_info = {
                    'type': 'owner',
                    'name': getattr(owner, 'username', getattr(owner, 'name', None)),
                    'email': getattr(owner, 'email', None),
                    'phone': getattr(owner, 'phone', None),
                }
            elif shelter:
                contact_info = {
                    'type': 'shelter',
                    'name': getattr(shelter, 'name', None),
                    'email': getattr(shelter, 'email', None),
                    'phone': getattr(shelter, 'phone', None),
                }
            else:
                contact_info = {'type': 'unknown'}

        recipient = None
        # get applicant email
        applicant = User.query.get(app_obj.applicant_id)
        if applicant:
            recipient = getattr(applicant, 'email', None)

        # Fallback recipient to the one you provided (user requested test email)
        if not recipient:
            recipient = 'fcdwii56@gmail.com'

        animal_name = getattr(animal, 'name', 'animal') if animal else 'animal'

        print(f'Enqueue email task to {recipient} for animal "{animal_name}" with contact_info={contact_info}')
        try:
            send_application_notification_email_task.delay(recipient, animal_name, 'approved', app_obj.review_notes or '', contact_info)
            print('Email task enqueued (delay called).')
        except Exception as e:
            print('Failed to enqueue email task:', e)


if __name__ == '__main__':
    main()
