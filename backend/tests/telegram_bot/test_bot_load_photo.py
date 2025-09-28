import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from django.test import TestCase
from telegram import Update, Message, User, Chat, PhotoSize
from telegram.ext import ContextTypes

from telegram_bot.survey_handlers import (
    load_document_command,
    _save_document,
    telegram_file_to_base64_image_field,
    _write_document_db,
)
from telegram_bot.menu_handlers import load_command
from telegram_bot.const import (
    LOAD_COMMAND_NAME,
    PROCESSING_COMMAND,
    HELP_COMMAND_NAME,
)


class TestDocumentUpload(TestCase):
    """Тесты для загрузки документов"""

    def setUp(self):
        """Настройка тестового окружения"""
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

    def create_mock_update(self, has_photo=False, photo_size=None):
        """Создание mock объекта Update с фото"""
        mock_update = Mock(spec=Update)
        mock_update.effective_user = self.mock_user
        mock_update.message = self.mock_message
        mock_update.message.reply_text = AsyncMock()
        mock_update.message.reply_photo = AsyncMock()

        if has_photo:
            # Создаем mock фото
            mock_photo = Mock(spec=PhotoSize)
            mock_photo.file_id = "test_file_id_123"
            mock_photo.file_size = 1024000  # 1MB
            mock_photo.width = 1920
            mock_photo.height = 1080

            if photo_size:
                mock_photo.file_size = photo_size

            mock_update.message.photo = [
                mock_photo,
                mock_photo,
            ]  # Несколько размеров

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
    @patch("telegram_bot.survey_handlers._save_document")
    async def test_load_document_command_success(
        self,
        mock_save_document,
        mock_get_user,
        mock_get_survey,
    ):
        """Тест успешной загрузки документа"""
        # Arrange
        mock_update = self.create_mock_update(has_photo=True)
        mock_context = self.create_mock_context()

        mock_survey = Mock()
        mock_survey.status = "waiting_docs"
        mock_survey.id = 1

        mock_get_user.return_value = Mock()
        mock_get_survey.return_value = (None, None, None, mock_survey)
        mock_save_document.return_value = (True, "test_file_id_123")

        # Act
        await load_document_command(mock_update, mock_context)

        # Assert
        mock_save_document.assert_called_once()
        mock_update.message.reply_photo.assert_called_once()

        # Проверяем, что photo_file_id передается правильно
        call_args = mock_update.message.reply_photo.call_args
        assert call_args[1]["photo"] == "test_file_id_123"
        assert call_args[1]["caption"] == "✅ Документ успешно загружен!"

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers._get_or_create_survey")
    @patch("telegram_bot.survey_handlers._get_or_create_user")
    @patch("telegram_bot.survey_handlers._save_document")
    async def test_load_document_command_failure(
        self,
        mock_save_document,
        mock_get_user,
        mock_get_survey,
    ):
        """Тест неудачной загрузки документа"""
        # Arrange
        mock_update = self.create_mock_update(has_photo=True)
        mock_context = self.create_mock_context()

        mock_survey = Mock()
        mock_survey.status = "waiting_docs"

        mock_get_user.return_value = Mock()
        mock_get_survey.return_value = (None, None, None, mock_survey)
        mock_save_document.return_value = (False, None)

        # Act
        await load_document_command(mock_update, mock_context)

        # Assert
        mock_save_document.assert_called_once()

        mock_update.message.reply_photo.assert_not_called()
        mock_update.message.reply_text.assert_called_once()

        call_args = mock_update.message.reply_text.call_args
        assert call_args[0][0] == "❌ Ошибка загрузки документа"
        assert "reply_markup" in call_args[1]

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers._get_or_create_survey")
    @patch("telegram_bot.survey_handlers._get_or_create_user")
    async def test_load_document_command_wrong_status(
        self,
        mock_get_user,
        mock_get_survey,
    ):
        """Тест загрузки документа при неправильном статусе опроса"""
        # Arrange
        mock_update = self.create_mock_update(has_photo=True)
        mock_context = self.create_mock_context()

        mock_survey = Mock()
        mock_survey.status = "new"  # Не waiting_docs

        mock_get_user.return_value = Mock()
        mock_get_survey.return_value = (None, None, None, mock_survey)

        # Act
        await load_document_command(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_with(
            "❌ Сначала завершите опрос, затем загружайте документы.\n"
            "Используйте /start для начала опроса."
        )

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers._write_document_db")
    @patch("telegram_bot.survey_handlers.telegram_file_to_base64_image_field")
    async def test_save_document_success(
        self,
        mock_to_base64,
        mock_write_db,
    ):
        """Тест успешного сохранения документа"""
        # Arrange
        mock_survey = Mock()
        mock_survey.id = 1

        mock_document_file = Mock()
        mock_document_file.file_id = "test_file_id"

        mock_file = AsyncMock()
        mock_document_file.get_file = AsyncMock(return_value=mock_file)

        mock_to_base64.return_value = "base64_string_data"
        mock_write_db.return_value = None

        # Act
        result, file_id = await _save_document(mock_survey, mock_document_file)

        # Assert
        assert result is True
        assert file_id == "test_file_id"
        mock_to_base64.assert_called_once_with(mock_file)
        mock_write_db.assert_called_once()

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers.telegram_file_to_base64_image_field")
    async def test_save_document_exception(
        self,
        mock_to_base64,
    ):
        """Тест исключения при сохранении документа"""
        # Arrange
        mock_survey = Mock()
        mock_document_file = Mock()
        mock_document_file.get_file = AsyncMock()

        mock_to_base64.side_effect = Exception("Test error")

        # Act
        result, file_id = await _save_document(mock_survey, mock_document_file)

        # Assert
        assert result is False
        assert file_id is None

    @pytest.mark.asyncio
    async def test_telegram_file_to_base64_image_field(self):
        """Тест преобразования Telegram файла в base64"""
        # Arrange
        mock_file = AsyncMock()
        mock_file.download_as_bytearray = AsyncMock(
            return_value=b"fake_image_data"
        )

        # Mock imghdr для определения формата
        with patch("telegram_bot.survey_handlers.imghdr.what") as mock_imghdr:
            mock_imghdr.return_value = "jpeg"

            # Act
            result = await telegram_file_to_base64_image_field(mock_file)

            # Assert
            assert result.startswith("data:image/jpeg;base64,")
            assert (
                "ZmFrZV9pbWFnZV9kYXRh" in result
            )  # base64 от "fake_image_data"

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers.DocumentSerializer")
    async def test_write_document_db_success(self, mock_serializer):
        """Тест записи документа в базу данных"""
        # Arrange
        mock_survey = Mock()
        mock_survey.user = Mock()

        mock_content_file = "base64_string_data"

        mock_serializer_instance = Mock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer.return_value = mock_serializer_instance

        # Act
        await _write_document_db(mock_survey, mock_content_file)

        # Assert
        mock_serializer.assert_called_once_with(
            data={"image": mock_content_file},
            context={"user": mock_survey.user},
        )
        mock_serializer_instance.save.assert_called_once_with(
            survey=mock_survey
        )

    @pytest.mark.asyncio
    async def test_load_command_with_photo_success(self):
        """Тест команды загрузки с фото при успешной загрузке"""
        # Arrange
        mock_update = self.create_mock_update()
        mock_context = self.create_mock_context()

        # Act
        await load_command(
            mock_update,
            mock_context,
            load_result=True,
            photo_file_id="test_file_id",
        )

        # Assert
        mock_update.message.reply_photo.assert_called_once_with(
            photo="test_file_id", caption="✅ Документ успешно загружен!"
        )

    @pytest.mark.asyncio
    @patch("telegram_bot.menu_handlers._load_documents_keyboard")
    async def test_load_command_without_photo_success(self, mock_keyboard):
        """Тест команды загрузки без фото при успешной загрузке"""
        # Arrange
        mock_update = self.create_mock_update()
        mock_context = self.create_mock_context()

        mock_keyboard_instance = Mock()
        mock_keyboard.return_value = mock_keyboard_instance

        # Act
        await load_command(
            mock_update, mock_context, load_result=True, photo_file_id=None
        )

        # Assert
        mock_update.message.reply_text.assert_called_with(
            "✅ Документ успешно загружен!",
            reply_markup=mock_keyboard_instance,
        )

    @pytest.mark.asyncio
    async def test_load_command_default_message(self):
        """Тест команды загрузки с сообщением по умолчанию"""
        # Arrange
        mock_update = self.create_mock_update()
        mock_context = self.create_mock_context()

        # Act
        await load_command(mock_update, mock_context, load_result=None)

        # Assert
        mock_update.message.reply_text.assert_called_once()
        args, kwargs = mock_update.message.reply_text.call_args
        assert "Загрузка документов" in args[0]
        assert LOAD_COMMAND_NAME in args[0]
        assert PROCESSING_COMMAND in args[0]
        assert HELP_COMMAND_NAME in args[0]

    @pytest.mark.asyncio
    @patch("telegram_bot.survey_handlers._get_or_create_survey")
    @patch("telegram_bot.survey_handlers._get_or_create_user")
    async def test_load_document_command_with_provided_survey(
        self,
        mock_get_user,
        mock_get_survey,
    ):
        """Тест загрузки документа с предоставленным survey_obj"""
        # Arrange
        mock_update = self.create_mock_update(has_photo=True)
        mock_context = self.create_mock_context()

        mock_survey = Mock()
        mock_survey.status = "waiting_docs"

        # Act
        await load_document_command(
            mock_update, mock_context, survey_obj=mock_survey
        )

        # Assert
        # Не должны вызываться get_user и get_survey, так как survey_obj предоставлен
        mock_get_user.assert_not_called()
        mock_get_survey.assert_not_called()
