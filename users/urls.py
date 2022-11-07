from django.urls import path, include
from users.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

app_name = 'users'
urlpatterns = [
    # user crud routs
    path('users/', UserListViewSet.as_view(), name="get_users"),
    path('users/<int:pk>', RetrieveUpdateDestroyUserViewSet.as_view(), name="get_update_or_delete_single_user"),
    path('register/', RegisterUserViewSet.as_view(), name='users_register'),

    # simplejwt token routs
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')

]
