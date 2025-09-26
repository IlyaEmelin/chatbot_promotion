from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from django.utils.translation import gettext_lazy as _

from .constants import (
    AGENT_STATUS_CHOISES,
    PHONE_MAX_LENGTH,
    RESIDENCE_NAME_LENGTH,
    TELEGRAM_USERNAME_LENGTH,
    USER_NAME_LENGTH,
)
from .validators import birthday_validator


class User(AbstractUser):
    """Модель для пользователей"""

    first_name = models.CharField(
        _("first name"),
        max_length=USER_NAME_LENGTH,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=USER_NAME_LENGTH,
        blank=True,
        null=True,
    )
    patronymic = models.CharField(
        "Отчество",
        max_length=USER_NAME_LENGTH,
        blank=True,
        null=True,
    )
    ward_first_name = models.CharField(
        "Подопечный. Имя",
        max_length=USER_NAME_LENGTH,
        blank=True,
        null=True,
    )
    ward_last_name = models.CharField(
        "Подопечный. Фамилия",
        max_length=USER_NAME_LENGTH,
        blank=True,
        null=True,
    )
    ward_patronymic = models.CharField(
        "Подопечный. Отчество",
        max_length=USER_NAME_LENGTH,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        _("email address"),
        unique=False,
        null=True,
        blank=True,
    )
    agent_status = models.CharField(
        "Статус контактного лица",
        choices=AGENT_STATUS_CHOISES,
        null=True,
        blank=True,
    )
    birthday = models.DateField(
        "Дата рождения",
        validators=[
            birthday_validator,
        ],
        null=True,
        blank=True,
    )
    residence = models.CharField(
        "Город проживания",
        max_length=RESIDENCE_NAME_LENGTH,
        null=True,
        blank=True,
    )
    phone_number = models.CharField(
        "Номер телефона",
        max_length=PHONE_MAX_LENGTH,
        validators=[
            RegexValidator(
                regex=r"^\+7\d{10}$",
                message="Укажите номер в формате: +7ХХХХХХХХХХ",
            )
        ],
        null=True,
        blank=True,
    )
    telegram_username = models.CharField(
        "Имя пользователя в Телеграм",
        max_length=TELEGRAM_USERNAME_LENGTH,
        validators=[
            RegexValidator(
                regex=r"^@[a-zA-Z0-9]+(_?[a-zA-Z0-9]+)*$",
                message="Укажите корректное имя пользователя начиная с @",
            )
        ],
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "username"

    class Meta:
        verbose_name = "пользователя"
        verbose_name_plural = "Пользователи"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                name="unique_non_empty_email",
                condition=models.Q(email__isnull=False) & ~models.Q(email=""),
            )
        ]

    def __str__(self):
        return self.username
