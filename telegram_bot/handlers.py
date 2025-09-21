from telegram import Update
from telegram.ext import ContextTypes

# from .models import TelegramUser


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    # Сохраняем пользователя в базу данных
    # TelegramUser.objects.get_or_create(
    #     chat_id=chat_id,
    #     defaults={
    #         "username": user.username,
    #         "first_name": user.first_name,
    #         "last_name": user.last_name,
    #     },
    # )

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

    count = TelegramUser.objects.count()
    await update.message.reply_text(f"Всего пользователей: {count}")
