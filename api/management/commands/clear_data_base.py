import logging

from django.core.management.base import BaseCommand
from django.apps import apps

logger = logging.getLogger(__name__)

EXCLUSION_TABLES = {
    "admin",
    "auth",
    "contenttypes",
    "sessions",
}


class Command(BaseCommand):
    help = "Очищает все данные из базы, но оставляет таблицы"

    def handle(self, *args, **options) -> None:
        """
        Очистка записей из базы данных

        Args:
            *args: аргументы
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
