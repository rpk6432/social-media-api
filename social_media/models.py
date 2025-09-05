import os
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


def get_image_path(instance, filename: str, base_folder: str) -> str:
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    user_id = instance.user.id
    return os.path.join(
        "uploads", "users", str(user_id), base_folder, filename
    )


def get_profile_image_path(instance, filename: str) -> str:
    return get_image_path(instance, filename, "profile_images")


def get_post_image_path(instance, filename: str) -> str:
    return get_image_path(instance, filename, "post_images")


class User(AbstractUser):
    email = models.EmailField(
        "email address",
        unique=True,
        error_messages={"unique": "This email already exists."},
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to=get_profile_image_path, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    content = models.TextField()
    image = models.ImageField(
        upload_to=get_post_image_path, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_posts",
        blank=True,
        through="Like",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return (
            f"Post by {self.user.username} "
            f"at {self.created_at.strftime("%Y-%m-%d %H:%M")}"
        )


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="following",
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="followers",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.follower.username} follows {self.following.username}"


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.user.username} on post {self.post.id}"


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "post"]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Like by {self.user.username} on post {self.post.id}"
