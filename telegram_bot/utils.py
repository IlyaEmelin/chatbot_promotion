import requests
from django.conf import settings

URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"


def send_telegram_message(chat_id, message):
    """
    Отправка сообщения через Telegram API

    Args:
        chat_id: идентификатор чата
        message: сообщение

    Returns:

    """
    data = {"chat_id": chat_id, "text": message}

    response = requests.post(URL, data=data)
    return response.json()
