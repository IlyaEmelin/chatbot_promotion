from datetime import datetime
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


# user
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
def other_user() -> User:
    """
    Другой пользователь

    Returns:
        User: пользователь
    """
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="otherpass123",
    )


# client
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


# question
# полная структура вопросов
# Структура:
# Тестовый вопрос?
# ├─ вариант ответа → Второй вопрос?
# │  └─ вариант ответа → Третий вопрос? *
# └─ вариант по альтернативной ветке → Второй вопрос?
#    └─ вариант ответа → Третий вопрос? *
# * - идут в один и тот же вопрос в базе
# В структуре нет
# Финальный вопрос?
# Укажите номер телефона в формате +7ХХХХХХХХХХ?
@pytest.fixture
def question() -> Question:
    """
    Тестовый вопрос?

    Returns:
        Question: первый вопрос
    """
    return Question.objects.create(
        text="Тестовый вопрос?",
        updated_uuid="12345678-1234-1234-1234-123456789012",
        type="start",
        updated_at=datetime(2013, 1, 11),
    )


@pytest.fixture
def second_question() -> Question:
    """
    Второй вопрос?

    Returns:
        Question: второй вопрос
    """
    return Question.objects.create(
        text="Второй вопрос?",
        updated_uuid="42345678-1234-1234-1234-123456789013",
        updated_at=datetime(2013, 1, 12),
    )


@pytest.fixture
def second_alternative_question() -> Question:
    """
    Второй вопрос?

    Returns:
        Question: второй вопрос
    """
    return Question.objects.create(
        text="Второй вопрос?",
        updated_uuid="42111178-1234-1234-1234-555456789013",
        updated_at=datetime(2000, 10, 18),
    )


@pytest.fixture
def third_question() -> Question:
    """
    Третий вопрос?

    Returns:
        Question: третий вопрос
    """
    return Question.objects.create(
        text="Третий вопрос?",
        updated_uuid="42345678-3333-4444-1234-123456789013",
        updated_at=datetime(2013, 1, 1),
    )


@pytest.fixture
def question_with_final_answer() -> Question:
    """
    Вопрос с завершающим ответом

    Returns:
        Question: Вопрос с завершающим ответом
    """
    return Question.objects.create(
        text="Финальный вопрос?",
        updated_uuid="82345678-1234-1234-1234-123456789014",
        updated_at=datetime(1984, 10, 1),
    )


@pytest.fixture
def question_phone() -> Question:
    """
    Вопрос с запросом номера телефона

    Returns:
        Question: Вопрос с запросом номера телефона
    """
    return Question.objects.create(
        text="Укажите номер телефона в формате +7ХХХХХХХХХХ?",
        updated_uuid="82399978-1234-1234-1234-123457779014",
        external_table_field_name="User.phone_number",
    )


# answer choice
@pytest.fixture
def answer_choice(
    question: Question,
    second_question: Question,
) -> AnswerChoice:
    """
    Вариант ответа

    Args:
        question: первый вопрос
        second_question: второй вопрос

    Returns:
        AnswerChoice: вариант ответа
    """
    return AnswerChoice.objects.create(
        current_question=question,
        next_question=second_question,
        answer="вариант ответа",
    )


@pytest.fixture
def answer_alternative_choice(
    question: Question,
    second_alternative_question: Question,
) -> AnswerChoice:
    """
    Вариант по альтернативной ветке

    Args:
        question: первый вопрос
        second_alternative_question: вопрос по альтернативной ветке

    Returns:
        AnswerChoice: вариант по альтернативной ветке
    """
    return AnswerChoice.objects.create(
        current_question=question,
        next_question=second_alternative_question,
        answer="вариант по альтернативной ветке",
    )


