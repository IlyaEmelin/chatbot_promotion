import logging
import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from telegram import (
    Update,
    User as TelegramUser,
    KeyboardButton,
    ReplyKeyboardMarkup,
    File,
)
from telegram.ext import ContextTypes

from questionnaire.models import Survey
from questionnaire.constant import SurveyStatus
from .menu_handlers import help_command, load_command
from .sync_to_async import (
    write_document_db,
    save_survey_data,
    get_or_create_user,
    change_processing,
    get_or_create_survey,
    get_survey_documents,
)
from .const import (
    START_COMMAND_NAME,
)

logger = logging.getLogger(__name__)


User = get_user_model()

FILETYPE_ERROR = "Передан неподдерживаемый формат файла"
SIGNATURES_MIMETYPES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"%PDF": "application/pdf",
}


class FileTypeError(Exception):
    """Класс исключений для неподдерживаемых форматов файлов."""


async def telegram_file_to_base64_image_field(file: File) -> tuple[str, bool]:
    """
    Преобразует Telegram File в строку для Base64ImageField
    Возвращает строку в формате: data:image/jpeg;base64,{base64_data}
    """

    def get_mime_from_signature(binary_data):
        """Определяет MIME-тип по сигнатурам файлов"""
        for signature, mime_type in SIGNATURES_MIMETYPES.items():
            if binary_data.startswith(signature):
                return mime_type
        raise FileTypeError(FILETYPE_ERROR)

    file_bytes = await file.download_as_bytearray()
    mime_type = get_mime_from_signature(file_bytes)
    base64_data = base64.b64encode(file_bytes).decode("utf-8")
    data_uri = f"data:{mime_type};base64,{base64_data}"
    return data_uri, mime_type == SIGNATURES_MIMETYPES[b"%PDF"]


async def _save_document(
    survey_obj: Survey,
    document_file,
) -> tuple[bool, int | None, bool | None]:
    """
    Сохранить документ из Telegram

    Args:
        survey_obj: опрос
        document_file: файл документа из Telegram

    Returns:
        bool: успешность загрузки
        int: файл id
    """
    try:
        file = await document_file.get_file()
        base64_string, is_pdf = await telegram_file_to_base64_image_field(file)
        await write_document_db(survey_obj, base64_string)
        logger.debug(
            "Документ сохранен для опроса %s",
            survey_obj.id,
        )
        return True, document_file.file_id, is_pdf
    except Exception as e:
        logger.error(
            f"Ошибка при сохранении документа: {str(e)}",
            exc_info=True,
        )
        return False, None, None


def _get_reply_markup(answers: list[str]) -> ReplyKeyboardMarkup | None:
    """
    Получить клавиатуру

    Args:
        answers: список ответов

    Returns:
        ReplyKeyboardMarkup | None: клавиатура с возможными ответами
    """
    keyboard = [[KeyboardButton(answer)] for answer in answers if answer]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return reply_markup


async def _inform_msg(survey_obj: Survey, update) -> None:
    """
    Информационное сообщение в зависимости от статуса

    Args:
        survey_obj:
        update:
    """
    match survey_obj.status:
        case SurveyStatus.NEW.value:
            await update.message.reply_text(
                "📝 Опрос еще не завершен. "
                "Пожалуйста, ответьте на все вопросы.\n"
                f"Используйте /{START_COMMAND_NAME} для "
                "продолжение опроса."
            )
        case SurveyStatus.PROCESSING.value:
            await update.message.reply_text(
                "✅ Ваша заявка уже находится в обработке.\n"
                "Ожидайте решения."
            )
        case SurveyStatus.COMPLETED.value:
            # Завершено - все готово
            await update.message.reply_text(
                "🎉 Опрос завершен! Заявка обработана.\n"
                f"Используйте /{START_COMMAND_NAME} для нового опроса."
            )


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Команда /start - приветствие с кнопкой помощи
    """
    user = update.effective_user

    try:
        user_obj = await get_or_create_user(user)
        text, answers, _, __ = await get_or_create_survey(user_obj, True)
        welcome_text = (
            f"Привет, {user.first_name}! 👋\nЯ бот для проведения опросов!\n\n"
        ) + (text or "")
        reply_markup = _get_reply_markup(answers)
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.error(
            "Ошибка в start_command: %s",
            str(e),
            exc_info=True,
        )
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


async def status_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Команда статус заявки

    Args:
        update: Входящее обновление
        context: контекст обновления
    """
    user = update.effective_user
    try:
        user_obj = await get_or_create_user(user)
        _, __, result, survey = await get_or_create_survey(user_obj, False)

        await update.message.reply_text(
            "Результаты опроса:" if result else "Опрос не пройден"
        )
        if result:
            for i, text in enumerate(result):
                await update.message.reply_text(
                    f"✅ Ответ:\n    {text}"
                    if i % 2
                    else f"❓ Вопрос:\n    {text}"
                )

        logger.debug("Добавляем отображение документов")
        if documents := await get_survey_documents(survey):
            await update.message.reply_text("📎 Прикрепленные документы:")
            for select_doc in (doc for doc in documents if doc.image):
                try:
                    await update.message.reply_photo(photo=select_doc.image)
                except Exception as e:
                    logger.error(f"Не удалось отправить фото: {e}")

        await help_command(update, context, status=survey.status)
    except Exception as e:
        logger.error(
            "Ошибка в status_command: %s",
            str(e),
            exc_info=True,
        )
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


