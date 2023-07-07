from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Если не админ - доступ только на чтение."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )


class AuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """Автор, модератор и админ могут обновить данные, иначе только чтение."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
            or request.user == obj.author
        )