@pytest.fixture
def answer_choice_final(question_with_final_answer: Question) -> AnswerChoice:
    """
    Вариант ответа финишного вопроса
    нет следующего вопроса

    Args:
        question_with_final_answer: Вопрос с завершающим ответом

    Returns:
        AnswerChoice:
    """
    # Создаем AnswerChoice без next_question (конец опроса)
    return AnswerChoice.objects.create(
        current_question=question_with_final_answer,
        next_question=None,  # Конец опроса
        answer="завершающий ответ",
    )


@pytest.fixture
def answer_choice_change_status(
    question: Question,
    second_question: Question,
) -> AnswerChoice:
    """
    Вариант ответа со сменой статуса

    Args:
        question: текущий вопрос
        second_question: следующий вопрос

    Returns:
        AnswerChoice: вариант ответа
    """
    return AnswerChoice.objects.create(
        current_question=question,
        next_question=second_question,
        answer="вариант ответа со сменой статуса",
        new_status=SurveyStatus.REJECTED.value,
    )


@pytest.fixture
def answer_choice_2to3(
    second_question: Question,
    third_question: Question,
) -> AnswerChoice:
    """
    Вариант ответа от второго к третьему вопросу

    Args:
        second_question: второй вопрос
        third_question: третий вопрос

    Returns:
        AnswerChoice: вариант ответа от второго к третьему вопросу
    """
    return AnswerChoice.objects.create(
        current_question=second_question,
        next_question=third_question,
        answer="вариант ответа от второго к третьему вопросу",
    )


@pytest.fixture
def answer_alternative_choice_2to3(
    second_alternative_question: Question,
    third_question: Question,
) -> AnswerChoice:
    """
    Вариант ответа от второго к третьему вопросу
    по альтернативной ветке

    Args:
        second_alternative_question: второй вопрос альтернативной ветки
        third_question: третий вопрос

    Returns:
        AnswerChoice: вариант ответа
    """
    return AnswerChoice.objects.create(
        current_question=second_alternative_question,
        next_question=third_question,
        answer="вариант ответа от второго к третьему вопросу",
    )


@pytest.fixture
def answer_choice_phone(
    question_phone: Question,
    second_question: Question,
) -> AnswerChoice:
    """
    Вариант ответа первый вопрос запрос номера телефона

    Args:
        question_phone: вопрос с запросом номера телефона
        second_question: второй вопрос

    Returns:
        AnswerChoice: вариант ответа
    """
    return AnswerChoice.objects.create(
        current_question=question_phone,
        next_question=second_question,
        answer=None,
    )


# survey
@pytest.fixture
def survey(user, question) -> Survey:
    """
    Получить опрос
    на этапе первого вопроса

    Структура опроса:
    - Тестовый вопрос?

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
        questions_version_uuid=question.updated_uuid,
        updated_at=question.updated_at,
    )


@pytest.fixture
def survey_with_custom_answer_start_step(
    user,
    question,
    second_question,
    answer_choice,
) -> Survey:
    """
    Опрос с вопросом, имеющим пользовательский ответ
    на этапе первого вопроса

    Структура опроса:
    - Тестовый вопрос?
        ** вариант ответа
        - Следующий вопрос?
    Args:
        user: пользователь
        question: 1-й вопрос с ответом
        second_question: 2-й следующий вопрос
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
        updated_at=question.updated_at,
    )


@pytest.fixture
def survey_with_custom_answer_second_step(
    user: User,
    question: Question,
    second_question: Question,
    answer_choice: AnswerChoice,
) -> Survey:
    """
    Опрос с вопросом, имеющим пользовательский ответ
    на этапе второго вопроса

    Структура опроса:
    - Тестовый вопрос?
        ** вариант ответа
        - Следующий вопрос?

    Args:
        user: пользователь
        question: 1-й вопрос с ответом
        second_question: 2-й следующий вопрос
        answer_choice: вариант ответа 1-й вопрос -> 2-й следующий вопрос

    Returns:
        Survey: опрос
    """
    return Survey.objects.create(
        user=user,
        current_question=second_question,
        status=SurveyStatus.NEW.value,
        result=[question.text, answer_choice.answer],
        questions_version_uuid=(
            UUID(
                int=question.updated_uuid.int
                ^ second_question.updated_uuid.int
            )
        ),
        updated_at=max(question.updated_at, second_question.updated_at),
    )