async def load_document_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    survey_obj: Survey = None,
) -> None:
    """
    Загрузка документов

    Args:
        update: обновление от Telegram
        context: контекст
        survey_obj: опрос
    """
    try:
        if survey_obj is None:
            user: TelegramUser = update.effective_user
            user_obj = await get_or_create_user(user)

            __, ___, ____, survey_obj = await get_or_create_survey(
                user_obj, False
            )
        logger.debug("Проверяем статус опроса")
        await _inform_msg(survey_obj, update)
        logger.debug("Обработка документа")
        doc_image = None
        if update.message.photo:
            logger.debug(
                "Берем фото самого высокого качества (последнее в списке)"
            )
            doc_image = update.message.photo[-1]
        if update.message.document:
            logger.debug("Берем документ PDF")
            doc_image = update.message.document
        if not doc_image:
            await update.message.reply_text(
                "❌ Файл не обнаружен. Отправьте фото."
            )
            await load_command(update, context)
            return

        result, file_id, is_pdf = await _save_document(survey_obj, doc_image)
        await load_command(
            update,
            context,
            load_result=result,
            photo_file_id=file_id,
            is_pdf=is_pdf,
        )
    except Exception as e:
        logger.error(
            "Ошибка в load_document_command: %s",
            str(e),
            exc_info=True,
        )
        await update.message.reply_text(
            "❌ Произошла ошибка при загрузке документа. Попробуйте позже."
        )
        await load_command(update, context)


async def processing_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Загрузка смена статуса в процессе

    Args:
        update: обновление от Telegram
        context: контекст
    """
    try:
        user: TelegramUser = update.effective_user
        user_obj = await get_or_create_user(user)

        __, ___, ____, survey_obj = await get_or_create_survey(user_obj, False)
        logger.debug("Проверяем статус опроса")
        await _inform_msg(survey_obj, update)
        logger.debug("Обработка смена статуса")
        await change_processing(survey_obj)
        await update.message.reply_text("✅ Ваша заявка принята")
        await help_command(update, context, status=survey_obj.status)
    except Exception as e:
        logger.error(
            "Ошибка в processing_command: %s",
            str(e),
            exc_info=True,
        )
        await update.message.reply_text(
            "❌ Произошла ошибка при смене статуса. Попробуйте позже."
        )
        await load_command(update, context)


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Обработка обычных текстовых сообщений

    Args:
        update: обновление от Telegram
        context: контекст
    """
    user_message: str = update.message.text
    user: TelegramUser = update.effective_user

    logger.debug(
        "Получено сообщение от %s (%s): %s",
        user.first_name,
        user.username,
        user_message,
    )

    try:
        user_obj = await get_or_create_user(user)

        __, ___, ____, survey_obj = await get_or_create_survey(user_obj, False)
        logger.debug(f"Статус опроса: {survey_obj.status}")
        match survey_obj.status:
            case SurveyStatus.NEW.value:
                logger.debug("Опрос")
                new_status = None
                try:
                    text, answers, new_status = await save_survey_data(
                        user_obj,
                        survey_obj,
                        user_message,
                    )
                    if (
                        settings.TELEGRAM_SHOW_RESPONSE_CHOICE
                        and answers
                        and None not in answers
                    ):
                        logger.debug("Подклейка в сообщение вариантов ответа")
                        text += "\nВарианты ответа:\n"
                        text += "\n".join(
                            f"🔘 - {answer}" for answer in answers
                        )
                except ValidationError as exp:
                    text, answers = "\n".join(exp.messages), []

                reply_markup = _get_reply_markup(answers)
                if text:
                    await update.message.reply_text(
                        text,
                        reply_markup=reply_markup,
                    )
                    if survey_obj.status == "waiting_docs":
                        await load_command(update, context)
                    return
                elif new_status != "waiting_docs":
                    await help_command(update, context, new_status)
                else:
                    await load_command(update, context)
            case "waiting_docs":
                logger.debug("Загрузка документов")
                await load_command(update, context)
            case _:
                await help_command(update, context, status=survey_obj.status)
        return

    except Exception as e:
        logger.error(
            "Ошибка в handle_message: %s",
            str(e),
            exc_info=True,
        )
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
