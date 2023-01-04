from typing import List

from rest_framework.status import HTTP_409_CONFLICT, HTTP_200_OK
from rest_framework.response import Response
import jwt

from innotter import settings
from core.models import Page, Post, Tag
from core.producer import produce
from users.models import User


def accept_request(page: Page, target_user: User) -> None:
    """Accept single user request to follow other user's page"""
    page.follow_requests.remove(target_user)
    page.followers.add(target_user)
    produce(method="PUT", body=dict(page_id=page.pk, action="follow"))


def accept_all_requests(page: Page) -> None:
    """Accept all users' requests to follow a page"""
    [accept_request(page, user) for user in page.follow_requests.all()]


def decline_all_requests(page: Page) -> None:
    """Decline all users' requests to follow a page"""
    [page.follow_requests.remove(user) for user in page.follow_requests.all()]


def get_posts(cur_user: User) -> List[Post]:
    """
    Get post list not including posts on blocked pages
    and posts on private pages current user isn't subscribed on.
    """
    if cur_user.is_staff:
        return Post.objects.all()
    else:
        pages = (
            Page.objects.select_related("posts").filter(is_private=False)
            ^ cur_user.follows.all()
        )
        return Post.objects.select_related("page").filter(page__in=pages)


def like_unlike(cur_user: User, post: Post, if_like: Post.LikeState) -> Response:
    """Like or remove your like from the post if you already liked it"""
    if if_like == Post.LikeState.LIKE:
        post.likes.add(cur_user)
        produce(method="GET", body=dict(page_id=post.page.pk, action="like"))
        return Response(
            data={"response": "Post was added to your liked posts"}, status=HTTP_200_OK
        )
    elif if_like == Post.LikeState.UNLIKE:
        post.likes.remove(cur_user)
        produce(method="GET", body=dict(page_id=post.page.pk, action="unlike"))
        return Response(
            data={"response": "Post was removed from your liked posts"},
            status=HTTP_200_OK,
        )


def follow_or_unfollow_page(cur_user: User, page: Page) -> Response:
    """
    Service that adds/removes user to/from page followers or
    sends follow request if page is private.
    """
    if page in cur_user.pages.all():
        return Response(
            {"response": "You're trying to follow your own page"},
            status=HTTP_409_CONFLICT,
        )

    if cur_user not in page.followers.all():
        if not page.is_private:
            page.followers.add(cur_user)
            produce(method="PUT", body=dict(page_id=page.pk, action="follow"))
            return Response(
                {"response": "Now you follow this page."},
                status=HTTP_200_OK,
            )
        else:
            page.follow_requests.add(cur_user)
            return Response(
                {"response": "Owner of the page will review your request."},
                status=HTTP_200_OK,
            )
    else:
        page.followers.remove(cur_user)
        produce(method="PUT", body=dict(page_id=page.pk, action="unfollow"))
        return Response(
            {"response": "You're successfully unsubscribed."},
            status=HTTP_200_OK,
        )


def decline_requests(page: Page, user: User = None) -> Response:
    """
    Service that accepts declines request if follower id is provided.
    Otherwise, declines all requests for certain page.
    """
    if user in page.followers.all():
        return Response(
            {"response": "User already follows you"}, status=HTTP_409_CONFLICT
        )
    if user in page.follow_requests.all():
        page.follow_requests.remove(user)
        return Response({"response": "Request has been declined"}, status=HTTP_200_OK)
    else:
        decline_all_requests(page)
        return Response(
            {"response": "All requests have been declined"}, status=HTTP_200_OK
        )


def accept_requests(page: Page, user: User = None) -> Response:
    """
    Service that accepts certain request if follower id is provided.
    Otherwise, accepts all requests for certain page
    """
    if not user:
        accept_all_requests(page)
        return Response(
            {"response": "All requests have been accepted"},
            status=HTTP_200_OK,
        )
    elif user in page.followers.all():
        return Response(
            {"response": "User already follows you."},
            status=HTTP_409_CONFLICT,
        )
    elif user in page.follow_requests.all():
        accept_request(page, user)
        return Response(
            {"response": "Request has been accepted"},
            status=HTTP_200_OK,
        )


def get_tag_set_for_page(tags: List[dict]) -> List[Tag]:
    """
    Service that returns list of tags to set for an instance of a page
    if you want to create or update it.
    """
    tag_objs = []
    for tag_data in tags:
        if Tag.objects.filter(name=tag_data["name"]).exists():
            tag = Tag.objects.get(name=tag_data["name"])
        else:
            tag = Tag.objects.create(**tag_data)
        tag_objs.append(tag)
    return tag_objs


def get_access_token(payload: dict) -> str:
    token = jwt.encode(payload, settings.SECRET_KEY, settings.SIMPLE_JWT["ALGORITHM"])
    return token
