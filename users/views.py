from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer, RegisterUserSerializer


class UserListViewSet(generics.ListAPIView):
    """ Gets list of all users """
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        If user provides username param, returns users
                with following username
        """

        queryset = User.objects.all()
        username = self.request.query_params.get('username')
        if username is not None:
            queryset = queryset.filter(username=username)
        return queryset


# class SingleUserViewSet(generics.RetrieveAPIView):
#     """ Gets single user """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = (AllowAny,)


class DeleteUSerViewSet(generics.DestroyAPIView):
    """ Deletes a user """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def delete(self, request, *args, **kwargs):
        super(DeleteUSerViewSet, self).delete(self, request, *args, **kwargs)
        return Response(
            {"result": "user successfully deleted"}
        )


class RegisterUserViewSet(generics.CreateAPIView):
    """ Registrate a new user """
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)


class RetrieveUpdateUserViewSet(generics.RetrieveUpdateAPIView):
    """ Updates user info """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
