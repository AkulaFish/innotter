from django.urls import path, include
from rest_framework.routers import SimpleRouter

from users.views import UserListViewSet, RegisterUserViewSet, RetrieveUpdateDestroyUserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = SimpleRouter()
router.register(r'users', viewset=UserListViewSet, basename='Page')
router.register(r'users', viewset=RetrieveUpdateDestroyUserViewSet, basename='Posts')
router.register(r'register', viewset=RegisterUserViewSet, basename='Posts')

app_name = 'users'
urlpatterns = [
    # user crud routs
    path('', include(router.urls)),
    # simplejwt token routs
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')

]
