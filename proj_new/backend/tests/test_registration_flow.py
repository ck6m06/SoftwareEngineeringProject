import json
import pytest

from app import create_app, db
from app.models import PendingRegistration, User
from app.utils import security


@pytest.fixture()
def app():
    app = create_app('testing')
    with app.app_context():
        # create all tables in in-memory sqlite
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_register_and_verify_flow(app):
    client = app.test_client()

    # 1) register -> should create a pending registration
    payload = {
        'email': 'int_test_user@example.invalid',
        'password': 'Test12345',
        'username': 'inttester',
        'phone_number': '0912000000'
    }

    resp = client.post('/api/auth/register', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'pending_id' in data
    pending_id = data['pending_id']

    # 2) overwrite the pending verification_code_hash with a known code (test-only)
    with app.app_context():
        p = PendingRegistration.query.get(pending_id)
        assert p is not None
        test_code = '123456'
        p.verification_code_hash = security.hash_verification_code(test_code)
        db.session.commit()

    # 3) verify-registration with the known code -> should create a user
    verify_resp = client.post('/api/auth/verify-registration', json={'pending_id': pending_id, 'code': test_code})
    assert verify_resp.status_code == 200
    vdata = verify_resp.get_json()
    assert vdata.get('message') and '成功' in vdata.get('message')

    # 4) confirm user exists and pending is removed
    with app.app_context():
        user = User.query.filter_by(email=payload['email']).first()
        assert user is not None
        assert user.verified is True
        p2 = PendingRegistration.query.get(pending_id)
        assert p2 is None


def test_resend_registration_code_limits(app):
    client = app.test_client()

    # create pending by registering
    payload = {'email': 'resend_user@example.invalid', 'password': 'Test12345'}
    resp = client.post('/api/auth/register', json=payload)
    assert resp.status_code == 201
    pending_id = resp.get_json()['pending_id']

    # call resend up to limit
    for i in range(5):
        r = client.post('/api/auth/resend-registration-code', json={'pending_id': pending_id})
        assert r.status_code == 200

    # 6th attempt should be rate limited (429)
    r = client.post('/api/auth/resend-registration-code', json={'pending_id': pending_id})
    assert r.status_code == 429
