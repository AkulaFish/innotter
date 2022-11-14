from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)

from innotter.permissions import (
    IsAdminOrModerOrReadOnly,
    IsNotAuthenticated,
    IsAdminOrModer,
)
from users.serializers import UserSerializer, RegisterUserSerializer
from users.models import User


class UserListViewSet(ListModelMixin, GenericViewSet):
    """Gets list of all users."""

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        If user provides username param, returns user
                with following username.
        """

        queryset = User.objects.all()
        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.get(username=username)
        return queryset


class RegisterUserViewSet(CreateModelMixin, GenericViewSet):
    """Registrate a new user."""

    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = (IsNotAuthenticated,)


class RetrieveUpdateDestroyUserViewSet(
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    """Updates, deletes and retrieves user info."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrModerOrReadOnly,)

    def delete(self, request, *args, **kwargs):
        """Override delete to log the successful removal of a user."""
        super(RetrieveUpdateDestroyUserViewSet, self).delete(
            self, request, *args, **kwargs
        )
        return Response({"result": "User successfully deleted."})

    @action(
        methods=["get"],
        permission_classes=(IsAuthenticated, IsAdminOrModer),
        detail=True,
        url_path="block",
        url_name="block_or_unblock_user",
    )
    def block_user(self, *args, **kwargs):
        """
        Service that provides possibility for
        admins and moderators to block users
        """
        user = self.get_object()
        if not user.is_blocked:
            user.is_blocked = True
            user.save()
            return Response({"response": "User successfully blocked"})
        else:
            user.is_blocked = False
            user.save()
            return Response({"response": "User unblocked"})
