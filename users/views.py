from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, DestroyModelMixin, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer, RegisterUserSerializer


class UserListViewSet(ListModelMixin, GenericAPIView):
    """ Gets list of all users """
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        If user provides username param, returns user
                with following username
        """

        queryset = User.objects.all()
        username = self.request.query_params.get('username')
        if username:
            queryset = queryset.get(username=username)
        return queryset


class DeleteUserViewSet(DestroyModelMixin, GenericAPIView):
    """ Deletes a user """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def delete(self, request, *args, **kwargs):
        super(DeleteUserViewSet, self).delete(self, request, *args, **kwargs)
        return Response(
            {"result": "user successfully deleted"}
        )


class RegisterUserViewSet(GenericAPIView, CreateModelMixin):
    """ Registrate a new user """
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)


class RetrieveUpdateUserViewSet(GenericAPIView, UpdateModelMixin, RetrieveModelMixin):
    """ Updates user info """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

