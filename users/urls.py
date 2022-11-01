from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import *

app_name = 'users'
urlpatterns = [
    path('users/', UserListViewSet.as_view(), name="get_users"),
    path('register/', RegisterUserViewSet.as_view(), name='users_register')
]
