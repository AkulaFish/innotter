import os

import requests

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
)

from core.email_services import send_new_post_notification_email
from users.serializers import UserSerializer
from core.producer import produce
from core.models import Page, Tag
from users.models import User


from core.serializers import (
    BlockPageSerializer,
    PageSerializer,
    PostSerializer,
    TagSerializer,
)
from core.services import (
    follow_or_unfollow_page,
    decline_requests,
    accept_requests,
    get_newsfeed,
    like_unlike,
    get_posts, get_access_token,
)
from innotter.permissions import (
    PostIsOwnerAdminModerOrReadOnly,
    IsAdminOrModer,
    IsOwner,
)


class PageViewSet(
    RetrieveModelMixin,
    DestroyModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    """Page view set."""

    queryset = Page.objects.prefetch_related("tags").all()
    serializer_class = PageSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("owner", "tags", "uuid")
    permission_classes = (
        IsAuthenticated,
        (IsAdminOrModer | IsOwner),
    )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        produce.delay(
            method="POST",
            body=dict(page_id=response.data.get("id"), action="page_created"),
        )
        return response

    def destroy(self, request, *args, **kwargs):
        page = self.get_object()
        super(PageViewSet, self).destroy(request, *args, **kwargs)
        produce.delay(
            method="DELETE", body=dict(page_id=page.pk, action="page_deleted")
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        permission_classes=(IsAuthenticated, IsOwner),
        url_path="requests",
        url_name="requests",
        serializer_class=UserSerializer,
        methods=["get"],
        detail=True,
    )
    def get_requests(self, *args, **kwargs):
        """Returns the list of follow requests"""
        self.check_permissions(self.request)
        self.check_object_permissions(self.request, self.get_object())
        follow_requests = self.get_object().follow_requests.all()
        serializer = self.get_serializer(follow_requests, many=True)
        return Response(serializer.data)

    @action(
        methods=["put"],
        detail=True,
        permission_classes=(IsAuthenticated, IsOwner),
    )
    def decline_requests_action(self, *args, **kwargs):
        """This action provides functionality for declining follow requests"""
        page = get_object_or_404(Page.objects.all(), pk=kwargs.get("pk"))
        self.check_permissions(self.request)
        self.check_object_permissions(self.request, page)
        if pk := kwargs.get("target_user_id"):
            user = User.objects.get(pk=int(pk))
            return decline_requests(page, user)
        return decline_requests(page)

    @action(
        methods=["put"],
        detail=True,
        permission_classes=(IsAuthenticated, IsOwner),
    )
    def accept_requests_action(self, *args, **kwargs):
        """Service that provides functionality for accepting follow requests"""
        page = get_object_or_404(Page.objects.all(), pk=kwargs.get("pk"))
        self.check_permissions(self.request)
        self.check_object_permissions(self.request, page)
        if pk := kwargs.get("target_user_id"):
            user = User.objects.get(pk=int(pk))
            return accept_requests(page, user)
        return accept_requests(page)

    @action(
        methods=["put"],
        url_name="follow_unfollow_page",
        url_path="follow-unfollow",
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def follow_or_unfollow_page_action(self, *args, **kwargs):
        """This action provides api for following and unfollowing pages"""
        self.check_permissions(self.request)
        return follow_or_unfollow_page(self.request.user, self.get_object())


class BlockPageViewSet(
    UpdateModelMixin,
    GenericViewSet,
):
    """Service for blocking pages for chosen period of time or permanently"""

    queryset = Page.objects.all()
    serializer_class = BlockPageSerializer
    permission_classes = (IsAuthenticated, IsAdminOrModer)


class PostViewSet(
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """Post view set."""

    serializer_class = PostSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        PostIsOwnerAdminModerOrReadOnly,
    )

    def get_queryset(self):
        """Excludes posts on blocked pages and private pages"""
        cur_user = self.request.user
        return get_posts(cur_user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        produce.delay(
            method="POST",
            body=dict(page_id=response.data.get("page"), action="post_created"),
        )
        send_new_post_notification_email.delay(response.data.get("id"))
        return response

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        super(PostViewSet, self).destroy(request, *args, **kwargs)
        produce.delay(
            method="DELETE", body=dict(page_id=post.page.pk, action="post_deleted")
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["get"],
        detail=True,
        url_path="like",
        url_name="like_or_unlike_post",
        permission_classes=(IsAuthenticated,),
    )
    def like_unlike_post(self, *args, **kwargs):
        self.check_permissions(self.request)
        cur_user = self.request.user
        post = self.get_object()
        return like_unlike(cur_user, post)


class NewsFeedViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """Displays newsfeed with post of pages you currently follow."""

    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Get queryset for all posts related to pages user is following.
        posts_in_pages has the following structure:
        [[posts_of_page_1],[posts_of_page_2]...[posts_of_page_n]]
        So we want to have a flat list for our queryset and that's
        why we use for cycle and extend our queryset with lists of pages
        """
        return get_newsfeed(self.request.user)


class TagListViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet,
):
    """
    Tag list view set. Allows user to get the list of Tags
    and create a new one.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class LikesListViewSet(ListModelMixin, GenericViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.liked_posts.all()


class GetMyPagesViewSet(GenericViewSet, ListModelMixin):
    """Gets user pages"""

    serializer_class = PageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.pages.all()

    @action(
        methods=["get"],
        detail=False,
        url_name="get_stats",
        url_path="stats"
    )
    def get_my_pages_stats(self, *args, **kwargs):
        """Get statistics of your pages"""
        my_pages_ids = {
            "pages_ids": [page.pk for page in self.request.user.pages.all()],
        }
        headers = {"token": get_access_token(my_pages_ids)}
        response = requests.get(
            url=os.getenv("MICROSERVICE_URL"),
            headers=headers
        )
        return Response(response.json())
