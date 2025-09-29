import logging
import base64
import imghdr

from asgiref.sync import sync_to_async

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from telegram import (
    Update,
    User as TelegramUser,
    KeyboardButton,
    ReplyKeyboardMarkup,
    File,
)
from telegram.ext import ContextTypes

from questionnaire.models import Survey, Question, Document
from api.v1.serializers import (
    SurveyUpdateSerializer,
    SurveyCreateSerializer,
    DocumentSerializer,
)
from .menu_handlers import help_command, load_command

logger = logging.getLogger(__name__)


User = get_user_model()


@sync_to_async
def _write_document_db(
    survey_obj: Survey,
    content_file: ContentFile,
) -> None:
    """
    Сохранение файлов в базу

    Args:
        survey_obj: опрос
        content_file: файл
    """
    serializer = DocumentSerializer(
        data={
            "image": content_file,
        },
        context={"user": survey_obj.user},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save(survey=survey_obj)


async def telegram_file_to_base64_image_field(file: File) -> str:
    """
    Преобразует Telegram File в строку для Base64ImageField
    Возвращает строку в формате: data:image/jpeg;base64,{base64_data}
    """
    # Скачиваем файл как байты
    file_bytes = await file.download_as_bytearray()

    # Определяем тип изображения
    image_format = imghdr.what(None, h=file_bytes)
    if not image_format:
        # Если imghdr не определил, пробуем по расширению
        image_format = "jpeg"  # значение по умолчанию

    # Маппинг форматов для MIME типов
    mime_types = {
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "bmp": "image/bmp",
        "webp": "image/webp",
    }

    mime_type = mime_types.get(image_format, "image/jpeg")

    # Кодируем в base64
    base64_data = base64.b64encode(file_bytes).decode("utf-8")

    # Формируем data URI
    data_uri = f"data:{mime_type};base64,{base64_data}"
    return data_uri


async def _save_document(
    survey_obj: Survey,
    document_file,
) -> tuple[bool, int | None]:
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
        base64_string = await telegram_file_to_base64_image_field(file)
        await _write_document_db(survey_obj, base64_string)
        logger.debug(
            f"Документ сохранен для опроса %s",
            survey_obj.id,
        )
        return True, document_file.file_id
    except Exception as e:
        logger.error(
            f"Ошибка при сохранении документа: {str(e)}",
            exc_info=True,
        )
        return False, None


@sync_to_async
def __save_survey_data(
    user_obj: User,
    survey_obj: Survey,
    user_message: str,
) -> tuple[str, list[None | str]]:
    """
    Сохранить "Опрос" через сериализатор

    Args:
        survey_obj: опрос,
        user_message: пользовательское сообщение

    Returns:
        str: Вопрос
        list[None|str]: варианты ответа
    """
    serializer = SurveyUpdateSerializer(
        instance=survey_obj,
        data={
            "answer": user_message,
            "add_telegram": False,
        },
        partial=True,
    )
    serializer.is_valid(raise_exception=True)
    serializer.save(user=user_obj)
    data = serializer.data
    return (
        data.get("current_question_text"),
        data.get("answers"),
    )


@sync_to_async
def _get_or_create_user(user: TelegramUser) -> User:
    """
    Создать найти пользователя

    Args:
        user:

    Returns:

    """
    user_obj, created = User.objects.get_or_create(
        telegram_username="@" + user.username,
        defaults={
            "username": user.username,
            "telegram_username": "@" + user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            # TODO При первичной авторизации не задается но потом просят задать
            "password": "unusable_password",
        },
    )
    if created:
        logger.debug("Создан пользователь: %s", user_obj)
    return user_obj


@sync_to_async
def __get_start_question() -> Question | None:
    """
    Стартовый вопрос

    Returns:
        Question | None: вопрос
    """
    return Question.objects.filter(type="start_telegram").first()


@sync_to_async
def _change_processing(survey_obj: Survey) -> None:
    """
    Выставление статуса <В обработке>

    Args:
        survey_obj: объект опроса
    """
    survey_obj.status = "processing"
    survey_obj.save()


@sync_to_async
def _get_or_create_survey(
    user_obj: User,
    restart_question: bool,
) -> tuple[
    str,
    list[str | None],
    list[str],
    Survey,
]:
    """
    Получить или создать опрос

    Args:
        user_obj: пользователь
        restart_question: перезапустить опрос

    Returns:
        str: текст текущего вопроса
        list[str|None]: варианта ответа
        list[str]: данные ответы
        Survey: объект вопроса
    """
    create_serializer = SurveyCreateSerializer(
        data={"restart_question": restart_question},
    )
    create_serializer.is_valid(raise_exception=True)
    create_serializer.save(user=user_obj)
    data = create_serializer.data
    return (
        data.get("current_question_text"),
        data.get("answers"),
        data.get("result"),
        create_serializer.instance,
    )


@sync_to_async
def _get_survey_documents(survey_obj: Survey) -> list[Document]:
    """
    Получить документы опроса

    Args:
        survey_obj: объект опроса

    Returns:
        list: список документов
    """
    documents = survey_obj.docs.all()
    return list(documents)


def _get_reply_markup(answers: list[str]) -> ReplyKeyboardMarkup | None:
    """
    Получить клавиатуру

    Args:
        answers: список ответов

    Returns:
        ReplyKeyboardMarkup | None: клавиатура с возможными ответами
    """
    reply_markup = None
    if answers:
        keyboard = [[KeyboardButton(answer)] for answer in answers if answer]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    return reply_markup


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Команда /start - приветствие с кнопкой помощи
    """
    user = update.effective_user

    welcome_text = (
        f"Привет, {user.first_name}! 👋\n" "Я бот для проведения опросов!\n\n"
    )
    try:
        user_obj = await _get_or_create_user(user)
        text, answers, _, __ = await _get_or_create_survey(user_obj, True)
        welcome_text += text
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
        user_obj = await _get_or_create_user(user)
        _, __, result, survey = await _get_or_create_survey(user_obj, False)

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
        if documents := await _get_survey_documents(survey):
            await update.message.reply_text("📎 Прикрепленные документы:")
            for select_doc in (doc for doc in documents if doc.image):
                try:
                    await update.message.reply_photo(photo=select_doc.image)
                except Exception as e:
                    logger.error(f"Не удалось отправить фото: {e}")

        status_text = {
            "new": "🆕 Новая",
            "waiting_docs": "📎 Ожидает документы",
            "processing": "⏳ В обработке",
            "completed": "✅ Завершена",
        }.get(survey.status, "❌ Ошибка")

        await update.message.reply_text(
            f"Текущий статус заявки: {status_text}"
        )
        await help_command(update, context)
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
            user_obj = await _get_or_create_user(user)

            __, ___, ____, survey_obj = await _get_or_create_survey(
                user_obj, False
            )

        logger.debug("Проверяем статус опроса")
        if survey_obj.status != "waiting_docs":
            await update.message.reply_text(
                "❌ Сначала завершите опрос, затем загружайте документы.\n"
                "Используйте /start для начала опроса."
            )
            return

        logger.debug("Обработка фото")
        photo = None
        if update.message.photo:
            logger.debug(
                "Берем фото самого высокого качества (последнее в списке)"
            )
            photo = update.message.photo[-1]

        if not photo:
            await update.message.reply_text(
                "❌ Файл не обнаружен. Отправьте фото."
            )
            await load_command(update, context)
            return

        result, file_id = await _save_document(survey_obj, photo)

        await load_command(
            update,
            context,
            load_result=result,
            photo_file_id=file_id,
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
        user_obj = await _get_or_create_user(user)

        __, ___, ____, survey_obj = await _get_or_create_survey(
            user_obj, False
        )
        logger.debug("Проверяем статус опроса")
        if survey_obj.status != "waiting_docs":
            await update.message.reply_text(
                "❌ Сначала завершите опрос, затем сменяйте статус.\n"
                "Используйте /start для начала опроса."
            )
            return
        logger.debug("Обработка смена статуса")
        await _change_processing(survey_obj)
        await update.message.reply_text("✅ Ваша заявка принята")
        await help_command(update, context)
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
):
    """Обработка обычных текстовых сообщений"""
    user_message: str = update.message.text
    user: TelegramUser = update.effective_user

    logger.debug(
        "Получено сообщение от %s (%s): %s",
        user.first_name,
        user.username,
        user_message,
    )

    try:
        user_obj = await _get_or_create_user(user)

        __, ___, ____, survey_obj = await _get_or_create_survey(
            user_obj, False
        )
        logger.debug(f"Статус опроса: {survey_obj.status}")
        match survey_obj.status:
            case "new":
                logger.debug("Опрос")
                try:
                    text, answers = await __save_survey_data(
                        user_obj,
                        survey_obj,
                        user_message,
                    )
                except ValidationError as exp:
                    text, answers = "\n".join(exp.messages), []

                reply_markup = _get_reply_markup(answers)
                if text:
                    await update.message.reply_text(
                        text,
                        reply_markup=reply_markup,
                    )
                    return
                else:
                    await load_command(update, context)
            case "waiting_docs":
                logger.debug("Загрузка документов")
                await load_command(update, context)
            case _:
                await help_command(update, context)
        return

    except Exception as e:
        logger.error(
            "Ошибка в handle_message: %s",
            str(e),
            exc_info=True,
        )
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
