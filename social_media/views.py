from typing import Type

from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    BasePermission,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import (
    UserRegistrationSerializer,
    ProfileSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("profile")

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "create":
            return UserRegistrationSerializer
        if self.action == "me" and self.request.method in ["PUT", "PATCH"]:
            return ProfileSerializer
        return UserSerializer

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "create":
            self.permission_classes = [AllowAny]
        elif self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    @action(
        detail=False,
        methods=["get", "put", "patch"],
        permission_classes=[IsAuthenticated],
        url_path="me",
    )
    def me(self, request: Request, *args, **kwargs) -> Response:
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        profile = user.profile
        serializer = self.get_serializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user).data)
