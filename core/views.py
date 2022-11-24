from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import GenericViewSet

from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
)

from core.mixins import RequestsAndFollowersMixin, LikeUnlikePostMixin
from core.models import Page, Tag
from core.serializers import (
    BlockPageSerializer,
    PageSerializer,
    PostSerializer,
    TagSerializer,
)
from core.services import (
    get_newsfeed,
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
    RequestsAndFollowersMixin,
    GenericViewSet,
):
    """Page view set."""

    queryset = Page.objects.prefetch_related("tags").all()
    serializer_class = PageSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("owner", "tags", "uuid")
    permission_classes = (IsAuthenticated & (IsAdminOrModer | IsOwner),)


class BlockPageViewSet(
    UpdateModelMixin,
    GenericViewSet,
):
    """Service for blocking pages for chosen period of time or permanently"""

    queryset = Page.objects.all()
    serializer_class = BlockPageSerializer
    permission_classes = (IsAuthenticated & IsAdminOrModer,)


class PostViewSet(
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet,
    LikeUnlikePostMixin,
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
