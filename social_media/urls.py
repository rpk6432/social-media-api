from django.urls import path, include
from rest_framework.routers import DefaultRouter

from social_media.views import UserViewSet

app_name = "social_media"

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns = [path("", include(router.urls))]
