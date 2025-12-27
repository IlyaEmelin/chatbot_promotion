# test_surveys.py
from typing import Any
from pytest import mark

from django.urls import reverse
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST,
)

from questionnaire.models import Survey
from questionnaire.constant import SurveyStatus


@mark.django_db
class TestSurveyCreate:

    def test_create1_survey_success(
        self,
        user,
        authenticated_client,
        question,
    ):
        """Тест 1 успешного создания опроса."""
        url = reverse("survey-list")
        data = {}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == HTTP_201_CREATED

        response_data = response.data
        assert len(response_data) == 5
        assert response_data["id"] is not None
        assert response_data["current_question_text"] == question.text
        assert response_data["answers"] == []
        assert response_data["result"] == []
        assert response_data["status"] == SurveyStatus.NEW.value

        # Проверяем, что опрос создался в базе
        survey: Survey = Survey.objects.get(id=response_data["id"])
        assert survey.user == user
        assert survey.current_question == question
        assert survey.status == SurveyStatus.NEW.value
        assert survey.result == []

    def test_create2_survey_success(
        self,
        user,
        authenticated_client,
        answer_choice,
        question,
    ):
        """Тест 2 успешного создания опроса."""
        url = reverse("survey-list")
        data = {}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == HTTP_201_CREATED

        response_data = response.data
        assert len(response_data) == 5
        assert response.data["id"] is not None
        assert response.data["current_question_text"] == question.text
        assert response.data["answers"] == ["вариант ответа"]
        assert response_data["result"] == []
        assert response_data["status"] == SurveyStatus.NEW.value

        # Проверяем, что опрос создался в базе
        survey = Survey.objects.get(id=response.data["id"])
        assert survey.user == user
        assert survey.current_question == question
        assert survey.status == SurveyStatus.NEW.value
        assert survey.result == []

    def test_create_survey_unauthenticated(self, user, api_client, question):
        """Тест создания опроса без аутентификации."""
        url = reverse("survey-list")
        data = {}

        response = api_client.post(url, data, format="json")

        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_create_survey_missing_question_id(self, authenticated_client):
        """Тест создания опроса без question_id"""
        url = reverse("survey-list")
        data = {}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == HTTP_400_BAD_REQUEST
        assert response.data == {
            "non_field_errors": [
                "Не существует стартового вопроса для опроса."
            ],
        }
