import pytest
from unittest.mock import Mock, patch, AsyncMock
from django.test import TestCase
from telegram import (
    Update,
    Message,
    User,
    Chat,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import ContextTypes

from telegram_bot.bot import TelegramBot
from telegram_bot.survey_handlers import handle_message
from questionnaire.constant import TelegramCommand, SurveyStatus
from telegram_bot.menu_handlers import _get_default_help_keyboard


class TestTelegramBot(TestCase):
    def setUp(self):
        """Настройка тестового окружения"""
        self.bot = TelegramBot()

        # Mock для Telegram объектов
        self.mock_user = Mock(spec=User)
        self.mock_user.id = 123456
        self.mock_user.username = "test_user"
        self.mock_user.first_name = "Test"
        self.mock_user.last_name = "User"

        self.mock_chat = Mock(spec=Chat)
        self.mock_chat.id = 123456

        self.mock_message = Mock(spec=Message)
        self.mock_message.message_id = 1
        self.mock_message.from_user = self.mock_user
        self.mock_message.chat = self.mock_chat
        self.mock_message.text = "test message"

    def create_mock_update(self, text=None):
        """Создание mock объекта Update"""
        if text:
            self.mock_message.text = text

        mock_update = Mock(spec=Update)
        mock_update.effective_user = self.mock_user
        mock_update.message = self.mock_message
        mock_update.message.reply_text = AsyncMock()

        return mock_update

    def create_mock_context(self):
        """Создание mock объекта Context"""
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot = Mock()
        mock_context.bot.send_message = AsyncMock()
        return mock_context

    @pytest.mark.asyncio
    @patch("telegram_bot.sync_to_async.get_or_create_user")
    async def test_handle_message_exception(self, mock_get_user):
        """Тест обработки исключения в handle_message"""
        # Arrange
        mock_update = self.create_mock_update(text="Текст")
        mock_context = self.create_mock_context()

        mock_get_user.side_effect = Exception("Test error")

        # Act
        await handle_message(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_with(
            "Произошла ошибка. Попробуйте позже."
        )

    def test_bot_initialization(self):
        """Тест инициализации бота"""
        # Act & Assert
        assert self.bot.token is not None
        assert self.bot.application is not None

    def test_handlers_registration(self):
        """Тест регистрации обработчиков"""
        # Arrange
        handlers = self.bot.application.handlers[0]

        # Assert
        assert len(handlers) == 7

        # Проверяем типы обработчиков
        handler_types = [type(handler).__name__ for handler in handlers]
        assert "MessageHandler" == handler_types[0]
        assert "MessageHandler" == handler_types[1]
        assert "MessageHandler" == handler_types[2]
        assert "MessageHandler" == handler_types[3]
        assert "CommandHandler" == handler_types[4]
        assert "MessageHandler" == handler_types[5]
        assert "MessageHandler" == handler_types[6]


class TestKeyboardFunctions:
    """Тесты для функций клавиатуры"""

    def test_get_default_help_keyboard(self):
        """Тест создания клавиатуры помощи"""

        # Act
        keyboard = _get_default_help_keyboard(SurveyStatus.NEW)

        # Assert
        assert keyboard is not None
        assert len(keyboard.keyboard) == 3
        assert TelegramCommand.START.get_button_text() in str(
            keyboard.keyboard[0][0]
        )
        assert TelegramCommand.STATUS.get_button_text() in str(
            keyboard.keyboard[1][0]
        )
        assert TelegramCommand.HELP.get_button_text() in str(
            keyboard.keyboard[2][0]
        )

    def test_get_default_help_keyboard2(self):
        """Тест создания клавиатуры помощи"""

        # Act
        keyboard = _get_default_help_keyboard(SurveyStatus.WAITING_DOCS)

        # Assert
        assert keyboard is not None
        assert len(keyboard.keyboard) == 4
        assert TelegramCommand.START.get_button_text() in str(
            keyboard.keyboard[0][0]
        )
        assert TelegramCommand.PROCESSING.get_button_text() in str(
            keyboard.keyboard[1][0]
        )
        assert TelegramCommand.STATUS.get_button_text() in str(
            keyboard.keyboard[2][0]
        )
        assert TelegramCommand.HELP.get_button_text() in str(
            keyboard.keyboard[3][0]
        )

    def test_get_reply_markup_with_answers(self):
        """Тест создания клавиатуры с ответами"""
        from telegram_bot.survey_handlers import _get_reply_markup

        # Arrange
        answers = ["Ответ 1", "Ответ 2", "Ответ 3"]

        # Act
        markup = _get_reply_markup(answers)

        # Assert
        assert markup is not None
        assert markup == ReplyKeyboardMarkup(
            [
                [KeyboardButton("Ответ 1")],
                [KeyboardButton("Ответ 2")],
                [KeyboardButton("Ответ 3")],
            ],
            one_time_keyboard=True,
            resize_keyboard=True,
        )

    def test_get_reply_markup_empty_answers(self):
        """Тест создания клавиатуры без ответов"""
        from telegram_bot.survey_handlers import _get_reply_markup

        # Act
        markup = _get_reply_markup([])

        # Assert
        assert markup == ReplyKeyboardMarkup(
            [],
            one_time_keyboard=True,
            resize_keyboard=True,
        )
