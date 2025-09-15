from typing import Type

from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    BasePermission,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from social_media.models import Post, Comment, Like, Follow
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import (
    UserRegistrationSerializer,
    ProfileSerializer,
    UserSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostSerializer,
    CommentSerializer,
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

    @action(
        methods=["POST"], detail=True, permission_classes=[IsAuthenticated]
    )
    def follow(self, request: Request, pk: int | None = None) -> Response:
        """Follow a user."""
        user_to_follow = self.get_object()
        if user_to_follow == request.user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        _, created = Follow.objects.get_or_create(
            follower=request.user, following=user_to_follow
        )

        if not created:
            return Response(
                {"detail": "You already following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Successfully followed the user."},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["POST"], detail=True, permission_classes=[IsAuthenticated]
    )
    def unfollow(self, request: Request, pk: int | None = None) -> Response:
        """Unfollow a user."""
        user_to_unfollow = self.get_object()

        deleted_count, _ = Follow.objects.filter(
            follower=request.user, following=user_to_unfollow
        ).delete()

        if deleted_count == 0:
            return Response(
                {"detail": "You don't following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Successfully unfollowed the user."},
        )


class PostViewSet(viewsets.ModelViewSet):
    def get_queryset(self) -> QuerySet:
        queryset = Post.objects.annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count("comments", distinct=True),
        ).select_related("user__profile")

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("comments__user__profile")

        return queryset

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostSerializer

    def get_permissions(self) -> list[BasePermission]:
        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)

    @action(
        methods=["post"], detail=True, permission_classes=[IsAuthenticated]
    )
    def like(self, request: Request, pk: int | None = None) -> Response:
        """Add a like to the post"""
        post = self.get_object()
        user = request.user
        _, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            return Response(
                {"detail": "You already liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Post liked successfully."}, status=status.HTTP_200_OK
        )

    @action(
        methods=["post"], detail=True, permission_classes=[IsAuthenticated]
    )
    def unlike(self, request: Request, pk: int | None = None) -> Response:
        """Remove a like from the post"""
        post = self.get_object()
        user = request.user
        deleted_count, _ = Like.objects.filter(user=user, post=post).delete()

        if deleted_count == 0:
            return Response(
                {"detail": "You have not liked this post yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Like removed successfully."},
            status=status.HTTP_200_OK,
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self) -> QuerySet:
        post_pk = self.kwargs.get("post_pk")
        post = get_object_or_404(Post, pk=post_pk)
        return Comment.objects.filter(post=post).select_related(
            "user__profile"
        )

    def get_permissions(self) -> list[BasePermission]:
        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer: Serializer) -> None:
        post_pk = self.kwargs.get("post_pk")
        post = get_object_or_404(Post, pk=post_pk)
        serializer.save(user=self.request.user, post=post)
