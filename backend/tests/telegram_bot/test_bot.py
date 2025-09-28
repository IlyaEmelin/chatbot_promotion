import pytest
from unittest.mock import Mock, patch, AsyncMock
from django.test import TestCase
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

from telegram_bot.bot import TelegramBot
from telegram_bot.survey_handlers import start_command, handle_message
from telegram_bot.menu_handlers import help_command
from telegram_bot.const import (
    START_COMMAND_NAME,
    HELP_COMMAND_NAME,
    STATUS_COMMAND_NAME,
)


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
    @patch("telegram_bot.survey_handlers._get_or_create_survey")
    @patch("telegram_bot.survey_handlers._get_or_create_user")
    async def test_start_command_success(
        self,
        mock_get_user,
        mock_get_survey,
    ):
        """Тест успешного выполнения команды /start"""
        # Arrange
        mock_update = self.create_mock_update()
        mock_context = self.create_mock_context()

        mock_get_user.return_value = Mock()
        mock_get_survey.return_value = (
            "Тестовый вопрос",
            ["Ответ 1", "Ответ 2"],
            [],
            Mock(),
        )

        # Act
        await start_command(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_once()
        args, kwargs = mock_update.message.reply_text.call_args
        assert "Привет, Test!" in args[0]
        assert "Тестовый вопрос" in args[0]

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers._get_or_create_user")
    async def test_start_command_exception(self, mock_get_user):
        """Тест обработки исключения в команде /start"""
        # Arrange
        mock_update = self.create_mock_update()
        mock_context = self.create_mock_context()

        mock_get_user.side_effect = Exception("Test error")

        # Act
        await start_command(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_with(
            "Произошла ошибка. Попробуйте позже."
        )

    @pytest.mark.asyncio
    async def test_help_command(self):
        """Тест команды /help"""
        # Arrange
        mock_update = self.create_mock_update()
        mock_context = self.create_mock_context()

        # Act
        await help_command(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_once()
        args, kwargs = mock_update.message.reply_text.call_args
        assert "Доступные команды" in args[0]
        assert "Markdown" in kwargs.get("parse_mode", "")

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers.__save_survey_data")
    @patch("telegram_bot.survey_handlers._get_or_create_survey")
    @patch("telegram_bot.survey_handlers._get_or_create_user")
    async def test_handle_message_new_survey(
        self,
        mock_get_user,
        mock_get_survey,
        mock_save_data,
    ):
        """Тест обработки сообщения для нового опроса"""
        # Arrange
        mock_update = self.create_mock_update(text="Ответ пользователя")
        mock_context = self.create_mock_context()

        mock_survey = Mock()
        mock_survey.status = "new"

        mock_get_user.return_value = Mock()
        mock_get_survey.return_value = (None, None, None, mock_survey)
        mock_save_data.return_value = (
            "Следующий вопрос",
            ["Ответ 1", "Ответ 2"],
        )

        # Act
        await handle_message(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_once()
        args, kwargs = mock_update.message.reply_text.call_args
        assert "Следующий вопрос" in args[0]

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers.help_command")
    @patch("telegram_bot.survey_handlers._get_or_create_survey")
    @patch("telegram_bot.survey_handlers._get_or_create_user")
    async def test_handle_message_completed_survey(
        self,
        mock_get_user,
        mock_get_survey,
        mock_help,
    ):
        """Тест обработки сообщения для завершенного опроса"""
        # Arrange
        mock_update = self.create_mock_update(text="Любой текст")
        mock_context = self.create_mock_context()

        mock_survey = Mock()
        mock_survey.status = "completed"

        mock_get_user.return_value = Mock()
        mock_get_survey.return_value = (None, None, None, mock_survey)
        mock_help.return_value = None

        # Act
        await handle_message(mock_update, mock_context)

        # Assert
        mock_help.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers._get_or_create_user")
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
        assert len(handlers) == 6  # start, help, status, message

        # Проверяем типы обработчиков
        handler_types = [type(handler).__name__ for handler in handlers]
        assert "CommandHandler" == handler_types[0]
        assert "CommandHandler" == handler_types[1]
        assert "CommandHandler" == handler_types[2]
        assert "CommandHandler" == handler_types[3]
        assert "MessageHandler" == handler_types[4]
        assert "MessageHandler" == handler_types[5]

    @pytest.mark.asyncio
    @patch("telegram_bot.bot.Application.process_update")
    @patch("telegram_bot.bot.Update.de_json")
    async def test_process_webhook_update(self, mock_dejson, mock_process):
        """Тест обработки webhook обновления"""
        # Arrange
        update_data = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 123456,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "test_user",
                },
                "chat": {
                    "id": 123456,
                    "first_name": "Test",
                    "username": "test_user",
                    "type": "private",
                },
                "date": 1630000000,
                "text": "test message",
            },
        }

        mock_dejson.return_value = Mock()
        mock_process.return_value = None

        # Act
        await self.bot.process_webhook_update(update_data)

        # Assert
        mock_dejson.assert_called_once()
        mock_process.assert_called_once()

    @pytest.mark.asyncio
    @patch("telegram_bot.bot.logger.error")
    async def test_process_webhook_update_exception(self, mock_logger):
        """Тест обработки исключения в webhook"""
        # Arrange
        update_data = {"invalid": "data"}

        # Act
        await self.bot.process_webhook_update(update_data)

        # Assert
        mock_logger.assert_called_once()


class TestKeyboardFunctions:
    """Тесты для функций клавиатуры"""

    def test_get_default_help_keyboard(self):
        """Тест создания клавиатуры помощи"""
        from telegram_bot.menu_handlers import _get_default_help_keyboard

        # Act
        keyboard = _get_default_help_keyboard()

        # Assert
        assert keyboard is not None
        assert len(keyboard.keyboard) == 3
        assert f"/{START_COMMAND_NAME}" in str(keyboard.keyboard[0][0])
        assert f"/{STATUS_COMMAND_NAME}" in str(keyboard.keyboard[1][0])
        assert f"/{HELP_COMMAND_NAME}" in str(keyboard.keyboard[2][0])

    def test_get_reply_markup_with_answers(self):
        """Тест создания клавиатуры с ответами"""
        from telegram_bot.survey_handlers import _get_reply_markup

        # Arrange
        answers = ["Ответ 1", "Ответ 2", "Ответ 3"]

        # Act
        markup = _get_reply_markup(answers)

        # Assert
        assert markup is not None
        assert len(markup.keyboard) == 3

    def test_get_reply_markup_empty_answers(self):
        """Тест создания клавиатуры без ответов"""
        from telegram_bot.survey_handlers import _get_reply_markup

        # Act
        markup = _get_reply_markup([])

        # Assert
        assert markup is None


class TestConstants:
    """Тесты констант"""

    def test_command_names(self):
        """Тест имен команд"""
        from telegram_bot.const import START_COMMAND_NAME, HELP_COMMAND_NAME

        assert START_COMMAND_NAME == "start"
        assert HELP_COMMAND_NAME == "help"
        assert isinstance(START_COMMAND_NAME, str)
        assert isinstance(HELP_COMMAND_NAME, str)


class TestIntegration:
    """Интеграционные тесты"""

    def create_mock_update(self, text=None):
        """Создание mock объекта Update"""
        mock_user = Mock(spec=User)
        mock_user.id = 123456
        mock_user.username = "test_user"
        mock_user.first_name = "Test"

        mock_chat = Mock(spec=Chat)
        mock_chat.id = 123456

        mock_message = Mock(spec=Message)
        mock_message.message_id = 1
        mock_message.from_user = mock_user
        mock_message.chat = mock_chat
        mock_message.text = text or "test message"
        mock_message.reply_text = AsyncMock()

        mock_update = Mock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.message = mock_message

        return mock_update

    def create_mock_context(self):
        """Создание mock объекта Context"""
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot = Mock()
        mock_context.bot.send_message = AsyncMock()
        return mock_context

    @pytest.mark.asyncio
    @patch("telegram_bot.menu_handlers._get_default_help_keyboard")
    async def test_help_command_integration(self, mock_keyboard):
        """Интеграционный тест команды помощи"""
        # Arrange
        mock_update = self.create_mock_update()
        mock_context = self.create_mock_context()
        mock_keyboard.return_value = Mock()

        # Act
        await help_command(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers.__save_survey_data")
    @patch("telegram_bot.survey_handlers._get_or_create_survey")
    @patch("telegram_bot.survey_handlers._get_or_create_user")
    @patch("telegram_bot.survey_handlers._get_reply_markup")
    async def test_handle_message_integration(
        self,
        mock_markup,
        mock_get_user,
        mock_get_survey,
        mock_save_data,
    ):
        """Интеграционный тест обработки сообщения"""
        # Arrange
        mock_update = self.create_mock_update(text="Тестовый ответ")
        mock_context = self.create_mock_context()

        mock_survey = Mock()
        mock_survey.status = "new"

        mock_get_user.return_value = Mock()
        mock_get_survey.return_value = (None, None, None, mock_survey)
        mock_save_data.return_value = ("Вопрос", ["Ответ"])
        mock_markup.return_value = Mock()

        # Act
        await handle_message(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_once()
        mock_markup.assert_called_once_with(["Ответ"])
