# test_surveys_update.py
import pytest

from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.test import APIClient

from questionnaire.models import Survey, Question, AnswerChoice
from questionnaire.constant import SurveyStatus


@pytest.mark.django_db
class TestSurveyUpdate:

    def test_update_survey_success(
        self,
        authenticated_client: APIClient,
        survey: Survey,
        answer_choice: AnswerChoice,
        question: Question,
        next_question: Question,
    ):
        """Тест успешного обновления опроса с ответом"""
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey.id},
        )
        data = {"answer": answer_choice.answer}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK
        assert response.data["id"] == str(survey.id)
        assert response.data.get("current_question_text") == next_question.text
        assert response.data.get("answers") == []

        # Проверяем обновление опроса в базе
        updated_survey = Survey.objects.get(id=survey.id)
        assert updated_survey.current_question == answer_choice.next_question
        assert len(updated_survey.result) == 2
        # question.text и answer_choice.answer
        assert updated_survey.result[0] == question.text
        assert updated_survey.result[1] == answer_choice.answer

    def test_update_survey_custom_answer(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест обновления опроса с пользовательским ответом"""
        # Создаем AnswerChoice с answer=None для пользовательского ответа
        next_question = Question.objects.create(
            text="Вопрос после пользовательского ответа",
            updated_uuid="42345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,  # Пользовательский ответ
        )

        url = reverse(
            "survey-detail",
            kwargs={"pk": survey.id},
        )
        data = {"answer": "мой_пользовательский_ответ"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        # Проверяем обновление опроса в базе
        updated_survey = Survey.objects.get(id=survey.id)
        assert updated_survey.current_question == next_question
        assert len(updated_survey.result) == 2
        assert updated_survey.result[1] == "мой_пользовательский_ответ"

    def test_update_survey_invalid_answer(
        self,
        authenticated_client,
        survey,
    ):
        """Тест обновления опроса с невалидным ответом"""
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey.id},
        )
        data = {"answer": "invalid_answer"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK
        # Должен вернуть тот же вопрос
        assert (
            "Некорректный ответ. Ответьте снова.\nТестовый вопрос?"
            == response.data["current_question_text"]
        )

        # Опрос не должен измениться
        unchanged_survey = Survey.objects.get(id=survey.id)
        assert unchanged_survey.current_question == survey.current_question
        assert unchanged_survey.result == survey.result

    def test_update_survey_missing_answer(self, authenticated_client, survey):
        """Тест обновления опроса без ответа"""
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey.id},
        )
        data = {"answer": None}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK
        assert (
            "Не передан ответ. Ответьте снова.\nТестовый вопрос?"
            == response.data["current_question_text"]
        )

    def test_update_survey_nonexistent_survey(self, authenticated_client):
        """Тест обновления несуществующего опроса"""
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": "12345678-1234-1234-1234-123456789999"},
        )
        data = {"answer": "test_answer"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_404_NOT_FOUND

    def test_update_survey_completion(
        self,
        authenticated_client: APIClient,
        survey: Survey,
    ):
        """Тест завершения опроса (когда next_question = None)"""
        # Создаем AnswerChoice без next_question для завершения
        AnswerChoice.objects.create(
            current_question=survey.current_question,
            next_question=None,  # Конец опроса
            answer="final_answer",
        )

        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey.id},
        )
        data = {"answer": "final_answer"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        # Проверяем, что опрос завершен
        completed_survey = Survey.objects.get(id=survey.id)
        assert completed_survey.current_question is None
        assert completed_survey.status == SurveyStatus.WAITING_DOCS.value
        assert len(completed_survey.result) == 2

    def test_update_survey_unauthenticated(self, api_client, survey):
        """Тест обновления опроса без аутентификации"""
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey.id},
        )
        data = {"answer": "test_answer"}

        response = api_client.put(url, data, format="json")

        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_update_survey_wrong_method(self, authenticated_client, survey):
        """Тест обновления опроса неправильным методом"""
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey.id},
        )
        data = {"answer": "test_answer"}

        # Пробуем POST вместо PUT
        response = authenticated_client.post(url, data, format="json")

        # Должен вернуть 405 Method Not Allowed
        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
