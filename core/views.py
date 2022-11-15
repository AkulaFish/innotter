from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
)

from users.serializers import UserSerializer
from core.models import Page, Post, Tag
from users.models import User
from core.serializers import (
    PageSerializer,
    PostSerializer,
    TagSerializer,
    BlockPageSerializer,
)
from core.services import (
    get_posts,
    get_newsfeed,
    follow_or_unfollow_page,
    decline_requests,
    accept_requests,
)
from innotter.permissions import (
    IsOwner,
    IsOwnerAdminModerOrReadOnly,
    PostIsOwnerAdminModerOrReadOnly,
    IsAdminOrModer,
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

    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsOwnerAdminModerOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("owner", "tags", "uuid")

    # REQUEST ACTIONS
    @action(
        permission_classes=(IsOwner, IsAuthenticated),
        serializer_class=UserSerializer,
        url_path="requests",
        url_name="requests",
        methods=["get"],
        detail=True,
    )
    def get_requests(self, *args, **kwargs):
        """Returns the list of follow requests to user"""
        if self.request.method == "GET":
            follow_requests = self.get_object().follow_requests.all()
            serializer = self.get_serializer(follow_requests, many=True)
            return Response(serializer.data)

    @action(
        permission_classes=(IsAuthenticated,),
        methods=["get"],
        detail=True,
    )
    def accept_requests_action(self, *args, **kwargs):
        """Service that provides functionality for accepting follow requests"""
        page = get_object_or_404(Page.objects.all(), pk=int(kwargs["pk"]))
        user = get_object_or_404(User.objects.all(), pk=int(kwargs["target_user_id"]))
        return accept_requests(user, page)

    @action(
        permission_classes=(IsAuthenticated,),
        methods=["get"],
        detail=True,
    )
    def decline_requests_action(self, *args, **kwargs):
        """This action provides functionality for declining follow requests"""
        page = get_object_or_404(Page.objects.all(), pk=int(kwargs["pk"]))
        user = get_object_or_404(User.objects.all(), pk=int(kwargs["target_user_id"]))
        return decline_requests(user, page)

    @action(
        permission_classes=(IsAuthenticated,),
        methods=["get"],
        url_name="follow_unfollow_page",
        url_path="follow-unfollow",
        detail=True,
    )
    def follow_page_action(self, *args, **kwargs):
        """This action provides api for following and unfollowing pages"""
        return follow_or_unfollow_page(self.request.user, self.get_object())


class BlockPageViewSet(
    UpdateModelMixin,
    GenericViewSet,
):
    """Service for blocking users for chosen period of time or permanently"""

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

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        PostIsOwnerAdminModerOrReadOnly,
    )

    def get_queryset(self):
        """Excludes posts on blocked pages and private pages"""
        cur_user = self.request.user
        posts = get_posts(cur_user)
        queryset = Post.objects.filter(pk__in=[post.pk for post in posts])
        return queryset

    @action(
        methods=["get"],
        detail=True,
        url_path="like",
        permission_classes=(IsAuthenticated,),
    )
    def like_unlike_post(self, *args, **kwargs):
        cur_user = self.request.user
        post = self.get_object()

        if cur_user not in post.likes.all():
            post.likes.add(cur_user)
            return Response({"response": "Post added to your liked posts"})
        else:
            post.likes.remove(cur_user)
            return Response({"response": "Post removed from your liked posts"})


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
