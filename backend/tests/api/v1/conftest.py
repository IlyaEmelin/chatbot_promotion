# conftest.py
from uuid import uuid4

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from questionnaire.models import Question, AnswerChoice, Survey, Document
from unittest.mock import patch, MagicMock
import pytest
import requests

User = get_user_model()


UPLOAD_URL = 'https://mock-upload.url/test.txt'
DOWNLOAD_URL = 'https://mock-download.url/test.txt'
LOCATION = 'https://disk.yandex.ru/disk/test.txt'
TEST_IMAGE_URL = 'https://example.com/test.jpg'
TEST_IMAGES_URLS = 'https://example.com/{}.jpg'



@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user() -> User:
    """
    Тестовый пользователь

    Returns:
        User: пользователь
    """
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def authenticated_client(
    api_client: APIClient,
    user: User,
) -> APIClient:
    """
    Получить аутентифицированного клиента

    Args:
        api_client: клиент
        user: пользователь

    Returns:
        APIClient: клиент
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def question() -> Question:
    """
    Первый вопрос

    Returns:
        Question: первый вопрос
    """
    return Question.objects.create(
        text="Тестовый вопрос?",
        updated_uuid="12345678-1234-1234-1234-123456789012",
        type="start",
    )


@pytest.fixture
def answer_choice(question: Question) -> Question:
    """
    Второй вопрос

    Args:
        question: первый вопрос

    Returns:
        Question: второй вопрос
    """
    next_question = Question.objects.create(
        text="Следующий вопрос?",
        updated_uuid="22345678-1234-1234-1234-123456789012",
    )
    return AnswerChoice.objects.create(
        current_question=question,
        next_question=next_question,
        answer="test_answer",
    )


@pytest.fixture
def survey(user, question) -> Survey:
    """
    Получить опрос

    Args:
        user: пользователь
        question: первый вопрос

    Returns:
        Survey: опрос
    """
    return Survey.objects.create(
        user=user,
        current_question=question,
        status="new",
        result=[],
        questions_version_uuid="32345678-1234-1234-1234-123456789012",
    )


@pytest.fixture
def question_with_custom_answer() -> Question:
    """Вопрос с вариантом для пользовательского ответа"""
    question = Question.objects.create(
        text="Вопрос с пользовательским ответом?",
        updated_uuid="52345678-1234-1234-1234-123456789012",
    )

    # Создаем AnswerChoice для пользовательского ответа
    next_question = Question.objects.create(
        text="Следующий вопрос после пользовательского",
        updated_uuid="62345678-1234-1234-1234-123456789012",
    )
    AnswerChoice.objects.create(
        current_question=question,
        next_question=next_question,
        answer=None,  # Для пользовательских ответов
    )
    return question


@pytest.fixture
def survey_with_custom_answer(user, question_with_custom_answer) -> Survey:
    """Опрос с вопросом, имеющим пользовательский ответ"""
    return Survey.objects.create(
        user=user,
        current_question=question_with_custom_answer,
        status="new",
        result=[],
        questions_version_uuid="72345678-1234-1234-1234-123456789012",
    )


@pytest.fixture
def question_with_final_answer() -> Question:
    """Вопрос с завершающим ответом"""
    question = Question.objects.create(
        text="Финальный вопрос?",
        updated_uuid="82345678-1234-1234-1234-123456789012",
    )

    # Создаем AnswerChoice без next_question (конец опроса)
    AnswerChoice.objects.create(
        current_question=question,
        next_question=None,  # Конец опроса
        answer="final_answer",
    )

    return question


@pytest.fixture
def survey_with_final_question(user, question_with_final_answer) -> Survey:
    """Опрос с финальным вопросом"""
    return Survey.objects.create(
        user=user,
        current_question=question_with_final_answer,
        status="new",
        result=[],
        questions_version_uuid="92345678-1234-1234-1234-123456789012",
    )


# Фикстуры для API Яндекс-диска

@pytest.fixture
def document(survey):
    """Фикстура для создания документа"""
    return Document.objects.create(survey=survey, image=TEST_IMAGE_URL)

@pytest.fixture
def document_factory(document):
    """Фабрика для создания документов"""
    def _factory(survey):
        return Document.objects.create(
            survey=survey,
            image=TEST_IMAGES_URLS.format(uuid4())
        )
    _factory.create_batch = lambda size, survey: [
        _factory(survey) for _ in range(size - 1)
    ]
    return _factory


@pytest.fixture
def mock_yandex_disk_uploader():
    """Фикстура для создания mock-объекта"""
    with patch('requests.get') as mock_get, \
            patch('requests.put') as mock_put:
        # mock-объект
        uploader_mock = MagicMock()
        # Поведение методов
        uploader_mock.get_upload_url.return_value = UPLOAD_URL
        uploader_mock.upload_file.return_value = DOWNLOAD_URL
        uploader_mock.get_download_url.return_value = DOWNLOAD_URL
        uploader_mock.check_file_exists.return_value = True
        # HTTP-запросы
        mock_response_upload = MagicMock()
        mock_response_upload.json.return_value = {'href': UPLOAD_URL}
        mock_response_upload.raise_for_status.return_value = None
        mock_response_download = MagicMock()
        mock_response_download.json.return_value = {'href': DOWNLOAD_URL}
        mock_response_download.raise_for_status.return_value = None
        mock_response_download.headers = {'Location': LOCATION}
        mock_response_put = MagicMock()
        mock_response_put.raise_for_status.return_value = None
        mock_response_put.headers = {'Location': LOCATION}
        mock_get.side_effect = [mock_response_upload, mock_response_download]
        mock_put.return_value = mock_response_put
        yield uploader_mock
