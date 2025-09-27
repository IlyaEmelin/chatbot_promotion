import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from .const import (
    START_COMMAND_NAME,
    HELP_COMMAND_NAME,
    STATUS_COMMAND_NAME,
    LOAD_COMMAND_NAME,
    NEXT_STEP_NAME,
)

logger = logging.getLogger(__name__)


def _get_default_help_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура по умолчанию с кнопкой помощи

    Returns:
        ReplyKeyboardMarkup: клавиатура с кнопкой помощи
    """
    keyboard = [
        [KeyboardButton(f"/{START_COMMAND_NAME}")],
        [KeyboardButton(f"/{STATUS_COMMAND_NAME}")],
        [KeyboardButton(f"/{HELP_COMMAND_NAME}")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Команда /help - помощь с кнопкой помощи

    Args:
        update:
        context: контекст
    """

    help_text = f"""
📋 *Доступные команды:*

/{START_COMMAND_NAME} - Пройти(Перепройти) опрос
/{STATUS_COMMAND_NAME} - Получить статус опроса
/{HELP_COMMAND_NAME} - Показать это сообщение помощи

🔍 *Основные функции:*
- Прохождение опросов

💡 *Советы:*
- Используйте кнопки для быстрых ответов
- Вы всегда можете вернуться к помощи через /help
"""
    await update.message.reply_text(
        help_text,
        reply_markup=_get_default_help_keyboard(),
        parse_mode="Markdown",  # Для красивого форматирования
    )
