from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.permissions import BasePermission


User = get_user_model()


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Handles both User model instances and objects with a 'user' attribute.
    """

    def has_object_permission(self, request: HttpRequest, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        # If the object is a User instance, check if it's the request user.
        if isinstance(obj, User):
            return obj == request.user

        # If the object has a 'user' attribute, check if that user is the request user.
        return getattr(obj, "user", None) == request.user
