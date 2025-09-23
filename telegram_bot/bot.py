import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from django.conf import settings
from .survey_handlers import (
    handle_message,
)
from .menu_handlers import (
    help_command,
    start_command,
)

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(
            CommandHandler("start", start_command),
        )
        self.application.add_handler(
            CommandHandler("help", help_command),
        )
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )

    async def process_webhook_update(self, update_data):
        """Обработка входящего обновления через webhook"""
        try:
            update = Update.de_json(update_data, self.application.bot)
            await self.application.process_update(update)
        except Exception as e:
            logger.error("Error processing update: %s", e)

    def run_polling(self):
        """Запуск бота в режиме polling"""
        logger.error("Starting bot in polling mode...")
        self.application.run_polling()


bot = TelegramBot()
