from unittest.mock import patch

import pytest


@pytest.mark.django_db
@patch("core.views.produce.delay")
@patch("core.views.send_new_post_notification_email.delay")
def test_create_post(
    produce_delay,
    send_email,
    client,
    user_page,
    user,
    post_on_private_page,
    post_payload,
):
    """Test creating post on user page that replies to another post"""
    client.login(username="user", password="userpass")
    response = client.post("/api/posts/", post_payload)

    assert response.status_code == 201
    assert response.data["subject"] == post_payload["subject"]
    assert response.data["content"] == post_payload["content"]
    assert response.data["reply_to"] == post_on_private_page.pk
    assert response.data["page"] == user_page.pk


@pytest.mark.django_db
def test_create_post_on_blocked_page(client, user, blocked_user_page):
    payload = dict(
        page=blocked_user_page.pk,
        subject="Blocked",
        content="Hello from blocked",
    )
    client.login(username="user", password="userpass")
    response = client.post("/api/posts/", payload)

    assert response.status_code == 400
    assert (
        response.data["detail"][0]
        == "Invalid page (perhaps page is blocked or it's not your page)."
    )


@pytest.mark.django_db
def test_wrong_page_provided(
    client, user_page, user_additional, post, incorrect_post_payload
):
    """Test creating post with wrong page provided"""
    client.login(username="user2", password="userpass")

    response = client.post("/api/posts/", incorrect_post_payload)

    assert "detail" in response.data
    assert (
        response.data["detail"][0]
        == "Invalid page (perhaps page is blocked or it's not your page)."
    )


@pytest.mark.django_db
def test_retrieve_post(client, admin, user_page, post):
    """Tset retrieve single post"""
    client.login(username="admin", password="adminpass")
    response = client.get(f"/api/posts/{post.pk}/")

    assert response.status_code == 200
    assert response.data["id"] == post.pk


@pytest.mark.django_db
@patch("core.views.produce.delay")
def test_delete_post(produce_delay, client, user, user_page, post):
    """Test delete post"""
    client.login(username="user", password="userpass")
    response = client.delete(f"/api/posts/{post.pk}/")

    assert response.status_code == 204
    assert len(user_page.posts.all()) == 0


@pytest.mark.django_db
def test_update_post(client, user, user_page, post):
    """Test update post content"""
    payload = dict(page=user_page.pk, content="New content")
    client.login(username="user", password="userpass")
    response = client.patch(f"/api/posts/{post.pk}/", payload)

    assert response.status_code == 200
    assert response.data["content"] == payload["content"]


@pytest.mark.django_db
def test_like_unlike_post(client, user_page, post, user_additional):
    """Test like post and remove your like from this post"""
    client.login(username="user2", password="userpass")
    response = client.get(f"/api/posts/{post.pk}/like/")

    assert response.status_code == 200
    assert response.data["response"] == "Post was added to your liked posts"
    assert post.likes.all()[0].pk == user_additional.pk

    response = client.get(f"/api/posts/{post.pk}/like/?if_like=unlike")

    assert response.status_code == 200
    assert response.data["response"] == "Post was removed from your liked posts"
    assert len(post.likes.all()) == 0


@pytest.mark.django_db
def test_get_liked_posts(client, user, post, post_on_admin_page):
    """Test get all the post current user ever liked"""
    client.login(username="user", password="userpass")
    client.get(f"/api/posts/{post.pk}/like/")
    client.get(f"/api/posts/{post_on_admin_page.pk}/like/")
    response = client.get("/api/posts/liked/")

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["id"] == post.pk
    assert response.data[1]["id"] == post_on_admin_page.pk
