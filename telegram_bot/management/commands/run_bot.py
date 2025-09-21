import logging

from django.core.management.base import BaseCommand
from telegram_bot.bot import bot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запускает Telegram бота в режиме polling"

    def handle(self, *args, **options):
        self.stdout.write("Запуск Telegram бота...")
        bot.run_polling()
