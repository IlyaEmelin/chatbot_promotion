# test_surveys_list.py
from time import sleep

import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
)
from questionnaire.models import Survey
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestSurveyList:
    """Тест на список опросов"""

    def test_list_surveys_success(
        self,
        authenticated_client: APIClient,
        survey: Survey,
    ):
        """Тест успешного получения списка опросов"""
        url = reverse("survey-list")

        response = authenticated_client.get(url)

        assert response.status_code == HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]["id"] == str(survey.id)
        assert "current_question_text" in response.data[0]
        assert "answers" in response.data[0]

    def test_list_surveys_empty(
        self,
        authenticated_client: APIClient,
        user,
    ):
        """Тест получения пустого списка опросов"""
        url = reverse("survey-list")

        response = authenticated_client.get(url)

        assert response.status_code == HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 0

    def test_list_surveys_multiple(
        self,
        authenticated_client: APIClient,
        user,
        question,
    ):
        """Тест получения списка с несколькими опросами"""
        # Создаем несколько опросов
        survey1 = Survey.objects.create(
            user=user,
            current_question=question,
            status="new",
            result=[],
            questions_version_uuid="12345678-1234-1234-1234-123456789012",
        )
        # Добавлена небольшая задержка для проверки порядка
        sleep(0.01)
        survey2 = Survey.objects.create(
            user=user,
            current_question=question,
            status="processing",
            result=[["Вопрос 1", "Ответ 1"]],
            questions_version_uuid="22345678-1234-1234-1234-123456789012",
        )

        url = reverse("survey-list")

        response = authenticated_client.get(url)

        assert response.status_code == HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 2

        # Проверяем, что опросы отсортированы по дате создания (новые first)
        survey_ids = [item["id"] for item in response.data]
        assert survey_ids == [str(survey2.id), str(survey1.id)]

    def test_list_surveys_only_current_user(
        self,
        authenticated_client: APIClient,
        user,
        question,
        api_client,
    ):
        """Тест, что пользователь видит только свои опросы"""
        # Создаем опрос для текущего пользователя
        user_survey = Survey.objects.create(
            user=user,
            current_question=question,
            status="new",
            result=[],
            questions_version_uuid="12345678-1234-1234-1234-123456789012",
        )

        # Создаем другого пользователя и его опрос
        other_user = user.__class__.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123",
        )
        other_survey = Survey.objects.create(
            user=other_user,
            current_question=question,
            status="new",
            result=[],
            questions_version_uuid="32345678-1234-1234-1234-123456789012",
        )

        url = reverse("survey-list")

        response = authenticated_client.get(url)

        assert response.status_code == HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]["id"] == str(user_survey.id)
        assert response.data[0]["id"] != str(other_survey.id)

    @pytest.mark.skip(
        reason="Временный пропуск Метод TODO @permission_classes([IsAuthenticated])"
    )
    def test_list_surveys_unauthenticated(
        self,
        api_client: APIClient,
        survey: Survey,
    ):
        """Тест получения списка опросов без аутентификации"""
        url = reverse("survey-list")

        response = api_client.get(url)

        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_list_surveys_filter_by_status(
        self,
        authenticated_client: APIClient,
        user,
        question,
    ):
        """Тест фильтрации опросов по статусу"""
        # Создаем опросы с разными статусами
        draft_survey = Survey.objects.create(
            user=user,
            current_question=question,
            status="new",
            result=[],
            questions_version_uuid="12345678-1234-1234-1234-123456789012",
        )

        processing_survey = Survey.objects.create(
            user=user,
            current_question=question,
            status="processing",
            result=[["Вопрос 1", "Ответ 1"]],
            questions_version_uuid="22345678-1234-1234-1234-123456789012",
        )

        completed_survey = Survey.objects.create(
            user=user,
            current_question=None,
            status="completed",
            result=[["Вопрос 1", "Ответ 1"], ["Вопрос 2", "Ответ 2"]],
            questions_version_uuid="32345678-1234-1234-1234-123456789012",
        )

        url = reverse("survey-list")

        # Фильтруем по массиву статусов
        response = authenticated_client.get(
            url,
            {"statuses": ["new", "processing"]},
        )
        assert response.status_code == HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 2
        survey_ids = {item["id"] for item in response.data}
        expected_ids = {str(draft_survey.id), str(processing_survey.id)}
        assert survey_ids == expected_ids

        # Фильтруем по другому массиву статусов
        response = authenticated_client.get(
            url,
            {"statuses": ["processing", "completed"]},
        )
        assert response.status_code == HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 2
        survey_ids = {item["id"] for item in response.data}
        expected_ids = {str(processing_survey.id), str(completed_survey.id)}
        assert survey_ids == expected_ids
