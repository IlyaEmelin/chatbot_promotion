import logging

from django.conf import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from questionnaire.constant import TelegramCommand
from .admin_handlers import log_command
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
            MessageHandler(
                filters.Text(
                    TelegramCommand.START.get_all_select_command(),
                ),
                start_command,
            ),
        )
        self.application.add_handler(
            MessageHandler(
                filters.Text(TelegramCommand.STATUS.get_all_select_command()),
                status_command,
            )
        )
        self.application.add_handler(
            MessageHandler(
                filters.Text(TelegramCommand.HELP.get_all_select_command()),
                help_command,
            )
        )
        self.application.add_handler(
            MessageHandler(
                filters.Text(
                    TelegramCommand.PROCESSING.get_all_select_command()
                ),
                processing_command,
            )
        )
        self.application.add_handler(
            CommandHandler(
                TelegramCommand.LOG.value,
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
