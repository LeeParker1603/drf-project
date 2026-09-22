from rest_framework.permissions import BasePermission

class IsModerator(BasePermission):
    """Проверяет, входит ли пользователь в группу модераторов."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='moderators').exists()

class IsOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user