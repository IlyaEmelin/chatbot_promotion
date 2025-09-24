import logging
import traceback
from asgiref.sync import sync_to_async

from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
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


logger = logging.getLogger(__name__)


User = get_user_model()


@sync_to_async
def __save_survey_data(
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
    serializer.save()
    data = serializer.data
    return (
        data.get("current_question_text"),
        data.get("answers"),
    )


@sync_to_async
def __get_or_create_user(user: TelegramUser) -> User:
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
def __get_or_create_survey(user_obj: User) -> tuple[
    str,
    list[str | None],
    Survey,
]:
    """
    Получить или создать опрос

    Args:
        user_obj: пользователь

    Returns:
        str: текст текущего вопроса
        list[str|None]: варианта ответа
        Survey: объект вопроса
    """
    create_serializer = SurveyCreateSerializer(
        data={"restart_question": True},
    )
    create_serializer.is_valid(raise_exception=True)
    create_serializer.save(user=user_obj)
    data = create_serializer.data
    return (
        data.get("current_question_text"),
        data.get("answers"),
        create_serializer.instance,
    )


# .instance


def __get_reply_markup(answers: list[str]) -> ReplyKeyboardMarkup | None:
    """
    Получить клавиатуру

    Args:
        answers: список ответов

    Returns:
        ReplyKeyboardMarkup | None: клавиатура с возможными ответами
    """
    reply_markup = None
    if answers:
        keyboard = [[KeyboardButton(answer)] for answer in answers]
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
        user_obj = await __get_or_create_user(user)
        text, answers, __ = await __get_or_create_survey(user_obj)
        welcome_text += text
        reply_markup = __get_reply_markup(answers)
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
        )
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(
            "Ошибка в handle_message: %s\nTraceback:\n%s",
            str(e),
            error_traceback,
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
        user_obj = await __get_or_create_user(user)

        __, ___, survey_obj = await __get_or_create_survey(user_obj)
        text, answers = await __save_survey_data(survey_obj, user_message)

        reply_markup = __get_reply_markup(answers)
        if not text:
            text = "Опрос пройден!"

        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
        )
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(
            "Ошибка в handle_message: %s\nTraceback:\n%s",
            str(e),
            error_traceback,
        )
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
