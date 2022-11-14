from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Determines whether user is Admin or Read Only."""

    def has_permission(self, request, view):
        if request.user.is_admin or request.method in permissions.SAFE_METHODS:
            return True
        return False


class IsAdminOrModerOrReadOnly(permissions.BasePermission):
    """
    Determines whether the user is Admin or Moderator
    Otherwise do not allow user to change data, but only look through it
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            True
            if request.user and (request.user.is_admin or request.user.is_moderator)
            else False
        )


class IsAdminOrModer(permissions.BasePermission):
    """Determines whether user is Admin or Moderator."""

    def has_permission(self, request, view):
        if request.user and (request.user.is_admin or request.user.is_moderator):
            return True
        return False


class IsOwnerAdminModerOrReadOnly(permissions.BasePermission):
    """
    To change profile info user must be
    owner of it, Admin or moderator.
    """

    def has_object_permission(self, request, view, obj):
        if (
            request.user.is_admin
            or request.user.is_moderator
            or obj.owner == request.user
            or request.method in permissions.SAFE_METHODS
        ):
            return True
        return False


class PostIsOwnerAdminModerOrReadOnly(permissions.BasePermission):
    """
    Post model specified permission.
    Post model requires different syntax to determine the owner of the object
    obj.page.owner instead of obj.owner because post refer
    to page and then page to owner
    Therefore this permission is identical
    to IsOwnerAdminModerOrReadOnly, just specified for
    post model.
    """

    def has_object_permission(self, request, view, obj):
        if (
            request.user.is_admin
            or request.user.is_moderator
            or obj.page.owner == request.user
            or request.method in permissions.SAFE_METHODS
        ):
            return True
        return False


class IsNotAuthenticated(permissions.BasePermission):
    """Returns True if user is not authenticated to proceed registration."""

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsOwner(permissions.BasePermission):
    """Checks if user is the owner of the object"""

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False
