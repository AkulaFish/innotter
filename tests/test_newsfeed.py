import pytest


@pytest.mark.django_db
def test_get_newsfeed(client, user_page, post, post_on_private_page, user2):
    """Test getting newsfeed content where are posts of pages that current user follows"""
    client.login(username="user2", password="userpass")
    client.put("/api/pages/2/follow-unfollow/")
    response = client.get("/api/newsfeed/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == 1
