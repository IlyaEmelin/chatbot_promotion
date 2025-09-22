import logging

from django.contrib.auth import get_user_model

from telegram import Update, User
from telegram.ext import ContextTypes

from questionnaire.models import Survey, Question
from api.v1.serializers import SurveyUpdateSerializer

logger = logging.getLogger(__name__)


User = get_user_model()


def __create_user(user) -> User:
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
    user: User = update.effective_user

    logger.debug(
        "Получено сообщение от %s (%s): %s",
        user.first_name,
        user.username,
        user_message,
    )

    user_obj = __create_user(user)

    question_start = Question.objects.filter(type="start_telegram").first()
    if not question_start:
        text = "Не существует стартового вопроса для опроса."
        logger.error(text)
        await update.message.reply_text(text)
        return

    survey_obj, created = User.objects.get_or_create(
        user=user_obj,
        defaults={
            "current_question": question_start,
        },
    )
    if created:
        logger.debug("Создан опрос %", survey_obj)

    SurveyUpdateSerializer(instance=survey_obj, data={})

    if created:
        await update.message.reply_text(response)
