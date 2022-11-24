import datetime
import json
from unittest import mock
from collections import OrderedDict

import pytest

from core.models import Tag


@pytest.mark.django_db
def test_get_pages(client, user, user_page, private_user_page):
    """Test get all pages"""
    client.login(username="user", password="userpass")
    response = client.get("/api/pages/")

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["id"] == user_page.pk
    assert response.data[1]["id"] == private_user_page.pk


@pytest.mark.django_db
def test_retrieve_page(client, user, user_page):
    """Test get single page"""
    client.login(username="user", password="userpass")
    response = client.get(f"/api/pages/{user_page.pk}/")

    assert response.status_code == 200
    assert response.data["id"] == user_page.pk


@pytest.mark.django_db
def test_page_create(client, user):
    """Test creating page"""
    payload = {
        "name": "UserPage",
        "description": "This is the first page of this user",
        "image": None,
        "tags": [{"name": "SomeTag"}],
        "is_private": True,
    }
    client.login(username="user", password="userpass")
    response = client.post("/api/pages/", payload, format="json")
    data = response.data

    assert response.status_code == 201
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert Tag.objects.filter(name=payload["tags"][0]["name"]).exists()
    assert data["is_private"] == payload["is_private"]


@pytest.mark.django_db
def test_page_update(client, user, user_page, tag):
    """Test updating page"""
    payload = {
        "name": "UserPage",
        "description": "This is the first page of this user",
        "image": None,
        "tags": [{"name": "SomeTag"}],
        "is_private": True,
    }

    client.login(username="user", password="userpass")
    response = client.put(f"/api/pages/{user_page.pk}/", payload, format="json")

    assert response.status_code == 200
    assert Tag.objects.filter(name=payload["tags"][0]["name"]).exists()


@pytest.mark.django_db
def test_follow_unfollow_page(client, user_page, admin):
    """Test follow and unfollow page functionality"""
    client.login(username="admin", password="adminpass")
    response = client.put(f"/api/pages/{user_page.pk}/follow-unfollow/")

    assert response.data["response"] == "Now you follow this page."
    assert len(user_page.followers.all()) == 1
    assert user_page.followers.all()[0] == admin

    response = client.get(f"/api/pages/{user_page.pk}/follow-unfollow/")

    assert response.data["response"] == "You're successfully unsubscribed."
    assert len(user_page.followers.all()) == 0


@pytest.mark.django_db
def test_send_request_to_page(client, private_user_page, admin):
    """Test sending request for follow page in case if page is private"""
    client.login(username="admin", password="adminpass")
    response = client.put(f"/api/pages/{private_user_page.pk}/follow-unfollow/")

    assert response.data["response"] == "Owner of the page will review your request."
    assert len(private_user_page.follow_requests.all()) == 1
    assert private_user_page.follow_requests.all()[0] == admin


@pytest.mark.django_db
def test_accept_single_request(client, admin, private_user_page):
    """Test accepting single request by page owner"""
    private_user_page.follow_requests.set([admin])
    client.login(username="user", password="userpass")
    response = client.put(
        f"/api/pages/{private_user_page.pk}/requests/accept/{admin.pk}"
    )

    assert response.status_code == 200
    assert len(private_user_page.follow_requests.all()) == 0
    assert len(private_user_page.followers.all()) == 1
    assert private_user_page.followers.all()[0] == admin


@pytest.mark.django_db
def test_accept_all_requests(
    client,
    user,
    moderator,
    admin,
    private_user_page,
):
    """Test accepting all requests with single request"""
    private_user_page.follow_requests.set([admin, moderator])
    private_user_page.save()
    client.login(username="user", password="userpass")
    response = client.put(f"/api/pages/{private_user_page.pk}/requests/accept/")

    assert response.status_code == 200
    assert response.data["response"] == "All requests have been accepted"
    assert len(private_user_page.follow_requests.all()) == 0
    assert len(private_user_page.followers.all()) == 2
    assert private_user_page.followers.all()[0] == moderator
    assert private_user_page.followers.all()[1] == admin


@pytest.mark.django_db
def test_decline_single_requests(client, admin, private_user_page):
    """Test declining single request"""
    private_user_page.follow_requests.set([admin])
    client.login(username="user", password="userpass")
    response = client.put(
        f"/api/pages/{private_user_page.pk}/requests/decline/{admin.pk}"
    )

    assert response.status_code == 200
    assert len(private_user_page.follow_requests.all()) == 0
    assert len(private_user_page.followers.all()) == 0


@pytest.mark.django_db
def test_decline_all_requests(client, admin, moderator, user, private_user_page):
    """Test declining all requests with one request"""
    private_user_page.follow_requests.set([admin, moderator])
    client.login(username="user", password="userpass")
    response = client.put(f"/api/pages/{private_user_page.pk}/requests/decline/")

    assert response.status_code == 200
    assert len(private_user_page.follow_requests.all()) == 0
    assert len(private_user_page.followers.all()) == 0


@pytest.mark.django_db
def test_get_requests(client, private_user_page, user, admin, moderator):
    """Test get all request for a user page"""
    private_user_page.follow_requests.set([admin, moderator])
    client.login(username="user", password="userpass")
    response = client.get(f"/api/pages/{private_user_page.pk}/requests/")

    assert len(response.data) == 2
    assert private_user_page.follow_requests.all()[0] == admin
    assert private_user_page.follow_requests.all()[1] == moderator


@pytest.mark.django_db
def test_accept_request_of_not_your_page(
    client, private_user_page, user, admin, moderator, user_additional
):
    """Test trying to accept request that doesn't belong to current user page"""
    private_user_page.follow_requests.set([admin, moderator])
    private_user_page.save()
    client.login(username="user2", password="userpass")
    response = client.put(f"/api/pages/{private_user_page.pk}/requests/accept/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_decline_request_of_not_your_page(
    client, private_user_page, user, admin, moderator, user_additional
):
    """Test trying to decline request that doesn't belong to current user page"""
    private_user_page.follow_requests.set([admin, moderator])
    private_user_page.save()
    client.login(username="user2", password="userpass")
    response = client.put(f"/api/pages/{private_user_page.pk}/requests/decline/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_get_requests_of_not_your_page(
    client, private_user_page, user, admin, moderator, user_additional
):
    """Test trying to get requests that don't belong to current user page"""
    private_user_page.follow_requests.set([admin, moderator])
    client.login(username="user2", password="userpass")
    response = client.get(f"/api/pages/{private_user_page.pk}/requests/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_block_page_without_permission(client, user_page, user_additional):
    """Testing blocking without admin or moderator privilege"""
    payload = {"permanent_block": True, "unblock_date": "2030-11-30T00:00:00+01:00"}
    client.login(username="user2", password="userpass")
    response = client.put(f"/api/block-page/{user_page.pk}/", payload, format="json")

    assert response.status_code == 403
