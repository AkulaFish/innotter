from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
)

from users.serializers import UserSerializer
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
    get_posts,
)
from innotter.permissions import (
    PostIsOwnerAdminModerOrReadOnly,
    IsAdminOrModer,
    IsOwner,
)


class PageViewSet(
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
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
        methods=["put", "get"],
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

    @action(
        methods=["get", "put"],
        detail=True,
        url_path="like",
        url_name="like_or_unlike_post",
        permission_classes=(IsAuthenticated,),
    )
    def like_unlike_post(self, *args, **kwargs):
        cur_user = self.request.user
        post = self.get_object()
        self.check_permissions(self.request)
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
