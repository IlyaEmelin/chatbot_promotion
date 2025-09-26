import logging
from asgiref.sync import sync_to_async

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from telegram import (
    Update,
    User as TelegramUser,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes

from questionnaire.models import Survey, Question
from api.v1.serializers import (
    SurveyUpdateSerializer,
    SurveyCreateSerializer,
)
from .menu_handlers import help_command

logger = logging.getLogger(__name__)


User = get_user_model()


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
        data={"answer": user_message},
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
        telegram_username=user.username,
        defaults={
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
def _get_or_create_survey(user_obj: User, restart_question: bool) -> tuple[
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


# .instance


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
        _, __, result, ___ = await _get_or_create_survey(user_obj, False)

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
        await help_command(update, context)
    except Exception as e:
        logger.error(
            "Ошибка в status_command: %s",
            str(e),
            exc_info=True,
        )
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        if survey_obj.status == "new":
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

        await update.message.reply_text("Опрос пройден!")
        await help_command(update, context)
        return

    except Exception as e:
        logger.error(
            "Ошибка в handle_message: %s",
            str(e),
            exc_info=True,
        )
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
