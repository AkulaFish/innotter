import pytest


@pytest.mark.django_db
def test_create_post(client, user_page, user, post_on_private_page):
    """Test creating post on user page that replies to another post"""
    payload = dict(
        page=2,
        subject="Some cool subject",
        reply_to=2,
        content="This is my first post",
    )
    client.login(username="user", password="userpass")
    response = client.post("/api/posts/", payload)

    assert response.status_code == 201
    assert response.data["content"] == payload["content"]
    assert response.data["id"] == 1


@pytest.mark.django_db
def test_wrong_page_provided(client, user_page, user2, post):
    """Test creating post with wrong page provided"""
    payload = dict(
        page=2,
        subject="Some cool subject",
        content="This is my first post",
    )
    client.login(username="user2", password="userpass")

    response = client.post("/api/posts/", payload)

    assert "detail" in response.data


@pytest.mark.django_db
def test_retrieve_post(client, admin, user_page, post):
    """Tset retrieve single post"""
    client.login(username="admin", password="adminpass")
    response = client.get("/api/posts/1/")

    assert response.status_code == 200
    assert response.data["id"] == 1


@pytest.mark.django_db
def test_delete_post(client, user, user_page, post):
    """Test delete post"""
    client.login(username="user", password="userpass")
    response = client.delete("/api/posts/1/")

    assert response.status_code == 204
    assert len(user_page.posts.all()) == 0


@pytest.mark.django_db
def test_update_post(client, user, user_page, post):
    """Test update post content"""
    payload = dict(
        page=2,
        content="New content"
    )
    client.login(username="user", password="userpass")
    response = client.patch("/api/posts/1/", payload)

    assert response.status_code == 200
    assert response.data["content"] == payload["content"]


@pytest.mark.django_db
def test_like_unlike_post(client, user_page, post, user2):
    """Test like post and remove your like from this post"""
    client.login(username="user2", password="userpass")
    response = client.put("/api/posts/1/like/")

    assert response.status_code == 200
    assert response.data["response"] == "Post added to your liked posts"

    response = client.put("/api/posts/1/like/")

    assert response.status_code == 200
    assert response.data["response"] == "Post removed from your liked posts"


@pytest.mark.django_db
def test_get_liked_posts(client, user, post, post_on_private_page):
    """Test get all the post current user ever liked"""
    client.login(username="user", password="userpass")
    client.put("/api/posts/1/like/")
    client.put("/api/posts/2/like/")
    response = client.get("/api/liked/")

    assert response.status_code == 200
    assert len(response.data) == 2
