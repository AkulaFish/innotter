from typing import List

from rest_framework.status import HTTP_409_CONFLICT, HTTP_200_OK
from rest_framework.response import Response
from django.db.models import QuerySet

from core.models import Page, Post, Tag
from users.models import User


def accept_request(page: Page, target_user: User) -> None:
    """Accept single user request to follow other user's page"""
    page.follow_requests.remove(target_user)
    page.followers.add(target_user)


def accept_all_requests(page: Page) -> None:
    """Accept all users' requests to follow a page"""
    for user in page.follow_requests.all():
        accept_request(page, user)


def decline_all_requests(page: Page) -> None:
    """Decline all users' requests to follow a page"""
    for user in page.follow_requests.all():
        page.follow_requests.remove(user)


def get_posts(cur_user: User) -> List[Post]:
    """
    Get post list not including posts on blocked pages
    and post on private pages current user isn't subscribed on.
    """
    posts = []
    for post in Post.objects.all():
        if post.page.is_blocked or (
            post.page.is_private
            and cur_user not in post.page.followers.all()
            and not cur_user.is_staff
        ):
            posts.append(post)
    return posts


def get_newsfeed(cur_user: User) -> List[QuerySet]:
    """Get posts from pages current user subscribed on for their newsfeed"""
    queryset = []
    posts_in_pages = [
        page.posts.all() for page in cur_user.follows.all() if not page.is_blocked
    ]
    for posts in posts_in_pages:
        queryset.extend(posts)
    return queryset


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
        return Response(
            {"response": "You're successfully unsubscribed."},
            status=HTTP_200_OK,
        )


def decline_requests(user: User, page: Page) -> Response:
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


def accept_requests(user: User, page: Page) -> Response:
    """
    Service that accepts certain request if follower id is provided.
    Otherwise, accepts all requests for certain page
    """
    if user in page.followers.all():
        return Response(
            {"response": "User already follows you"},
            status=HTTP_409_CONFLICT,
        )

    if user in page.follow_requests.all():
        accept_request(page, user)
        return Response(
            {"response": "Request has been accepted"},
            status=HTTP_200_OK,
        )
    else:
        accept_all_requests(page)
        return Response(
            {"response": "All requests have been accepted"},
            status=HTTP_200_OK,
        )


def get_tag_set_for_page(tags: List[dict]) -> List[Tag]:
    """
    Service that returns list of tags to set for an instance of a page
    if you want to create or update it.
    """
    tag_objs = []
    for tag_data in tags:
        if Tag.objects.filter(**tag_data).exists():
            tag = Tag.objects.get(**tag_data)
        else:
            tag = Tag.objects.create(**tag_data)
        tag_objs.append(tag)
    return tag_objs
