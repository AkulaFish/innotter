import pytest


@pytest.mark.django_db
def test_register_user(client, user_payload):
    """Testing user registration"""
    response = client.post("/api/register/", user_payload)
    data = response.data

    assert data["email"] == user_payload["email"]
    assert data["role"] == user_payload["role"]
    assert data["title"] == user_payload["title"]
    assert data["username"] == user_payload["username"]
    assert data["first_name"] == user_payload["first_name"]
    assert data["last_name"] == user_payload["last_name"]
    assert "password" not in data
    assert "password_repeat" not in data


@pytest.mark.django_db
def test_register_incorrect_repeated_password(client, incorrect_user_payload):
    """Testing registration with incorrect data"""
    response = client.post("/api/register/", incorrect_user_payload)

    assert response.status_code == 400


@pytest.mark.django_db
def test_token_authentication(client, user):
    """Testing token authentication"""
    request = client.post("/api/token/", dict(username="user", password="userpass"))

    assert "access" in request.data
    assert "refresh" in request.data


@pytest.mark.django_db
def test_get_list_of_users(client, user, admin):
    """Testing getting list of all users"""
    request = client.get("/api/users/")

    assert len(request.data) == 2


@pytest.mark.django_db
def test_retrieve_user(client, user_auth_token, user):
    """Testing retrieve single user"""
    client.login(username="user", password="userpass")
    response = client.get(f"/api/users/{user.pk}/")

    assert response.data["id"] == user.pk


@pytest.mark.django_db
def test_block_user(client, user, admin):
    """Testing user block by admin"""
    client.login(username="admin", password="adminpass")
    response = client.put(f"/api/users/{user.pk}/block-unblock/")

    assert response.status_code == 200
    assert response.data["response"] == "User successfully blocked"


@pytest.mark.django_db
def test_block_user_without_permission(client, user_additional, admin):
    """Testing user block by another user without privileges"""
    client.login(username="user2", password="userpass")
    response = client.put(f"/api/users/{admin.pk}/block-unblock/")

    assert response.status_code == 403
