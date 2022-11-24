import pytest


@pytest.mark.django_db
def test_create_post(client, user_page, user, post_on_private_page):
    """Test creating post on user page that replies to another post"""
    payload = dict(
        page=user_page.pk,
        subject="Some cool subject",
        reply_to=post_on_private_page.pk,
        content="This is my first post",
    )
    client.login(username="user", password="userpass")
    response = client.post("/api/posts/", payload)

    assert response.status_code == 201
    assert response.data["subject"] == payload["subject"]
    assert response.data["content"] == payload["content"]


@pytest.mark.django_db
def test_wrong_page_provided(client, user_page, user_additional, post):
    """Test creating post with wrong page provided"""
    payload = dict(
        page=user_page.pk,
        subject="Some cool subject",
        content="This is my first post",
    )
    client.login(username="user2", password="userpass")

    response = client.post("/api/posts/", payload)

    assert "detail" in response.data
    assert response.data["detail"][0] == "Invalid page"


@pytest.mark.django_db
def test_retrieve_post(client, admin, user_page, post):
    """Tset retrieve single post"""
    client.login(username="admin", password="adminpass")
    response = client.get(f"/api/posts/{post.pk}/")

    assert response.status_code == 200
    assert response.data["id"] == post.pk


@pytest.mark.django_db
def test_delete_post(client, user, user_page, post):
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
    response = client.put(f"/api/posts/{post.pk}/like/")

    assert response.status_code == 200
    assert response.data["response"] == "Post added to your liked posts"
    assert post.likes.all()[0].pk == user_additional.pk

    response = client.put(f"/api/posts/{post.pk}/like/")

    assert response.status_code == 200
    assert response.data["response"] == "Post removed from your liked posts"
    assert len(post.likes.all()) == 0


@pytest.mark.django_db
def test_get_liked_posts(client, user, post, post_on_private_page):
    """Test get all the post current user ever liked"""
    client.login(username="user", password="userpass")
    client.put(f"/api/posts/{post.pk}/like/")
    client.put(f"/api/posts/{post_on_private_page.pk}/like/")
    response = client.get("/api/liked/")

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["id"] == post.pk
    assert response.data[1]["id"] == post_on_private_page.pk
