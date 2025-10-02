from datetime import datetime, date
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.utils import timezone


def birthday_validator(value: str | date):
    """Проверяет корректность даты рождения."""
    message = "Пожалуйста, введите корректную дату рождения!"
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValidationError(message)
        value = value.replace(tzinfo=ZoneInfo("UTC"))
        if value >= timezone.now():
            raise ValidationError(message)
    else:
        if value and value >= timezone.now().date():
            raise ValidationError(message)
