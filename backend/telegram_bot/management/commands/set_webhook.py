import logging
import requests

from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Устанавливает вебхук для Telegram бота"

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        webhook_url = settings.TELEGRAM_WEBHOOK_URL

        url = f"https://api.telegram.org/bot{token}/setWebhook"
        data = {"url": webhook_url}

        response = requests.post(url, data=data)
        print(response)

        if response.json().get("ok"):
            logger.info("Вебхук успешно установлен!")
        else:
            logger.error("Ошибка при установке вебхука!")
