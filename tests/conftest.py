# conftest.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from questionnaire.models import Question, AnswerChoice, Survey

User = get_user_model()


TEST_QUESTION_1_TEXT = 'Тестовый вопрос?'
TEST_QUESTION_2_TEXT = "Следующий вопрос?"

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
        text=TEST_QUESTION_1_TEXT,
        updated_uuid="12345678-1234-1234-1234-123456789012",
        type='start_web'
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
        text=TEST_QUESTION_2_TEXT,
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
        # status="draft",
        # result=[],
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
        status="draft",
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
        status="draft",
        result=[],
        questions_version_uuid="92345678-1234-1234-1234-123456789012",
    )
