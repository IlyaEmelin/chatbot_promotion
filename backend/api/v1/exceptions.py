# backend/api/v1/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для DRF
    """
    # Обрабатываем Django ValidationError
    if isinstance(exc, DjangoValidationError):
        errors = {}
        if hasattr(exc, "message_dict"):
            # Для ошибок с message_dict (например, из full_clean())
            errors = exc.message_dict
        elif hasattr(exc, "messages"):
            # Для ошибок с messages
            errors = {"non_field_errors": exc.messages}
        else:
            errors = {"non_field_errors": [str(exc)]}

        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    # Для остальных исключений используем стандартный обработчик
    response = exception_handler(exc, context)

    return response
