from rest_framework.routers import SimpleRouter
from django.urls import path, include
from core.views import (
    PageViewSet,
    PostViewSet,
    TagListViewSet,
    NewsFeedViewSet,
    LikesListViewSet,
    BlockPageViewSet,
    GetMyPagesViewSet,
)

router = SimpleRouter()
router.register(r"pages", viewset=PageViewSet, basename="Page")
router.register(r"posts", viewset=PostViewSet, basename="Posts")
router.register(r"tags", viewset=TagListViewSet, basename="Tags")
router.register("liked", viewset=LikesListViewSet, basename="Posts")
router.register(r"newsfeed", viewset=NewsFeedViewSet, basename="Posts")
router.register("block-page", viewset=BlockPageViewSet, basename="BlockPages")
router.register("get_my_pages", viewset=GetMyPagesViewSet, basename="get_my_pages")

app_name = "core"
urlpatterns = [
    path("", include(router.urls)),
    # FOLLOW REQUESTS ACTIONS URLS
    path(
        "pages/<int:pk>/requests/accept/<int:target_user_id>",
        PageViewSet.as_view({"put": "accept_requests_action", "get": "retrieve"}),
        name="accept_request",
    ),
    path(
        "pages/<int:pk>/requests/accept/",
        PageViewSet.as_view({"put": "accept_requests_action", "get": "retrieve"}),
        kwargs={"target_user_id": None},
        name="accept_all_requests",
    ),
    path(
        "pages/<int:pk>/requests/decline/<int:target_user_id>",
        PageViewSet.as_view({"put": "decline_requests_action", "get": "retrieve"}),
        name="decline_request",
    ),
    path(
        "pages/<int:pk>/requests/decline/",
        PageViewSet.as_view({"put": "decline_requests_action", "get": "retrieve"}),
        kwargs={"target_user_id": None},
        name="decline_all_requests",
    ),
]
