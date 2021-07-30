
from rest_framework import permissions


class IsYouOrIsAdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow profile owner of an object to edit it.
    Assumes the model instance has an `id` attribute.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id or request.user.is_staff
