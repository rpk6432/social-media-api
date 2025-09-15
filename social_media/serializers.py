from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile, Comment, Post, Follow

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("bio", "profile_picture")


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "profile")


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        min_length=8,
        max_length=25,
    )
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data: dict) -> User:
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "user", "post", "text", "created_at")
        read_only_fields = ("id", "user", "post", "created_at")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "content", "image", "created_at")
        read_only_fields = ("id", "created_at")


class PostListSerializer(PostSerializer):
    user = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + (
            "user",
            "likes_count",
            "comments_count",
        )


class PostDetailSerializer(PostListSerializer):
    comments = CommentSerializer(read_only=True, many=True)

    class Meta(PostListSerializer.Meta):
        fields = PostSerializer.Meta.fields + ("comments",)


class UserPublicInfoSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(
        source="profile.profile_picture", read_only=True
    )

    class Meta:
        model = User
        fields = ("id", "username", "profile_picture")


class FollowerSerializer(serializers.ModelSerializer):
    follower = UserPublicInfoSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ("follower", "created_at")


class FollowingSerializer(serializers.ModelSerializer):
    following = UserPublicInfoSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ("following", "created_at")
