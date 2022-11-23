import pytest


@pytest.mark.django_db
def test_create_tag(client, user):
    """Test create tag"""
    payload = dict(
        name="SomeTag"
    )
    client.login(username="user", password="userpass")
    response = client.post("/api/tags/", payload)

    assert response.status_code == 201
    assert response.data["name"] == payload["name"]


@pytest.mark.django_db
def test_get_tags(client, user, tag, tag2):
    """Test get all the tags"""
    client.login(username="user", password="userpass")
    response = client.get("/api/tags/")

    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_retrieve_tag(client, user, tag):
    """Test get single tag"""
    client.login(username="user", password="userpass")
    response = client.get("/api/tags/1/")

    assert response.status_code == 200
    assert response.data["name"] == "SomeTag"

