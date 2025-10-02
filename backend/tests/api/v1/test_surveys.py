# test_surveys.py
from pytest import mark, raises

from django.urls import reverse
from django.core.exceptions import ValidationError
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
)
from questionnaire.models import Survey


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
        assert response.data["id"] is not None
        assert response.data["current_question_text"] == question.text
        assert "answers" in response.data
        assert response.data["answers"] == []

        # Проверяем, что опрос создался в базе
        survey = Survey.objects.get(id=response.data["id"])
        assert survey.user == user
        assert survey.current_question == question
        assert survey.status == "new"
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
        assert response.data["id"] is not None
        assert response.data["current_question_text"] == question.text
        assert "answers" in response.data
        assert response.data["answers"] == ["test_answer"]

        # Проверяем, что опрос создался в базе
        survey = Survey.objects.get(id=response.data["id"])
        assert survey.user == user
        assert survey.current_question == question
        assert survey.status == "new"
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

        with raises(ValidationError) as exp:
            authenticated_client.post(url, data, format="json")

        assert (
            exp.value.message == "Не существует стартового вопроса для опроса."
        )
        assert exp.type == ValidationError
