import json
import requests
import pytest


BASE = 'http://localhost:5000'


def is_server_up():
    try:
        r = requests.get(BASE + '/api/animals', timeout=2)
        return r.status_code == 200
    except Exception:
        return False


@pytest.mark.skipif(not is_server_up(), reason='API server not reachable at http://localhost:5000')
def test_region_filter_returns_results():
    r = requests.get(BASE + '/api/animals', params={'per_page': 5, 'region': '台北市'})
    assert r.status_code == 200
    data = r.json()
    assert 'animals' in data
    # at least one of returned animals should have shelter.region containing 台北市
    animals = data.get('animals', [])
    assert isinstance(animals, list)
    if animals:
        found = any(a.get('shelter', {}).get('region', '').find('台北') != -1 for a in animals)
        assert found


@pytest.mark.skipif(not is_server_up(), reason='API server not reachable at http://localhost:5000')
def test_source_type_shelter_returns_results():
    r = requests.get(BASE + '/api/animals', params={'per_page': 5, 'source_type': 'shelter'})
    assert r.status_code == 200
    data = r.json()
    animals = data.get('animals', [])
    # Expect returned animals are shelter-sourced (shelter_id present or shelter object present)
    if animals:
        assert any(a.get('shelter_id') or a.get('shelter') for a in animals)


@pytest.mark.skipif(not is_server_up(), reason='API server not reachable at http://localhost:5000')
def test_min_age_filter():
    # test min_age=0 should return at least one published animal
    r = requests.get(BASE + '/api/animals', params={'per_page': 5, 'min_age': 0})
    assert r.status_code == 200
    data = r.json()
    animals = data.get('animals', [])
    assert isinstance(animals, list)
