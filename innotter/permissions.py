from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_blocked:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
        return True if request.user and request.user.is_admin else False


class IsAdminOrModerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_blocked:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
        return True if request.user and request.user.is_admin or request.user.is_moderator else False


class IsAdminOrModer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_blocked:
            return False

        if request.user and request.user.is_admin or request.user.is_moderator:
            return True
        return False




