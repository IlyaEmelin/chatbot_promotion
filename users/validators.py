from django.core.exceptions import ValidationError
from django.utils import timezone


def birthday_validator(value):
    """Проверяет корректность даты рождения."""
    if value >= timezone.now():
        raise ValidationError(
            'Пожалуйста, введите корректную дату рождения!'
        )