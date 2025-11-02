# conftest.py
from uuid import uuid4, UUID

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from questionnaire.models import (
    Question,
    AnswerChoice,
    Survey,
    Document,
    Comment,
)
from unittest.mock import patch, MagicMock
import pytest

from questionnaire.constant import SurveyStatus

User = get_user_model()


UPLOAD_URL = "https://mock-upload.url/test.png"
DOWNLOAD_URL = "https://mock-download.url/test.png"
LOCATION = "https://disk.yandex.ru/disk/test.png"
TEST_IMAGE_URL = "https://example.com/test.jpg"
TEST_IMAGES_URLS = "https://example.com/{}.jpg"


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
def next_question() -> Question:
    """
    Следующий вопрос

    Returns:
        Question: следующий вопрос
    """

    return Question.objects.create(
        text="Следующий вопрос?",
        updated_uuid="42345678-1234-1234-1234-123456789013",
    )


@pytest.fixture
def answer_choice(question: Question, next_question: Question) -> AnswerChoice:
    """
    Второй вопрос

    Args:
        question: первый вопрос
        next_question: второй вопрос

    Returns:
        AnswerChoice: вариант ответа
    """
    return AnswerChoice.objects.create(
        current_question=question,
        next_question=next_question,
        answer="вариант ответа",
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
        status=SurveyStatus.NEW.value,
        result=[],
        questions_version_uuid="32345678-1234-1234-1234-123456789012",
    )


@pytest.fixture
def survey_with_custom_answer_start_step(
    user,
    question,
    next_question,
    answer_choice,
) -> Survey:
    """
    Опрос с вопросом, имеющим пользовательский ответ
    на этапе первого вопроса

    Args:
        user: пользователь
        question: 1-й вопрос с ответом
        next_question: 2-й следующий вопрос
        answer_choice: вариант ответа 1-й вопрос -> 2-й следующий вопрос

    Returns:
        Survey: опрос
    """
    return Survey.objects.create(
        user=user,
        current_question=question,
        status=SurveyStatus.NEW.value,
        result=[],
        questions_version_uuid=question.updated_uuid,
    )


@pytest.fixture
def survey_with_custom_answer_second_step(
    user,
    question: Question,
    next_question: Question,
    answer_choice: AnswerChoice,
) -> Survey:
    """
    Опрос с вопросом, имеющим пользовательский ответ
    на этапе второго вопроса

    Args:
        user: пользователь
        question: 1-й вопрос с ответом
        next_question: 2-й следующий вопрос
        answer_choice: вариант ответа 1-й вопрос -> 2-й следующий вопрос

    Returns:
        Survey: опрос
    """
    return Survey.objects.create(
        user=user,
        current_question=next_question,
        status=SurveyStatus.NEW.value,
        result=[question.text, answer_choice.answer],
        questions_version_uuid=(
            UUID(
                int=question.updated_uuid.int ^ next_question.updated_uuid.int
            )
        ),
        updated_at=max(question.updated_at, next_question.updated_at),
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
        status=SurveyStatus.NEW.value,
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
            survey=survey, image=TEST_IMAGES_URLS.format(uuid4())
        )

    _factory.create_batch = lambda size, survey: [
        _factory(survey) for _ in range(size)
    ]
    return _factory


patch_path = "api.yadisk.requests"


@pytest.fixture
def mock_yandex_disk_uploader():
    """Фикстура для создания mock-объекта"""
    with (
        patch(f"{patch_path}.get") as mock_get,
        patch(f"{patch_path}.put") as mock_put,
    ):
        # Настройка mock-ответов
        mock_response_upload = MagicMock()
        mock_response_upload.json.return_value = {"href": UPLOAD_URL}
        mock_response_upload.raise_for_status.return_value = None

        mock_response_download = MagicMock()
        mock_response_download.json.return_value = {"href": DOWNLOAD_URL}
        mock_response_download.raise_for_status.return_value = None
        mock_response_download.headers = {"Location": LOCATION}

        mock_response_put = MagicMock()
        mock_response_put.raise_for_status.return_value = None
        mock_response_put.headers = {"Location": LOCATION}

        # Настройка side_effect для последовательных вызовов
        mock_get.side_effect = [mock_response_upload, mock_response_download]
        mock_put.return_value = mock_response_put
        yield {
            "mock_get": mock_get,
            "mock_put": mock_put,
            "mock_response_upload": mock_response_upload,
            "mock_response_download": mock_response_download,
            "mock_response_put": mock_response_put,
        }


# Фикстуры для комментариев


@pytest.fixture
def admin_user():
    """Создание администратора"""
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        is_staff=True,
    )


@pytest.fixture
def authenticated_admin(api_client, admin_user):
    """Получить аутентифицированного админа"""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def comment(survey, admin_user):
    """Создание комментария"""
    return Comment.objects.create(
        survey=survey, user=admin_user, text="Test comment text"
    )


@pytest.fixture
def comment_data():
    """Данные для создания комментария"""
    return {"text": "New test comment"}
