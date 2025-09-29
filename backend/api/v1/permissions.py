from rest_framework import permissions


class AuthorOnly(permissions.BasePermission):
    """Позволяет только самому пользователю редактировать свои данные."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
