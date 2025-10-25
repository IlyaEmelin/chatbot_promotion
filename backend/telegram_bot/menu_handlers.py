import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from .const import (
    START_COMMAND_NAME,
    HELP_COMMAND_NAME,
    STATUS_COMMAND_NAME,
    PROCESSING_COMMAND,
)
from .sync_to_async import (
    get_or_create_user,
    get_or_create_survey,
)

STATUS_DICT = {
    "new": "🆕 Новая",
    "waiting_docs": "📎 Ожидает документы",
    "processing": "⏳ В обработке",
    "completed": "✅ Завершен",
}

logger = logging.getLogger(__name__)


def __get_status(status: str) -> str:
    """
    Получить текстовое описание статуса на интерфейсе.

    Args:
        status: внутренне имя статуса

    Returns:
        str: читаемое название
    """
    return STATUS_DICT.get(status, "❌ Ошибка")


def _get_default_help_keyboard(add_processing_command) -> ReplyKeyboardMarkup:
    """
    Клавиатура по умолчанию с кнопкой помощи
    Args:
        add_processing_command: добавить команду закончить загрузку документов

    Returns:
        ReplyKeyboardMarkup: клавиатура с кнопкой помощи
    """
    keyboard = [
        [KeyboardButton(f"/{START_COMMAND_NAME}")],
        [KeyboardButton(f"/{STATUS_COMMAND_NAME}")],
        [KeyboardButton(f"/{HELP_COMMAND_NAME}")],
    ]
    if add_processing_command:
        keyboard.insert(
            1,
            [KeyboardButton(f"/{PROCESSING_COMMAND}")],
        )

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def __get_command_text(status) -> str:
    """
    Получить список доступных команд

    Args:
        status: статус ответа

    Returns:
        str: текстовый список доступных команд
    """
    commands = [
        f"/{START_COMMAND_NAME} - Пройти(Перепройти) опрос",
        f"/{STATUS_COMMAND_NAME} - Получить статус опроса",
        f"/{HELP_COMMAND_NAME} - Показать это сообщение помощи",
    ]
    if status == "waiting_docs":
        commands.insert(
            1,
            f"/{PROCESSING_COMMAND} - Закончить загрузку документов",
        )
    return "\n".join(commands)


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    status: str | None = None,
):
    """
    Команда /help - помощь с кнопкой помощи

    Args:
        update:
        context: контекст
        status: статус ответа
    """
    if status is None:
        user = update.effective_user
        user_obj = await get_or_create_user(user)
        _, __, result, survey = await get_or_create_survey(user_obj, False)
        status = survey.status

    processing_text = (
        "Спасибо за вашу заявку, свяжемся с вами по указанными вами контактам "
        "в ближайшее время"
        if status == "processing"
        else ""
    )

    help_text = f"""
Текущий статус опроса: {__get_status(status)}
{processing_text}
📋 *Доступные команды:*

{__get_command_text(status)}

💡 *Советы:*
- Используйте кнопки для быстрых ответов
- Вы всегда можете вернуться к помощи через /help
"""
    await update.message.reply_text(
        help_text,
        reply_markup=_get_default_help_keyboard(status == "processing"),
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
    is_pdf: bool | None = None,
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
        if is_pdf:
            await update.message.reply_document(
                document=photo_file_id,
                caption=caption,
            )
        elif photo_file_id:
            await update.message.reply_photo(
                photo=photo_file_id,
                caption=caption,
            )
        else:
            await update.message.reply_text(
                caption,
                reply_markup=_load_documents_keyboard(),
            )
