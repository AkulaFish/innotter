from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Determines whether user is Admin or Read Only."""

    def has_permission(self, request, view):
        return request.user.is_admin or request.method in permissions.SAFE_METHODS


class IsAdminOrModerOrReadOnly(permissions.BasePermission):
    """
    Determines whether the user is Admin or Moderator
    Otherwise do not allow user to change data, but only look through it
    """

    def has_permission(self, request, view):
        return (
            request.user and (request.user.is_admin or request.user.is_moderator)
        ) or request.method in permissions.SAFE_METHODS


class IsAdminOrModer(permissions.BasePermission):
    """Determines whether user is Admin or Moderator."""

    def has_permission(self, request, view):
        return (
            True
            if request.user and (request.user.is_admin or request.user.is_moderator)
            else False
        )


class IsOwnerAdminModerOrReadOnly(permissions.BasePermission):
    """
    To change profile info user must be
    owner of it, Admin or moderator.
    """

    def has_object_permission(self, request, view, obj):
        return (
            True
            if (
                request.user.is_admin
                or request.user.is_moderator
                or obj.owner == request.user
                or request.method in permissions.SAFE_METHODS
            )
            else False
        )


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
        return (
            True
            if (
                request.user.is_admin
                or request.user.is_moderator
                or obj.page.owner == request.user
                or request.method in permissions.SAFE_METHODS
                and not obj.page.is_blocked
            )
            else False
        )


class IsNotAuthenticated(permissions.BasePermission):
    """Returns True if user is not authenticated to proceed registration."""

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsOwner(permissions.BasePermission):
    """Checks if user is the owner of the object"""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsAdmin(permissions.BasePermission):
    """Checks if user is admin"""

    def has_permission(self, request, view):
        return request.user.is_admin
