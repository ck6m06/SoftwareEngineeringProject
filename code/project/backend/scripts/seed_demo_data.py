#!/usr/bin/env python3
"""
Seed demo data for animals/shelters to help test filters (region/source/age).

This script uses raw pymysql to avoid depending on app factory imports. It
reads DATABASE_URL from environment if available, otherwise attempts sensible
defaults for the Docker Compose setup.

Run inside the backend container (recommended):
  docker-compose exec backend python backend/scripts/seed_demo_data.py
"""
import os
import json
from urllib.parse import urlparse

try:
    import pymysql
except ImportError:
    raise SystemExit("pymysql is required. Install via pip install pymysql")


def get_db_conn():
    database_url = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URI')
    if database_url:
        # expect format mysql+pymysql://user:pass@host:port/db
        if database_url.startswith('mysql'):
            if database_url.startswith('mysql+pymysql://'):
                url = database_url.replace('mysql+pymysql://', 'mysql://')
            else:
                url = database_url
            parsed = urlparse(url)
            user = parsed.username or 'petuser'
            password = parsed.password or 'petpassword'
            host = parsed.hostname or 'mysql'
            port = parsed.port or 3306
            db = parsed.path.lstrip('/')
        else:
            # fallback
            user = 'petuser'
            password = 'petpassword'
            host = 'mysql'
            port = 3306
            db = 'pet_adoption'
    else:
        # default for docker-compose container network
        user = os.environ.get('DB_USER', 'petuser')
        password = os.environ.get('DB_PASSWORD', 'petpassword')
        host = os.environ.get('DB_HOST', 'mysql')
        port = int(os.environ.get('DB_PORT', 3306))
        db = os.environ.get('DB_NAME', 'pet_adoption')

    conn = pymysql.connect(host=host, user=user, password=password, port=port, database=db, charset='utf8mb4')
    return conn


def seed():
    conn = get_db_conn()
    cur = conn.cursor()

    # create a demo shelter if not exists
    shelter_name = '測試收容所'
    address = {
        'city': '台北市',
        'county': '測試區',
        'street': '台北市測試區測試路123號',
        'postal_code': '100'
    }

    cur.execute("SELECT shelter_id FROM shelters WHERE name=%s LIMIT 1", (shelter_name,))
    row = cur.fetchone()
    if row:
        shelter_id = row[0]
        print('Shelter exists id=', shelter_id)
    else:
        cur.execute(
            "INSERT INTO shelters (name, contact_email, contact_phone, address, verified, primary_account_user_id) VALUES (%s,%s,%s,%s,%s,%s)",
            (shelter_name, 'shelter@test.com', '02-12345678', json.dumps(address, ensure_ascii=False), True, 2)
        )
        conn.commit()
        shelter_id = cur.lastrowid
        print('Inserted shelter id=', shelter_id)

    # ensure shelters.region is filled from address if empty
    try:
        cur.execute("UPDATE shelters SET region = JSON_UNQUOTE(JSON_EXTRACT(address,'$.city')) WHERE (region IS NULL OR region='') AND address IS NOT NULL")
        conn.commit()
    except Exception:
        pass

    # seed animals: some with shelter_id, some with owner only, and varied dob
    animals = [
        {'name': '老貓', 'species': 'CAT', 'sex': 'FEMALE', 'dob': '2022-01-01', 'shelter_id': shelter_id, 'owner_id': None, 'status': 'PUBLISHED'},
        {'name': '年輕狗', 'species': 'DOG', 'sex': 'MALE', 'dob': '2025-10-06', 'shelter_id': shelter_id, 'owner_id': None, 'status': 'PUBLISHED'},
        {'name': '未知年齡', 'species': 'CAT', 'sex': 'MALE', 'dob': None, 'shelter_id': None, 'owner_id': 4, 'status': 'PUBLISHED'},
    ]

    for a in animals:
        cur.execute("SELECT animal_id FROM animals WHERE name=%s LIMIT 1", (a['name'],))
        if cur.fetchone():
            print('Animal already exists:', a['name'])
            continue
        cur.execute(
            "INSERT INTO animals (name, species, sex, dob, shelter_id, owner_id, status, created_by, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())",
            (a['name'], a['species'], a['sex'], a['dob'], a['shelter_id'], a['owner_id'], a['status'], 1)
        )
        conn.commit()
        print('Inserted animal:', a['name'])

    cur.close()
    conn.close()


if __name__ == '__main__':
    print('Seeding demo data...')
    seed()
    print('Done.')
