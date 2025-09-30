from rest_framework import permissions

from questionnaire.models import Survey


class AuthorOrStaffOnly(permissions.BasePermission):
    """Доступ к данным только авторам и админам."""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.is_staff


class NestedAuthorStaffOnly(permissions.BasePermission):
    """Доступ к запросам только админам, доступ к данным только админам.
    Для вложенных маршрутов (комментарии)"""

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class NestedAuthorOrStaffOnly(permissions.BasePermission):
    """Доступ к запросам только аутентифицированным пользователям
    и админам, доступ к данным только авторам.
    Для вложенных маршрутов (документы)"""

    def has_permission(self, request, view):
        return request.user.is_authenticated or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user == Survey.objects.get(
            id=request.parser_context['kwargs'].get('survey_pk')).user
