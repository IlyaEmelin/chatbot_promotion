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
    """Тест на список опросов."""

    def test_list_surveys_success(
        self,
        authenticated_client: APIClient,
        survey: Survey,
    ):
        """Тест успешного получения списка опросов админом"""
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
        question,
    ):
        """Тест получения пустого списка опросов"""
        url = reverse("survey-list")

        response = authenticated_client.get(url)

        assert response.status_code == HTTP_200_OK

        assert isinstance(response.data, list)
        assert len(response.data) == 1
        response_question = response.data[0]
        assert response_question["current_question_text"] == question.text
        assert response_question["status"] == "new"
        assert response_question["result"] == []
        assert response_question["answers"] == []

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

    def test_list_surveys_unauthenticated(
        self,
        api_client: APIClient,
        survey: Survey,
    ):
        """Тест получения списка опросов без аутентификации."""
        url = reverse("survey-list")

        response = api_client.get(url)

        assert response.status_code == HTTP_401_UNAUTHORIZED
