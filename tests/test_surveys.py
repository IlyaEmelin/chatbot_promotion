# test_surveys.py
import pytest

from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
)
from questionnaire.models import Survey


@pytest.mark.django_db
class TestSurveyCreate:

    def test_create1_survey_success(
        self, user, authenticated_client, question
    ):
        """Тест 1 успешного создания опроса"""
        url = reverse("create_survey")
        data = {"current_question": question.id}

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
        assert survey.status == "draft"
        assert survey.result == []

    def test_create2_survey_success(
        self,
        user,
        authenticated_client,
        answer_choice,
        question,
    ):
        """Тест 2 успешного создания опроса"""
        url = reverse("create_survey")
        data = {"current_question": question.id}

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
        assert survey.status == "draft"
        assert survey.result == []

    @pytest.mark.skip(
        reason="Временный пропуск Метод TODO @permission_classes([IsAuthenticated])"
    )
    def test_create_survey_unauthenticated(self, user, api_client, question):
        """Тест создания опроса без аутентификации"""
        url = reverse("create_survey")
        data = {"current_question": question.id}

        response = api_client.post(url, data, format="json")

        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_create_survey_missing_question_id(self, authenticated_client):
        """Тест создания опроса без question_id"""
        url = reverse("create_survey")
        data = {}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == HTTP_400_BAD_REQUEST

    def test_create_survey_invalid_question_id(self, authenticated_client):
        """Тест создания опроса с несуществующим current_question"""
        url = reverse("create_survey")
        data = {"current_question": 123}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == HTTP_400_BAD_REQUEST
