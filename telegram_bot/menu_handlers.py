import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from .const import START_COMMAND_NAME, HELP_COMMAND_NAME

logger = logging.getLogger(__name__)


def __get_default_help_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура по умолчанию с кнопкой помощи

    Returns:
        ReplyKeyboardMarkup: клавиатура с кнопкой помощи
    """
    keyboard = [
        [KeyboardButton(f"/{START_COMMAND_NAME}")],
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
    """
    help_text = """
📋 *Доступные команды:*

/start - Начать работу с ботом
/help - Показать это сообщение помощи

🔍 *Основные функции:*
- Прохождение опросов
- Ответы на вопросы
- Автоматическое сохранение результатов

💡 *Советы:*
- Используйте кнопки для быстрых ответов
- Вы всегда можете вернуться к помощи через /help
"""

    # Отправляем помощь с той же клавиатурой
    await update.message.reply_text(
        help_text,
        reply_markup=__get_default_help_keyboard(),
        parse_mode="Markdown",  # Для красивого форматирования
    )
