import pytest

from rest_framework.test import APIClient

from core.models import Page, Tag, Post
from users.models import User


@pytest.fixture
def user():
    """Default user instance fixture"""
    user = User(
        id=1,
        email="user@user.com",
        role="user",
        title="user",
        username="user",
        first_name="Harry",
        last_name="Potter",
    )
    user.set_password("userpass")
    user.save()
    return user


@pytest.fixture
def user2():
    """Additional user instance fixture"""
    user = User(
        id=4,
        email="user2@user.com",
        role="user",
        title="user2",
        username="user2",
        first_name="Harry",
        last_name="Potter",
    )
    user.set_password("userpass")
    user.save()
    return user


@pytest.fixture
def moderator():
    """Moder user instance"""
    moder = User(
        id=2,
        email="moder@moder.com",
        role="moderator",
        title="moder",
        username="moder",
        first_name="Albus",
        last_name="Dumbledore",
    )
    moder.set_password("moderpass")
    moder.save()
    return moder


@pytest.fixture
def admin():
    """Admin user instance fixture"""
    admin = User(
        id=3,
        email="admin@admin.com",
        role="admin",
        title="admin",
        username="admin",
        first_name="Tom",
        last_name="Riddle",
    )
    admin.set_password("adminpass")
    admin.save()
    return admin


@pytest.fixture
def client():
    """Returns APIClient fixture"""
    return APIClient()


@pytest.fixture
def user_auth_token(client, user):
    """Get user auth token"""
    response = client.post("/api/token/", dict(username="user", password="userpass"))
    return {"Authorization": "JWT " + response.data["access"]}


@pytest.fixture
def user_page(user):
    """Default user page fixture"""
    page = Page(
        id=2,
        name="UserPage",
        description="This is the first page of this user",
        is_private=False,
        owner=user,
    )
    page.save()
    return page


@pytest.fixture
def private_user_page(user):
    """Private user page fixture"""
    page = Page(
        id=1,
        name="UserPrivatePage",
        description="This is the seccond page of this user",
        is_private=True,
        owner=user,
    )
    page.save()
    return page


@pytest.fixture
def admin_page(admin):
    """Admin page fixture"""
    page = Page(
        id=3,
        name="AdminPage",
        description="I'm the boss here!!!",
        is_private=False,
        owner=admin,
    )
    page.save()
    return page


@pytest.fixture
def tag():
    """Tag instance fixture"""
    tag = Tag(
        id=1,
        name="SomeTag"
    )
    tag.save()
    return tag


@pytest.fixture
def tag2():
    """Additional tag fixture"""
    tag = Tag(
        id=2,
        name="SomeOtherTag"
    )
    tag.save()
    return tag


@pytest.fixture
def post_on_private_page(user, private_user_page):
    """Post instance on private user page fixture"""
    post = Post(
        id=2,
        subject="Private post subject",
        page=private_user_page,
        content="This is my second post"
    )
    post.save()
    return post


@pytest.fixture
def post(user, user_page):
    """Default post instance fixture"""
    post = Post(
        id=1,
        subject="Post subject",
        page=user_page,
        content="This is my first post"
    )
    post.save()
    return post
