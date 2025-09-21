from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from django.utils.translation import gettext_lazy as _

from constants import (AGENT_STATUS_CHOISES,
                       PHONE_MAX_LENGTH,
                       RESIDENCE_NAME_LENGTH,
                       TELEGRAM_USERNAME_LENGTH,
                       USER_NAME_LENGTH,)
from validators import birthday_validator


class User(AbstractUser):
    """Модель для пользователей"""
    first_name = models.CharField(
        _('first name'),
        max_length=USER_NAME_LENGTH,
        blank=False
    )
    last_name = models.CharField(
        _('last name'),
        max_length=USER_NAME_LENGTH,
        blank=False
    )
    email = models.EmailField(
        _('email address'),
        unique=True
    )
    agent = models.CharField(
        'Контактное лицо',
        max_length=USER_NAME_LENGTH,
    )
    agent_status = models.CharField(
        'Статус контактного лица',
        choices=AGENT_STATUS_CHOISES,
    )
    birthday = models.DateField(
        'Дата рождения',
        validators=[birthday_validator,]
    )
    residence = models.CharField(
        'Город проживания',
        max_length=RESIDENCE_NAME_LENGTH
    )
    phone_number = models.CharField(
        'Номер телефона',
        max_length=PHONE_MAX_LENGTH,
        validators=[
            RegexValidator(
                regex=r'^\+7\d{10}$',
                message='Укажите номер в формате: +7ХХХХХХХХХХ'
            )
        ]
    )
    telegram_username = models.CharField(
        'Имя пользователя в Телеграм',
        max_length=TELEGRAM_USERNAME_LENGTH,
        validators=[
            RegexValidator(
                regex=r'^@[a-zA-Z0-9]+(_?[a-zA-Z0-9]+)*$',
                message='Укажите корректное имя пользователя начиная с @'
            )
        ]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username