@pytest.fixture
def survey_with_custom_answer_second_step_reset(
    user: User,
    question: Question,
    second_question: Question,
    answer_choice: AnswerChoice,
) -> Survey:
    """
    Опрос с вопросом, имеющим пользовательский ответ
    на этапе не заданного вопроса

    Структура опроса:
    - Тестовый вопрос?
        ** вариант ответа
        - Второй вопрос?

    Args:
        user: пользователь
        question: 1-й вопрос с ответом
        second_question: 2-й следующий вопрос
        answer_choice: вариант ответа 1-й вопрос -> 2-й следующий вопрос

    Returns:
        Survey: опрос
    """
    return Survey.objects.create(
        user=user,
        current_question=None,
        status=SurveyStatus.NEW.value,
        result=[question.text, answer_choice.answer],
        questions_version_uuid=(
            UUID(
                int=question.updated_uuid.int
                ^ second_question.updated_uuid.int
            )
        ),
        updated_at=max(question.updated_at, second_question.updated_at),
    )


@pytest.fixture
def survey_other_user(other_user, question) -> Survey:
    """
    Получить опрос от другого пользователя
    на этапе первого вопроса

    Структура опроса:
    - Тестовый вопрос?

    Args:
        other_user: пользовательl
        question: первый вопрос

    Returns:
        Survey: опрос
    """
    return Survey.objects.create(
        user=other_user,
        current_question=question,
        status=SurveyStatus.NEW.value,
        result=[],
        questions_version_uuid=question.updated_uuid,
        updated_at=question.updated_at,
    )


@pytest.fixture
def survey_with_final_question(
    user: User,
    question_with_final_answer: Question,
    answer_choice_final: AnswerChoice,
) -> Survey:
    """
    Опрос с финальным вопросом

    Args:
        user: пользователь
        question_with_final_answer: финальный вопрос
        answer_choice_final: финальный вариант ответа

    Returns:
        Survey: опрос с финальным вопросом
    """
    return Survey.objects.create(
        user=user,
        current_question=question_with_final_answer,
        status=SurveyStatus.NEW.value,
        result=[],
        questions_version_uuid=question_with_final_answer.updated_uuid,
        updated_at=question_with_final_answer.updated_at,
    )


@pytest.fixture
def survey_with_change_status_question(
    user: User,
    question: Question,
    second_question: Question,
    answer_choice_change_status: AnswerChoice,
    third_question: Question,
    answer_choice_2to3: AnswerChoice,
) -> Survey:
    """
    Опрос со сменой статуса

    Структура опроса:
    - Тестовый вопрос?
        ** вариант ответа со сменой статуса
        - Второй вопрос?
            ** вариант ответа от второго к третьему вопросу
            -Третий вопрос?

    Args:
        user: пользователь
        question: текущий вопрос
        second_question: второй вопрос
        answer_choice_change_status: ответ со сменой статуса
        third_question: третий вопрос
        answer_choice_2to3: ответ от второго к третьему вопросу

    Returns:
        Survey: опрос
    """
    return Survey.objects.create(
        user=user,
        current_question=question,
        status=SurveyStatus.NEW.value,
        result=[],
        questions_version_uuid=question.updated_uuid,
        updated_at=question.updated_at,
    )


