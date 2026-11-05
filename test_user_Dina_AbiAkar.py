# test_user_Dina_AbiAkar.py
# Lab 7 - Python testing - Dina Abi Akar

import sqlite3

import pytest
from flask import json

import database
from database import (init_db, initial_users, insert_user, get_users,
                      get_user_by_id, update_user, delete_user)
from app import app


# ---------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------

@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    '''Before EVERY test: point the code at a brand-new, empty test
    database (so the real database.db is never touched), then run the
    same startup step the app runs when it first starts.'''
    test_db_file = tmp_path / "test_database.db"
    monkeypatch.setattr(database, "connect_to_db",
                        lambda: sqlite3.connect(test_db_file))
    init_db()


@pytest.fixture
def client():
    '''Returns a Flask test client for calling the API.'''
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def new_user():
    '''A user that is not in the database yet.'''
    return {
        "name": "Dina Abi Akar",
        "email": "dina@gmail.com",
        "phone": "71111111",
        "address": "Baabda, Mount Lebanon",
        "country": "Lebanon"
    }


# ---------------------------------------------------------------
# 1. The database is created with the specified users on first run
# ---------------------------------------------------------------

def test_database_created_with_initial_users():
    users = get_users()
    assert len(users) == len(initial_users)
    for expected, actual in zip(initial_users, users):
        assert actual["name"] == expected["name"]
        assert actual["email"] == expected["email"]
        assert actual["phone"] == expected["phone"]
        assert actual["address"] == expected["address"]
        assert actual["country"] == expected["country"]


def test_running_app_again_does_not_duplicate_users():
    init_db()  # simulate starting the app a second time
    assert len(get_users()) == len(initial_users)


# ---------------------------------------------------------------
# 2. insert_user()
# ---------------------------------------------------------------

def test_insert_user(new_user):
    inserted = insert_user(new_user)
    assert inserted["user_id"] == len(initial_users) + 1
    assert inserted["name"] == new_user["name"]
    assert inserted["email"] == new_user["email"]
    assert len(get_users()) == len(initial_users) + 1


# ---------------------------------------------------------------
# 3. get_users()
# ---------------------------------------------------------------

def test_get_users():
    users = get_users()
    assert isinstance(users, list)
    assert len(users) == 3
    names = [u["name"] for u in users]
    assert "John Doe" in names
    assert "Jane Smith" in names
    assert "Ali Hassan" in names


# ---------------------------------------------------------------
# 4. get_user_by_id()
# ---------------------------------------------------------------

def test_get_user_by_id():
    user = get_user_by_id(1)
    assert user["user_id"] == 1
    assert user["name"] == "John Doe"
    assert user["country"] == "Austria"


def test_get_user_by_id_not_found():
    assert get_user_by_id(999) == {}


# ---------------------------------------------------------------
# 5. update_user()
# ---------------------------------------------------------------

def test_update_user():
    changes = {
        "user_id": 1,
        "name": "John Updated",
        "email": "johnupdated@gmail.com",
        "phone": "000000",
        "address": "New Street, Beirut",
        "country": "Lebanon"
    }
    updated = update_user(changes)
    assert updated == changes
    assert get_user_by_id(1)["name"] == "John Updated"


# ---------------------------------------------------------------
# 6. delete_user()
# ---------------------------------------------------------------

def test_delete_user():
    result = delete_user(1)
    assert result["status"] == "User deleted successfully"
    assert get_user_by_id(1) == {}
    assert len(get_users()) == len(initial_users) - 1


# ---------------------------------------------------------------
# 7. api_get_user()  (plus api_get_users for the full list)
# ---------------------------------------------------------------

def test_api_get_users(client):
    response = client.get('/api/users')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert len(data) == 3
    assert "John Doe" in str(response.data)


def test_api_get_user(client):
    response = client.get('/api/users/2')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data["user_id"] == 2
    assert data["name"] == "Jane Smith"
    assert data["email"] == "janesmith@gmail.com"


# ---------------------------------------------------------------
# 8. api_add_user()
# ---------------------------------------------------------------

def test_api_add_user(client, new_user):
    response = client.post(
        '/api/users/add',
        data=json.dumps(new_user),
        content_type='application/json',
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data["user_id"] == 4
    assert data["name"] == new_user["name"]
    assert data["email"] == new_user["email"]
    # check it really got saved
    assert get_user_by_id(4)["name"] == new_user["name"]


# ---------------------------------------------------------------
# 9. api_update_user()
# ---------------------------------------------------------------

def test_api_update_user(client):
    changes = {
        "user_id": 3,
        "name": "Ali Updated",
        "email": "aliupdated@gmail.com",
        "phone": "70000000",
        "address": "Jounieh",
        "country": "Lebanon"
    }
    response = client.put(
        '/api/users/update',
        data=json.dumps(changes),
        content_type='application/json',
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data == changes
    assert get_user_by_id(3)["name"] == "Ali Updated"


# ---------------------------------------------------------------
# 10. api_delete_user()
# ---------------------------------------------------------------

def test_api_delete_user(client):
    response = client.delete('/api/users/delete/2')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data["status"] == "User deleted successfully"
    # check it is really gone
    response2 = client.get('/api/users/2')
    assert json.loads(response2.get_data(as_text=True)) == {}
