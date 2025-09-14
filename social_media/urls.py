from django.urls import path, include
from rest_framework.routers import DefaultRouter

from social_media.views import UserViewSet, PostViewSet

app_name = "social_media"

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("posts", PostViewSet, basename="posts")

urlpatterns = [path("", include(router.urls))]
