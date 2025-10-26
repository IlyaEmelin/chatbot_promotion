import logging
import asyncio

from django.conf import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .admin_handlers import log_command
from .const import TelegramCommand
from .menu_handlers import help_command
from .survey_handlers import (
    start_command,
    status_command,
    load_document_command,
    processing_command,
    handle_message,
)

logger = logging.getLogger(__name__)


class TelegramBot:

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(
            CommandHandler(str(TelegramCommand.START.value), start_command),
        )
        self.application.add_handler(
            CommandHandler(str(TelegramCommand.STATUS.value), status_command)
        )
        self.application.add_handler(
            CommandHandler(str(TelegramCommand.HELP.value), help_command),
        )
        self.application.add_handler(
            CommandHandler(
                str(TelegramCommand.PROCESSING.value),
                processing_command,
            ),
        )
        self.application.add_handler(
            CommandHandler(
                str(TelegramCommand.LOG),
                log_command,
            )
        )
        self.application.add_handler(
            MessageHandler(
                filters.PHOTO | filters.Document.IMAGE | filters.Document.PDF,
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
                "Error processing update: %s",
                e,
                exc_info=True,
            )

    def run_polling(self):
        """Запуск бота в режиме polling"""
        logger.info("Starting bot in polling mode.." ".")
        self.application.run_polling()


bot = TelegramBot()
