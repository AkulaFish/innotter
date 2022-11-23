import pytest


@pytest.mark.django_db
def test_register_user(client):
    payload = dict(
        email="user@user.com",
        role="user",
        title="user",
        username="user",
        first_name="Harry",
        last_name="Potter",
        image_s3_path="",
        password="userpass",
        password_repeat="userpass"
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
    payload = dict(
        email="user@user.com",
        role="user",
        title="user",
        username="user",
        first_name="Harry",
        last_name="Potter",
        password="userpass",
        password_repeat="userpass2"
    )

    response = client.post("/api/register/", payload)

    assert response.status_code == 400


@pytest.mark.django_db
def test_token_authentication(client, user):
    request = client.post(
        "/api/token/",
        dict(username="user", password="userpass")
    )

    assert "access" in request.data
    assert "refresh" in request.data


@pytest.mark.django_db
def test_get_list_of_users(client, user, admin):
    request = client.get("/api/users/")

    assert len(request.data) == 2


@pytest.mark.django_db
def test_retrieve_user(client, user_auth_token, user):
    client.login(username="user", password="userpass")
    response = client.get(r"/api/users/1/")

    assert response.data["id"] == 1


@pytest.mark.django_db
def test_block_user(client, user, admin):
    client.login(username="admin", password="adminpass")
    response = client.get("/api/users/1/block-unblock/")

    assert response.data["response"] == "User successfully blocked"


@pytest.mark.django_db
def test_block_user_without_permission(client, user2, admin):
    client.login(username="user2", password="userpass")
    response = client.get("/api/users/3/block-unblock/")

    assert response.status_code == 403
