from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, \
    CreateModelMixin, ListModelMixin, DestroyModelMixin

from core.models import Page, Post, Tag
from core.serializers import PageSerializer, PostSerializer, TagSerializer
from innotter.permissions import IsOwnerAdminModerOrReadOnly, PostIsOwnerAdminModerOrReadOnly
from users.models import User


class PageViewSet(CreateModelMixin,
                  UpdateModelMixin,
                  ListModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    """ Page view set """

    serializer_class = PageSerializer
    permission_classes = (IsOwnerAdminModerOrReadOnly,)

    def get_queryset(self):
        """
        If user provides username, uuid or tags  param, returns page
                of following user, with following uuid or tag
        """

        queryset = Page.objects.all()
        username = self.request.query_params.get('username')
        uuid = self.request.query_params.get('uuid')
        tags = self.request.query_params.get('tags')
        if username:
            queryset = queryset.get(owner=User.objects.all().get(username=username))
        elif uuid:
            queryset = queryset.get(uuid=uuid)
        elif tags:
            queryset = queryset.get(tags=tags)
        return queryset


class PostViewSet(CreateModelMixin,
                  UpdateModelMixin,
                  ListModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    """ Post view set """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (PostIsOwnerAdminModerOrReadOnly,)


class NewsFeedSet(ListModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet):
    """ Displays newsfeed with post of pages you currently follow """

    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        follows = self.request.user.follows.all()
        pages = []
        posts = []

        for follow in follows:
            pages.append(follow.pages.all())

        for page in pages:
            posts.append(page.posts.all())

        return posts


class TagListViewSet(ListModelMixin,
                     GenericViewSet):
    """ Tag list view set. Allows looking through the list of Tags """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
