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
from api.v1.serializers import SurveyUpdateSerializer


logger = logging.getLogger(__name__)


User = get_user_model()


@sync_to_async
def __save_survey_data(serializer: ModelSerializer) -> dict:
    """
    Сохранить "Опрос" через сериализатор

    Args:
        serializer: сериализатор

    Returns:
        dict: сохраненные данные
    """
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


@sync_to_async
def __create_user(user: TelegramUser) -> User:
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
def __get_or_create_survey(question_start: Question, user_obj: User) -> Survey:
    """
    Получить или создать опрос

    Args:
        question_start: стартовый вопрос
        user_obj: пользователь

    Returns:
        Survey: опрос
    """
    survey_obj, created = Survey.objects.get_or_create(
        user=user_obj,
        defaults={
            "current_question": question_start,
        },
    )
    if created:
        logger.debug("Создан опрос %", survey_obj)
    return survey_obj


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


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    await update.message.reply_text(
        "Привет! Я бот, интегрированный с Django приложением!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    Доступные команды:
    /start - Начать работу
    /help - Помощь
    /users - Количество пользователей
    """
    await update.message.reply_text(help_text)


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда пользователей

    Args:
        update:
        context:

    Returns:

    """
    await update.message.reply_text(f"Всего пользователей: {0}")


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
        user_obj = await __create_user(user)

        question_start = await __get_start_question()
        if not question_start:
            text = "Не существует стартового вопроса для опроса."
            logger.error(text)
            await update.message.reply_text(text)
            return

        survey_obj = await __get_or_create_survey(question_start, user_obj)

        serializer = SurveyUpdateSerializer(
            instance=survey_obj,
            data={"answer": user_message},
            partial=True,
        )

        data = await __save_survey_data(serializer)

        text, answers = (
            data.get("current_question_text"),
            data.get("answers"),
        )
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
