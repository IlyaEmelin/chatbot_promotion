import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from django.conf import settings
from .survey_handlers import (
    start_command,
    status_command,
    load_document_command,
    handle_message,
)
from .menu_handlers import help_command
from .const import (
    START_COMMAND_NAME,
    STATUS_COMMAND_NAME,
    HELP_COMMAND_NAME,
    LOAD_COMMAND_NAME,
    NEXT_STEP_NAME,
)

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(
            CommandHandler(START_COMMAND_NAME, start_command),
        )
        self.application.add_handler(
            CommandHandler(STATUS_COMMAND_NAME, status_command)
        )
        self.application.add_handler(
            CommandHandler(HELP_COMMAND_NAME, help_command),
        )
        self.application.add_handler(
            CommandHandler(LOAD_COMMAND_NAME, load_document_command),
        )
        self.application.add_handler(
            MessageHandler(
                filters.PHOTO | filters.Document.IMAGE | filters.Document.ALL,
                load_document_command,
            )
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
            logger.error(
                "Error processing update: %s\n",
                e,
                exc_info=True,
            )

    def run_polling(self):
        """Запуск бота в режиме polling"""
        logger.error("Starting bot in polling mode...")
        self.application.run_polling()


bot = TelegramBot()
