from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем профиля."""
    def has_object_permission(self, request, view, obj):
        return obj == request.user