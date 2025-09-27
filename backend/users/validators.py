from datetime import datetime, date

from django.core.exceptions import ValidationError
from django.utils import timezone


def birthday_validator(value: str | date):
    """Проверяет корректность даты рождения."""
    if isinstance(value, str):
        value = datetime.strptime(value, "%d.%m.%Y").date()
        if value >= timezone.now():
            raise ValidationError(
                "Пожалуйста, введите корректную дату рождения!"
            )
    else:
        if value and value >= timezone.now().date():
            raise ValidationError(
                "Пожалуйста, введите корректную дату рождения!"
            )
