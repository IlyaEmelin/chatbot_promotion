import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from .const import (
    START_COMMAND_NAME,
    HELP_COMMAND_NAME,
    STATUS_COMMAND_NAME,
    PROCESSING_COMMAND,
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


def _load_documents_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура загрузки документов

    Returns:
        ReplyKeyboardMarkup: клавиатура с кнопкой помощи
    """
    keyboard = [
        [KeyboardButton(f"/{PROCESSING_COMMAND}")],
        [KeyboardButton(f"/{HELP_COMMAND_NAME}")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


async def load_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    load_result: bool | None = None,
    photo_file_id: int | None = None,
):
    """
    Команда /help - помощь с кнопкой помощи

    Args:
        update:
        context: контекст
        load_result: bool - результат загрузки документа,
            None - стандартное сообщение
        photo_file_id: идентификатор файла
    """
    reply_markup = None
    if load_result is None:
        help_text = f"""
📋 *Загрузка документов*

Команды:
/{PROCESSING_COMMAND} - закончить загрузку документов
/{HELP_COMMAND_NAME} - помощь
"""
        reply_markup = _load_documents_keyboard()
        await update.message.reply_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    else:
        caption = (
            "✅ Документ успешно загружен!"
            if load_result
            else "❌ Ошибка загрузки документа"
        )
        if photo_file_id:
            await update.message.reply_photo(
                photo=photo_file_id,
                caption=caption,
            )
        else:
            await update.message.reply_text(
                caption,
                reply_markup=_load_documents_keyboard(),
            )