@pytest.fixture
def survey_with_save_last_status_question(
    user: User,
    question: Question,
    second_question: Question,
    answer_choice: AnswerChoice,
    third_question: Question,
    answer_choice_2to3: AnswerChoice,
) -> Survey:
    """
    Опрос со сохранением старого статуса

    Структура опроса:
    - Тестовый вопрос?
        ** вариант ответа со сменой статуса
        - Второй вопрос?
            ** вариант ответа от второго к третьему вопросу
            -Третий вопрос?

    Args:
        user: пользователь
        question: текущий вопрос
        second_question: второй вопрос
        answer_choice: ответ
        third_question: третий вопрос
        answer_choice_2to3: ответ от второго к третьему вопросу

    Returns:
        Survey: опрос
    """
    return Survey.objects.create(
        user=user,
        current_question=question,
        status=SurveyStatus.REJECTED.value,
        result=[],
        questions_version_uuid=question.updated_uuid,
        updated_at=question.updated_at,
    )


@pytest.fixture
def survey_question_phone(
    user: User,
    question_phone: Question,
    second_question: Question,
    answer_choice_phone: AnswerChoice,
) -> Survey:
    """
    Опрос со сохранением старого статуса

    Структура опроса:
    - Укажите номер телефона в формате +7ХХХХХХХХХХ?
        ** None
        - Второй вопрос?

    Args:
        user: пользователь
        question_phone: текущий вопрос
        second_question: второй вопрос
        answer_choice_phone: ответ

    Returns:
        Survey: опрос
    """
    return Survey.objects.create(
        user=user,
        current_question=question_phone,
        status=SurveyStatus.NEW.value,
        result=[],
        questions_version_uuid=question_phone.updated_uuid,
        updated_at=question_phone.updated_at,
    )


@pytest.fixture
def survey_question_2_to3(
    user: User,
    question: Question,
    second_question: Question,
    second_alternative_question: Question,
    third_question: Question,
    answer_choice: AnswerChoice,
    answer_choice_2to3: AnswerChoice,
    answer_alternative_choice_2to3: AnswerChoice,
) -> Survey:
    """
    Сложная структура опросов на этапе третьего вопроса

    Структура опроса:
    Структура:
    Тестовый вопрос?
    ├─ вариант ответа → Второй вопрос?
    │  └─ вариант ответа → Третий вопрос?
    └─ вариант по альтернативной ветке → Второй альтернативный вопрос?
       └─ вариант ответа → Третий вопрос?

    Args:
        user:
        question: первый вопрос
        second_question: Второй вопрос?
        second_alternative_question: второй альтернативный вопрос?
        third_question: Третий вопрос?
        answer_choice: вариант ответа
        answer_choice_2to3: вариант ответа от второго к третьему вопросу
        answer_alternative_choice_2to3: вариант ответа от второго
            к третьему вопросу

    Returns:
        Survey: опрос
    """
    return Survey.objects.create(
        user=user,
        current_question=third_question,
        status=SurveyStatus.WAITING_DOCS.value,
        result=[
            question.text,
            answer_choice.answer,
            second_question.text,
            answer_choice_2to3.answer,
        ],
        questions_version_uuid=(
            UUID(
                int=question.updated_uuid.int
                ^ second_question.updated_uuid.int
                ^ third_question.updated_uuid.int
            )
        ),
        updated_at=max(
            question.updated_at,
            second_question.updated_at,
            third_question.updated_at,
        ),
    )


# Фикстуры для API Яндекс-диска
@pytest.fixture
def document(survey):
    """Фикстура для создания документа"""
    return Document.objects.create(survey=survey, image=TEST_IMAGE_URL)


@pytest.fixture
def document_factory():
    """Фабрика для создания документов"""

    def _factory(survey):
        return Document.objects.create(
            survey=survey, image=TEST_IMAGES_URLS.format(uuid4())
        )

    def _create_batch(size, survey):
        return [_factory(survey) for _ in range(size)]

    _factory.create_batch = _create_batch
    return _factory


patch_path = "common.utils.yadisk.requests"


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

        # side_effect как функция, чтобы не падать при >2 вызовах
        def get_side_effect(url, *args, **kwargs):
            if "upload" in url:
                return mock_response_upload
            return mock_response_download

        mock_get.side_effect = get_side_effect
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
