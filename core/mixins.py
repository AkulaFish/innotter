from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from core.services import (
    decline_requests,
    accept_requests,
    follow_or_unfollow_page,
    like_unlike,
)
from users.serializers import UserSerializer
from innotter.permissions import IsOwner
from core.models import Page
from users.models import User


class RequestsAndFollowersMixin:
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
        follow_requests = self.get_object().follow_requests.all()
        serializer = self.get_serializer(follow_requests, many=True)
        self.check_permissions(self.request)
        self.check_object_permissions(self.request, self.get_object())
        return Response(serializer.data)

    @action(
        methods=["put"],
        detail=True,
        permission_classes=[
            IsAuthenticated & IsOwner,
        ],
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


class LikeUnlikePostMixin:
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
        return like_unlike(cur_user, post)
