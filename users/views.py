from rest_framework.permissions import AllowAny
from rest_framework import generics
from users.models import User
from users.serializers import UserSerializer, RegisterUserSerializer, RetrieveUpdateDestroyUserSerializer


class UserListViewSet(generics.ListAPIView):
    """ Gets list of all users """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny, ]


class RegisterUserViewSet(generics.CreateAPIView):
    """ Registrates a new user """
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)


class RetrieveUpdateDestroyUserViewSet(generics.RetrieveUpdateDestroyAPIView):
    """ Updates user info """
    queryset = User.objects.all()
    serializer_class = RetrieveUpdateDestroyUserSerializer

