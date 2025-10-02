import logging
import asyncio

from django.conf import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .admin_handlers import log_command
from .const import (
    START_COMMAND_NAME,
    STATUS_COMMAND_NAME,
    HELP_COMMAND_NAME,
    PROCESSING_COMMAND,
    LOG_COMMAND,
)
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
    _initialized = False

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application = None

    async def _ensure_initialized(self):
        """Гарантирует, что приложение инициализировано"""
        if not self._initialized:
            self.application = Application.builder().token(self.token).build()

            # Добавляем обработчики
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
                CommandHandler(PROCESSING_COMMAND, processing_command),
            )
            self.application.add_handler(
                MessageHandler(
                    (
                        filters.PHOTO
                        | filters.Document.IMAGE
                        | filters.Document.PDF
                    ),
                    load_document_command,
                )
            )
            self.application.add_handler(
                CommandHandler(LOG_COMMAND, log_command)
            )
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
            )

            await self.application.initialize()
            self._initialized = True
            logger.info("Telegram bot application initialized")

    async def process_webhook_update(self, update_data):
        """Обработка входящего обновления через webhook"""
        try:
            await self._ensure_initialized()
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
        import asyncio

        asyncio.run(self._run_polling())

    async def _run_polling(self):
        """Асинхронный запуск polling"""
        await self._ensure_initialized()
        await self.application.run_polling()


bot = TelegramBot()
