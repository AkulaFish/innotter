from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.api.views import *
from users.views import UserViewSet

router = DefaultRouter()
router.register('users', viewset=UserViewSet)

app_name = 'users'
urlpatterns = [
    path('', include(router.urls)),
    path('register', registration_view, name='register'),
    path('/login/', login_view, name='login')
]