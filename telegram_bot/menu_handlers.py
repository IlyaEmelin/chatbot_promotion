import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def __get_default_help_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура по умолчанию с кнопкой помощи

    Returns:
        ReplyKeyboardMarkup: клавиатура с кнопкой помощи
    """
    keyboard = [
        [KeyboardButton("/help")],  # Кнопка помощи
        [KeyboardButton("Начать опрос")],  # Дополнительная кнопка
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,  # Клавиатура остается постоянно
    )


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Команда /start - приветствие с кнопкой помощи
    """
    chat_id = update.effective_chat.id
    user = update.effective_user

    welcome_text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот для проведения опросов!\n\n"
        "Для получения списка команд нажмите кнопку 'Помощь' или введите /help"
    )

    logging.debug("Отправляем сообщение с клавиатурой по умолчанию")
    await update.message.reply_text(
        welcome_text, reply_markup=__get_default_help_keyboard()
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Команда /help - помощь с кнопкой помощи
    """
    help_text = """
📋 *Доступные команды:*

/start - Начать работу с ботом
/help - Показать это сообщение помощи

🔍 *Основные функции:*
- Прохождение опросов
- Ответы на вопросы
- Автоматическое сохранение результатов

💡 *Советы:*
- Используйте кнопки для быстрых ответов
- Вы всегда можете вернуться к помощи через /help
"""

    # Отправляем помощь с той же клавиатурой
    await update.message.reply_text(
        help_text,
        reply_markup=__get_default_help_keyboard(),
        parse_mode="Markdown",  # Для красивого форматирования
    )
