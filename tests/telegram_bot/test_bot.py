import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from django.test import TestCase
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

from telegram_bot.bot import TelegramBot
from telegram_bot.survey_handlers import start_command, handle_message
from telegram_bot.menu_handlers import help_command
from telegram_bot.const import START_COMMAND_NAME, HELP_COMMAND_NAME


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
    async def test_start_command_success(self):
        """Тест успешного выполнения команды /start"""
        # Arrange
        mock_update = self.create_mock_update()
        mock_context = self.create_mock_context()

        with patch(
            "telegram_bot.survey_handlers._get_or_create_user"
        ) as mock_get_user, patch(
            "telegram_bot.survey_handlers._get_or_create_survey"
        ) as mock_get_survey:

            mock_get_user.return_value = Mock()
            mock_get_survey.return_value = (
                "Тестовый вопрос",
                ["Ответ 1", "Ответ 2"],
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
    async def test_start_command_exception(self):
        """Тест обработки исключения в команде /start"""
        # Arrange
        mock_update = self.create_mock_update()
        mock_context = self.create_mock_context()

        with patch(
            "telegram_bot.survey_handlers._get_or_create_user"
        ) as mock_get_user:
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
    async def test_handle_message_new_survey(self):
        """Тест обработки сообщения для нового опроса"""
        # Arrange
        mock_update = self.create_mock_update(text="Ответ пользователя")
        mock_context = self.create_mock_context()

        with patch(
            "telegram_bot.survey_handlers._get_or_create_user"
        ) as mock_get_user, patch(
            "telegram_bot.survey_handlers._get_or_create_survey"
        ) as mock_get_survey, patch(
            "telegram_bot.survey_handlers.__save_survey_data"
        ) as mock_save_data:

            mock_survey = Mock()
            mock_survey.status = "new"

            mock_get_user.return_value = Mock()
            mock_get_survey.return_value = (None, None, mock_survey)
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
    async def test_handle_message_completed_survey(self):
        """Тест обработки сообщения для завершенного опроса"""
        # Arrange
        mock_update = self.create_mock_update(text="Любой текст")
        mock_context = self.create_mock_context()

        with patch(
            "telegram_bot.survey_handlers._get_or_create_user"
        ) as mock_get_user, patch(
            "telegram_bot.survey_handlers._get_or_create_survey"
        ) as mock_get_survey, patch(
            "telegram_bot.survey_handlers.help_command"
        ) as mock_help:

            mock_survey = Mock()
            mock_survey.status = "completed"

            mock_get_user.return_value = Mock()
            mock_get_survey.return_value = (None, None, mock_survey)
            mock_help.return_value = None

            # Act
            await handle_message(mock_update, mock_context)

            # Assert
            mock_update.message.reply_text.assert_called_with("Опрос пройден!")
            mock_help.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_message_exception(self):
        """Тест обработки исключения в handle_message"""
        # Arrange
        mock_update = self.create_mock_update(text="Текст")
        mock_context = self.create_mock_context()

        with patch(
            "telegram_bot.survey_handlers._get_or_create_user"
        ) as mock_get_user:
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
        assert len(handlers) == 3  # start, help, message

        # Проверяем типы обработчиков
        handler_types = [type(handler).__name__ for handler in handlers]
        assert "CommandHandler" in handler_types
        assert "MessageHandler" in handler_types

    @pytest.mark.asyncio
    async def test_process_webhook_update(self):
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

        with patch("telegram_bot.bot.Update.de_json") as mock_dejson, patch(
            "telegram_bot.bot.Application.process_update"
        ) as mock_process:

            mock_dejson.return_value = Mock()
            mock_process.return_value = None

            # Act
            await self.bot.process_webhook_update(update_data)

            # Assert
            mock_dejson.assert_called_once()
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_webhook_update_exception(self):
        """Тест обработки исключения в webhook"""
        # Arrange
        update_data = {"invalid": "data"}

        # Act
        with patch("telegram_bot.bot.logger.error") as mock_logger:
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
        assert len(keyboard.keyboard) == 2
        assert f"/{START_COMMAND_NAME}" in str(keyboard.keyboard[0][0])
        assert f"/{HELP_COMMAND_NAME}" in str(keyboard.keyboard[1][0])

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
