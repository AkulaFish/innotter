from django.urls import path
from users.views import *

app_name = 'users'
urlpatterns = [
    path('users/', UserListViewSet.as_view(), name="get_users"),
    path('users/<int:pk>', RetrieveUpdateUserViewSet.as_view(), name="get_or_update_single_user"),
    path('userdelete/<int:pk>', DeleteUSerViewSet.as_view(), name="delete_user"),
    path('register/', RegisterUserViewSet.as_view(), name='users_register'),
]
