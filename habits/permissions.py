from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Разрешение: только владелец может редактировать/удалять"""

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем авторизованным
        if request.method in permissions.SAFE_METHODS:
            return True

        # Изменение только владельцу
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение: чтение всем, изменение только владельцу"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
