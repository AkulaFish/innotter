from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Determines whether user is Admin or Read Only."""

    def has_permission(self, request, view):
        if (
            request.user.is_admin and not request.user.is_blocked
        ) or request.method in permissions.SAFE_METHODS:
            return True
        return False


class IsAdminOrModerOrReadOnly(permissions.BasePermission):
    """
    Determines whether the user is Admin or Moderator
    Otherwise do not allow user to change data, but only look through it
    Blocked user also has no permission.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS and not request.user.is_blocked:
            return True
        return (
            True
            if request.user and (request.user.is_admin or request.user.is_moderator)
            else False
        )


class IsAdminOrModerAndNotBlocked(permissions.BasePermission):
    """Determines whether user is Admin or Moderator and not blocked."""

    def has_permission(self, request, view):
        if (
            request.user
            and not request.user.is_blocked
            and (request.user.is_admin or request.user.is_moderator)
        ):
            return True
        return False


class IsOwnerAdminModerOrReadOnlyOrBlocked(permissions.BasePermission):
    """
    To change profile info user must be
    owner of it, Admin or moderator.
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


class PostIsOwnerAdminModerOrReadOnlyOrBlocked(permissions.BasePermission):
    """
    Post model specified permission.
    Post model requires different syntax to determine the owner of the object
    obj.page.owner instead of obj.owner because post refer
    to page and then page to owner
    Therefore this permission is identical
    to IsOwnerAdminModerOrReadOnlyOrBlocked, just specified for
    post model.
    """

    def has_object_permission(self, request, view, obj):
        if (
            request.user.is_admin
            or request.user.is_moderator
            or obj.page.owner == request.user
            or request.method in permissions.SAFE_METHODS
            and not request.user.is_blocked
        ):
            return True
        return False


class IsNotAuthenticated(permissions.BasePermission):
    """Returns True if user is not authenticated to proceed registration."""

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsBlockedOrReadOnly(permissions.BasePermission):
    """
    Returns True if user is not blocked and uses Safe methods.
    Set as a default permission
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS and not request.user.is_blocked:
            return True
        return False
