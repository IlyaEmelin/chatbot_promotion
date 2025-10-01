from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from chatbot_promotion.settings import TELEGRAM_ADMIN_IDS, BASE_DIR, DEBUG


async def log_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
):
    """
    Команда /log - отправка лога сервера администратору

    Args:
        update: объект обновления от Telegram
        context: контекст
    """

    user_id = update.effective_user.id
    is_admin = any(
        str(user_id) == str(admin_id) for admin_id in TELEGRAM_ADMIN_IDS
    )

    if not is_admin and not DEBUG:
        return

    log_file_path = Path(BASE_DIR) / 'logs' / 'django.log'

    try:
        with open(log_file_path, 'rb') as log_file:
            await update.message.reply_document(
                document=log_file,
                filename='server.log',
                caption='Вот файл логов сервера'
            )
    except FileNotFoundError:
        await update.message.reply_text(
            'Файл логов не найден - проверьте сервер'
        )
    except Exception as e:
        await update.message.reply_text(
            f'Произошла ошибка при чтении файла логов: {str(e)}'
        )
