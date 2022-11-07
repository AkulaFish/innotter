from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import (RetrieveModelMixin, UpdateModelMixin,
                                   CreateModelMixin, ListModelMixin, DestroyModelMixin)

from core.models import Page, Post, Tag
from core.serializers import PageSerializer, PostSerializer, TagSerializer
from innotter.permissions import IsOwnerAdminModerOrReadOnlyOrBlocked, PostIsOwnerAdminModerOrReadOnlyOrBlocked
from users.models import User


class PageViewSet(CreateModelMixin,
                  UpdateModelMixin,
                  ListModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    """
    Page view set.
    """

    serializer_class = PageSerializer
    permission_classes = (IsOwnerAdminModerOrReadOnlyOrBlocked,)

    def get_queryset(self):
        """
        If user provides username, uuid or tags  param, returns page
                of following user, with following uuid or tag.
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
    """
    Post view set.
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (PostIsOwnerAdminModerOrReadOnlyOrBlocked,)


class NewsFeedSet(ListModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet):
    """ Displays newsfeed with post of pages you currently follow. """

    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ Get queryset for all posts related to pages user is following """
        queryset = [page.posts.all() for page in self.request.user.follows.all()]
        return queryset


class TagListViewSet(ListModelMixin,
                     GenericViewSet):
    """ Tag list view set. Allows looking through the list of Tags. """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer

