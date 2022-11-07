from django.urls import path, include
from rest_framework.routers import SimpleRouter
from core.views import PageViewSet, PostViewSet, NewsFeedSet

router = SimpleRouter()
router.register(r'pages', viewset=PageViewSet, basename='Page')
router.register(r'posts', viewset=PostViewSet, basename='Posts')
router.register(r'newsfeed', viewset=NewsFeedSet, basename='Posts')

app_name = 'core'
urlpatterns = [
    path('', include(router.urls))
]
