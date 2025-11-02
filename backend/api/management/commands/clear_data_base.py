import logging

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.apps import apps

from .add_survey_data import Command as AddSurveyDataCommand

logger = logging.getLogger(__name__)

EXCLUSION_TABLES = {
    "admin",
    "auth",
    "contenttypes",
    "sessions",
}

User = get_user_model()

USERNAME = "admin"
USERNAME_EMAIL = "admin@example.com"
USERNAME_PASSWORD = "admin123"
USERNAME_TELEGRAM = "@TestUser"


class Command(BaseCommand):
    help = "Очищает все данные из базы, но оставляет таблицы"

    def add_arguments(self, parser):
        parser.add_argument(
            "--add_user",
            action="store_true",
            help="Добавить тестового пользователя",
        )
        parser.add_argument(
            "--add_survey_data",
            action="store_true",
            help="Добавить данные опросов из JSON файла",
        )
        parser.add_argument(
            "--file",
            type=str,
            default="survey_data.json",
            help="Путь к JSON файлу с данными опросов",
        )

    def handle(
        self,
        *args,
        add_user=False,
        add_survey_data=False,
        **options,
    ) -> None:
        """
        Очистка записей из базы данных

        Args:
            *args: аргументы
            add_user: добавить пользователя
            add_survey_data:
            **options: именные аргументы
        """
        models = apps.get_models()

        logger.info("Старт очистки всех данных из базы.")
        for model in models:
            if label := model._meta.app_label not in EXCLUSION_TABLES:
                count = model.objects.count()
                model.objects.all().delete()
                logger.info(f"Удалено {count} объектов из {label}")
        logger.info("База данных очищена!")

        if add_user:
            logger.info("Добавление тестового пользователя!")
            if not User.objects.filter(username=USERNAME).exists():
                User.objects.create_superuser(
                    username=USERNAME,
                    email=USERNAME_EMAIL,
                    password=USERNAME_PASSWORD,
                    telegram_username=USERNAME_TELEGRAM,
                )
                logger.info(f"Суперпользователь {USERNAME} создан!")
            else:
                logger.info(f"Пользователь {USERNAME} уже существует")

        if add_survey_data:
            add_survey_data_command = AddSurveyDataCommand()
            add_survey_data_command.handle(*args, **options)
