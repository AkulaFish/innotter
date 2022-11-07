from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (ListModelMixin, CreateModelMixin,
                                   UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin)

from users.models import User
from innotter.permissions import IsAdminOrModerOrReadOnly, IsNotAuthenticated
from users.serializers import UserSerializer, RegisterUserSerializer


class UserListViewSet(ListModelMixin,
                      GenericViewSet):
    """ Gets list of all users. """
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        If user provides username param, returns user
                with following username.
        """

        queryset = User.objects.all()
        username = self.request.query_params.get('username')
        if username:
            queryset = queryset.get(username=username)
        return queryset


class RegisterUserViewSet(CreateModelMixin,
                          GenericViewSet):
    """ Registrate a new user. """
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = (IsNotAuthenticated,)


class RetrieveUpdateDestroyUserViewSet(RetrieveModelMixin,
                                       UpdateModelMixin,
                                       DestroyModelMixin,
                                       GenericViewSet):
    """ Updates, deletes and retrieves user info. """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrModerOrReadOnly,)

    def delete(self, request, *args, **kwargs):
        """ Override delete to log the successful deletion of a user. """
        super(RetrieveUpdateDestroyUserViewSet, self).delete(self, request, *args, **kwargs)
        return Response(
            {"result": "User successfully deleted."}
        )
