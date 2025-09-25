import logging

from django.core.management.base import BaseCommand
from django.conf import settings
import requests

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Тестирование базовой функциональности бота"

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN

        if not token:
            logger.error("Токен бота не настроен!")
            return

        # Проверка получения информации о боте
        url = f"https://api.telegram.org/bot{token}/getMe"

        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get("ok"):
                bot_info = data["result"]
                logger.info(
                    f"Бот активен! Имя: {bot_info['first_name']}, "
                    f"Username: @{bot_info['username']}"
                )
            else:
                logger.error(f"Ошибка: {data.get('description')}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения: {e}")
