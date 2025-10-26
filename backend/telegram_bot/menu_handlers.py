import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from questionnaire.constant import SurveyStatus
from .const import TelegramCommand
from .sync_to_async import (
    get_or_create_user,
    get_or_create_survey,
)


logger = logging.getLogger(__name__)


def _get_default_help_keyboard(status) -> ReplyKeyboardMarkup:
    """
    Клавиатура по умолчанию с кнопкой помощи

    Args:
        status: статус ответа

    Returns:
        ReplyKeyboardMarkup: клавиатура с кнопкой помощи
    """
    keyboard = [
        [KeyboardButton(TelegramCommand.START.get_call_name())],
        [KeyboardButton(TelegramCommand.STATUS.get_call_name())],
        [KeyboardButton(TelegramCommand.HELP.get_call_name())],
    ]
    if status == SurveyStatus.WAITING_DOCS.value:
        keyboard.insert(
            1,
            [KeyboardButton(TelegramCommand.PROCESSING.get_call_name())],
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
        f"{TelegramCommand.START.get_call_name()} - Пройти(Перепройти) опрос",
        f"{TelegramCommand.STATUS.get_call_name()} - Получить статус опроса",
        f"{TelegramCommand.HELP.get_call_name()} - Показать это сообщение помощи",
    ]
    if status == SurveyStatus.WAITING_DOCS.value:
        commands.insert(
            1,
            f"{TelegramCommand.PROCESSING.get_call_name()} "
            "- Закончить загрузку документов",
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
        if status == SurveyStatus.PROCESSING.value
        else ""
    )

    help_text = f"""
Текущий статус опроса: {SurveyStatus.get_ext_label(status)}
{processing_text}
📋 *Доступные команды:*

{__get_command_text(status)}

💡 *Советы:*
- Используйте кнопки для быстрых ответов
- Вы всегда можете вернуться к помощи через /help
"""
    await update.message.reply_text(
        help_text,
        reply_markup=_get_default_help_keyboard(status),
        parse_mode="Markdown",  # Для красивого форматирования
    )


def _load_documents_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура загрузки документов

    Returns:
        ReplyKeyboardMarkup: клавиатура с кнопкой помощи
    """
    keyboard = [
        [KeyboardButton(TelegramCommand.PROCESSING.get_call_name())],
        [KeyboardButton(TelegramCommand.HELP.get_call_name())],
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
{TelegramCommand.PROCESSING.get_call_name()} - закончить загрузку документов
{TelegramCommand.HELP.get_call_name()} - помощь
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
