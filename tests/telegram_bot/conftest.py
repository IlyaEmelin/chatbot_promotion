import pytest
import django
from django.conf import settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")


def pytest_configure():
    django.setup()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Включение доступа к БД для всех тестов"""
    pass


@pytest.fixture
def mock_telegram_user():
    """Фикстура для mock пользователя Telegram"""
    from unittest.mock import Mock

    user = Mock()
    user.id = 123456
    user.username = "test_user"
    user.first_name = "Test"
    user.last_name = "User"
    return user


@pytest.fixture
def mock_telegram_update(mock_telegram_user):
    """Фикстура для mock обновления Telegram"""
    from unittest.mock import Mock
    from telegram import Update, Message, Chat

    mock_chat = Mock(spec=Chat)
    mock_chat.id = 123456

    mock_message = Mock(spec=Message)
    mock_message.message_id = 1
    mock_message.from_user = mock_telegram_user
    mock_message.chat = mock_chat
    mock_message.text = "test message"
    mock_message.reply_text = Mock()

    mock_update = Mock(spec=Update)
    mock_update.effective_user = mock_telegram_user
    mock_update.message = mock_message

    return mock_update


@pytest.fixture
def mock_context():
    """Фикстура для mock контекста"""
    from unittest.mock import Mock
    from telegram.ext import ContextTypes

    mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    mock_context.bot = Mock()
    mock_context.bot.send_message = Mock()

    return mock_context
