import pytest


@pytest.mark.django_db
def test_register_user(client):
    """Testing user registration"""
    payload = dict(
        email="user@user.com",
        role="user",
        title="user",
        username="user",
        first_name="Harry",
        last_name="Potter",
        image_s3_path="",
        password="userpass",
        password_repeat="userpass",
    )

    response = client.post("/api/register/", payload)
    data = response.data

    assert data["email"] == payload["email"]
    assert data["role"] == payload["role"]
    assert data["title"] == payload["title"]
    assert data["username"] == payload["username"]
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]
    assert "password" not in data
    assert "password_repeat" not in data


@pytest.mark.django_db
def test_register_incorrect_repeated_password(client):
    """Testing registration with incorrect data"""
    payload = dict(
        email="user@user.com",
        role="user",
        title="user",
        username="user",
        first_name="Harry",
        last_name="Potter",
        password="userpass",
        password_repeat="userpass2",
    )

    response = client.post("/api/register/", payload)

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
    response = client.get(f"/api/users/{user.pk}/block-unblock/")

    assert response.status_code == 200
    assert response.data["response"] == "User successfully blocked"


@pytest.mark.django_db
def test_block_user_without_permission(client, user_additional, admin):
    """Testing user block by another user without privileges"""
    client.login(username="user2", password="userpass")
    response = client.get(f"/api/users/{admin.pk}/block-unblock/")

    assert response.status_code == 403
