from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from social_media.views import UserViewSet, PostViewSet, CommentViewSet

app_name = "social_media"

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("posts", PostViewSet, basename="posts")

posts_router = routers.NestedSimpleRouter(router, "posts", lookup="post")
posts_router.register("comments", CommentViewSet, basename="post-comments")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(posts_router.urls)),
]
