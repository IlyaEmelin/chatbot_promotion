# conftest.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from questionnaire.models import Question, AnswerChoice, Survey

User = get_user_model()


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
        last_question=question,
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
        status="draft",
        result=[],
        questions_version_uuid="32345678-1234-1234-1234-123456789012",
    )
