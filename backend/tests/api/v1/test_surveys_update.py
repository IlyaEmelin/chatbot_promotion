# test_surveys_update.py
import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.test import APIClient

from questionnaire.models import Survey, Question, AnswerChoice
from questionnaire.constant import SurveyStatus

User = get_user_model()


@pytest.mark.django_db
class TestSurveyUpdate:
    """
    Тест обновления опроса
    """

    def test_update_survey_success(
        self,
        authenticated_client: APIClient,
        survey_with_custom_answer_start_step: Survey,
        answer_choice: AnswerChoice,
        question: Question,
        second_question: Question,
    ) -> None:
        """
        Тест успешного обновления опроса с ответом

        Args:
            authenticated_client: авторизованный клиент
            survey_with_custom_answer_start_step: опрос
            answer_choice: вариант ответа
            question: текущий вопрос
            next_question: следующий вопрос
        """
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey_with_custom_answer_start_step.id},
        )
        data = {"answer": answer_choice.answer}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        response_data = response.data
        assert len(response_data) == 5
        assert response_data["id"] == str(
            survey_with_custom_answer_start_step.id
        )
        assert (
            response_data.get("current_question_text") == second_question.text
        )
        assert response_data.get("answers") == []
        assert response_data.get("result") == [
            question.text,
            answer_choice.answer,
        ]
        assert response_data.get("status") == SurveyStatus.WAITING_DOCS.value

        # Проверяем обновление опроса в базе
        updated_survey = Survey.objects.get(
            id=survey_with_custom_answer_start_step.id
        )
        assert updated_survey.current_question == answer_choice.next_question
        assert len(updated_survey.result) == 2
        # question.text и answer_choice.answer
        assert updated_survey.result == [question.text, answer_choice.answer]

    def test_update_survey_success_reset(
        self,
        authenticated_client: APIClient,
        survey_with_custom_answer_second_step_reset: Survey,
        answer_choice: AnswerChoice,
        question: Question,
        second_question: Question,
    ) -> None:
        """
        Опрос с вопросом, имеющий пользовательский ответ
        на этапе не заданного вопроса

        Структура опроса:
        - Тестовый вопрос?
            ** вариант ответа
            - Следующий вопрос?

        Args:
            authenticated_client: авторизованный клиент
            survey_with_custom_answer_second_step_reset: опрос
            answer_choice: вариант ответа
            question: текущий вопрос
            second_question: следующий вопрос
        """
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey_with_custom_answer_second_step_reset.id},
        )
        data = {"answer": answer_choice.answer}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        response_data = response.data
        assert len(response_data) == 5
        assert response_data["id"] == str(
            survey_with_custom_answer_second_step_reset.id
        )
        assert (
            response_data.get("current_question_text") == second_question.text
        )
        assert response_data.get("answers") == []
        assert response_data.get("result") == [
            question.text,
            answer_choice.answer,
        ]
        assert response_data.get("status") == SurveyStatus.WAITING_DOCS.value

        updated_survey = Survey.objects.get(
            id=survey_with_custom_answer_second_step_reset.id
        )
        assert updated_survey.current_question == answer_choice.next_question
        assert len(updated_survey.result) == 2
        assert updated_survey.result == [question.text, answer_choice.answer]

    def test_update_survey_change_status_question(
        self,
        authenticated_client: APIClient,
        survey_with_change_status_question: Survey,
        question: Question,
        second_question: Question,
        answer_choice_change_status: AnswerChoice,
        third_question: Question,
        answer_choice_2to3: AnswerChoice,
    ) -> None:
        """
        Опрос со сменой статуса

        Структура опроса:
        - Тестовый вопрос?
            ** вариант ответа со сменой статуса
            - Второй вопрос?
                ** вариант ответа от второго к третьему вопросу
                -Третий вопрос?

        Args:
            authenticated_client: аутентифицированный клиент
            survey_with_change_status_question: опрос со сменой статуса
            question: стартовый вопрос
            second_question: второй вопрос
            answer_choice_change_status: ответ со сменой статуса
            third_question: третий вопрос
            answer_choice_2to3: ответ от 2-го к 3-му вопросу
        """
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey_with_change_status_question.id},
        )
        data = {"answer": answer_choice_change_status.answer}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        response_data_change_status = response.data
        assert len(response_data_change_status) == 5
        assert response_data_change_status["id"] == str(
            survey_with_change_status_question.id
        )
        assert (
            response_data_change_status.get("current_question_text")
            == second_question.text
        )
        assert response_data_change_status.get("answers") == [
            answer_choice_2to3.answer
        ]
        assert response_data_change_status.get("result") == [
            question.text,
            answer_choice_change_status.answer,
        ]
        assert (
            response_data_change_status.get("status")
            == SurveyStatus.REJECTED.value
        )

        updated_survey = Survey.objects.get(
            id=survey_with_change_status_question.id
        )
        assert updated_survey.current_question == second_question
        assert len(updated_survey.result) == 2
        assert updated_survey.result == [
            question.text,
            answer_choice_change_status.answer,
        ]
        assert updated_survey.status == SurveyStatus.REJECTED.value

    def test_update_survey_save_last_status_question(
        self,
        authenticated_client: APIClient,
        survey_with_save_last_status_question: Survey,
        question: Question,
        second_question: Question,
        answer_choice: AnswerChoice,
        third_question: Question,
        answer_choice_2to3: AnswerChoice,
    ) -> None:
        """
        Опрос со сохранением старого статуса

        Структура опроса:
        - Тестовый вопрос?
            ** вариант ответа со сменой статуса
            - Второй вопрос?
                ** вариант ответа от второго к третьему вопросу
                -Третий вопрос?

        Args:
            authenticated_client: аутентифицированный клиент
            survey_with_save_last_status_question: опрос сохранением
                старого статуса
            question: стартовый вопрос
            second_question: второй вопрос
            answer_choice: ответ от 1-го к 2-му вопросу
            third_question: третий вопрос
            answer_choice_2to3: ответ от 2-го к 3-му вопросу
        """
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey_with_save_last_status_question.id},
        )
        data = {"answer": answer_choice.answer}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        response_data_save_status = response.data
        assert response_data_save_status["id"] == str(
            survey_with_save_last_status_question.id
        )
        assert (
            response_data_save_status.get("current_question_text")
            == second_question.text
        )
        assert response_data_save_status.get("answers") == [
            answer_choice_2to3.answer
        ]
        assert response_data_save_status.get("result") == [
            question.text,
            answer_choice.answer,
        ]
        assert (
            response_data_save_status.get("status")
            == SurveyStatus.REJECTED.value
        )

        updated_survey = Survey.objects.get(
            id=survey_with_save_last_status_question.id
        )
        assert updated_survey.current_question == second_question
        assert len(updated_survey.result) == 2
        assert updated_survey.result == [
            question.text,
            answer_choice.answer,
        ]
        assert updated_survey.status == SurveyStatus.REJECTED.value

    def test_update_survey_custom_answer(
        self,
        authenticated_client,
        survey,
        question,
        second_question,
        answer_choice_user_set,
    ) -> None:
        """Тест обновления опроса с пользовательским ответом"""
        url = reverse(
            "survey-detail",
            kwargs={"pk": survey.id},
        )
        data = {"answer": "мой_пользовательский_ответ"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK
        response_data = response.data
        assert len(response_data) == 5
        assert response_data["id"] == str(survey.id)
        assert (
            response_data.get("current_question_text") == second_question.text
        )
        assert response_data.get("answers") == []
        assert response_data.get("result") == [
            question.text,
            "мой_пользовательский_ответ",
        ]
        assert response_data.get("status") == SurveyStatus.WAITING_DOCS.value

        # Проверяем обновление опроса в базе
        updated_survey = Survey.objects.get(id=survey.id)
        assert updated_survey.current_question == second_question
        assert len(updated_survey.result) == 2
        assert updated_survey.result == [
            "Тестовый вопрос?",
            "мой_пользовательский_ответ",
        ]

    def test_update_survey_with_final_question(
        self,
        authenticated_client: APIClient,
        survey_with_final_question: Survey,
        question_with_final_answer: Question,
        answer_choice_final: AnswerChoice,
    ) -> None:
        """
        Тест обновления опроса для финального вопроса

        Args:
            authenticated_client: авторизованный клиент
            survey_with_final_question: финальный опрос
            question_with_final_answer: вопрос финального опроса
            answer_choice_final: финальный вариант ответа
        """
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey_with_final_question.id},
        )
        data = {"answer": answer_choice_final.answer}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        response_data = response.data
        assert len(response_data) == 5
        assert response_data["id"] == str(survey_with_final_question.id)
        assert response_data.get("current_question_text") is None
        assert response_data.get("answers") == []
        assert response_data.get("result") == [
            question_with_final_answer.text,
            answer_choice_final.answer,
        ]
        assert response_data.get("status") == SurveyStatus.WAITING_DOCS.value

        updated_survey = Survey.objects.get(id=survey_with_final_question.id)
        assert updated_survey.current_question is None
        assert len(updated_survey.result) == 2
        assert updated_survey.result == [
            question_with_final_answer.text,
            answer_choice_final.answer,
        ]

    def test_update_survey_question_phone(
        self,
        user: User,
        authenticated_client: APIClient,
        survey_question_phone: Survey,
        question_phone: Question,
        second_question: Question,
        answer_choice_phone: AnswerChoice,
    ) -> None:
        """
        Тест сохранения телефона в пользователя

        Args:
            user: пользователь
            authenticated_client: авторизованный клиент
            survey_question_phone: опрос со сохранением старого статуса
            question_phone:  Вопрос с запросом номера телефона
            second_question: Второй вопрос
            answer_choice_phone: вариант ответа телефона с номером телефона
        """
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey_question_phone.id},
        )
        new_phone_number = "+79206548807"
        data = {"answer": new_phone_number}

        response_set_phone = authenticated_client.put(url, data, format="json")

        assert response_set_phone.status_code == HTTP_200_OK

        response_data = response_set_phone.data
        assert response_data["id"] == str(survey_question_phone.id)
        assert (
            response_data.get("current_question_text") == second_question.text
        )
        assert response_data.get("answers") == []
        assert response_data.get("result") == [
            question_phone.text,
            new_phone_number,
        ]
        assert response_data.get("status") == SurveyStatus.WAITING_DOCS.value

        updated_survey = Survey.objects.get(id=survey_question_phone.id)
        assert updated_survey.current_question == second_question
        assert len(updated_survey.result) == 2
        assert updated_survey.result == [
            question_phone.text,
            new_phone_number,
        ]

        user.refresh_from_db()
        assert user.phone_number == new_phone_number

    def test_update_survey_question_phone2(
        self,
        user: User,
        authenticated_client: APIClient,
        survey_question_phone: Survey,
        question_phone: Question,
        second_question: Question,
        answer_choice_phone: AnswerChoice,
    ) -> None:
        """
        Тест сохранения не корректного телефона

        Args:
            user: пользователь
            authenticated_client: авторизованный клиент
            survey_question_phone: опрос со сохранением старого статуса
            question_phone:  Вопрос с запросом номера телефона
            second_question: Второй вопрос
            answer_choice_phone: вариант ответа телефона с номером телефона
        """
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey_question_phone.id},
        )
        new_phone_number = "724433"
        data = {"answer": new_phone_number}

        response_set_phone = authenticated_client.put(url, data, format="json")

        assert response_set_phone.status_code == HTTP_400_BAD_REQUEST
        assert response_set_phone.data == {
            "phone_number": ["Укажите номер в формате: +7ХХХХХХХХХХ"]
        }

        updated_survey = Survey.objects.get(id=survey_question_phone.id)
        assert updated_survey.current_question == question_phone
        assert updated_survey.result == []

        user.refresh_from_db()
        assert user.phone_number is None

    def test_update_survey_invalid_answer(
        self,
        authenticated_client,
        survey_with_custom_answer_start_step,
        answer_choice,
    ):
        """Тест обновления опроса с невалидным ответом"""
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey_with_custom_answer_start_step.id},
        )
        data = {"answer": "invalid_answer"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        response_data = response.data
        assert len(response_data) == 5
        assert response_data["id"] == str(
            survey_with_custom_answer_start_step.id
        )
        assert (
            response.data["current_question_text"]
            == "Некорректный ответ. Ответьте снова.\nТестовый вопрос?"
        )
        assert response_data.get("answers") == [answer_choice.answer]
        assert response_data.get("result") == []
        assert response_data.get("status") == SurveyStatus.NEW.value

        # Опрос не должен измениться
        unchanged_survey = Survey.objects.get(
            id=survey_with_custom_answer_start_step.id
        )
        assert (
            unchanged_survey.current_question
            == survey_with_custom_answer_start_step.current_question
        )
        assert (
            unchanged_survey.result
            == survey_with_custom_answer_start_step.result
        )

    def test_update_survey_missing_answer(
        self,
        authenticated_client,
        survey_with_custom_answer_second_step_reset,
        question,
        second_question,
        answer_choice,
    ):
        """Тест обновления опроса без ответа"""
        url = reverse(
            viewname="survey-detail",
            kwargs={"pk": survey_with_custom_answer_second_step_reset.id},
        )
        data = {"answer": None}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        response_data = response.data
        assert len(response_data) == 5
        assert response_data["id"] == str(
            survey_with_custom_answer_second_step_reset.id
        )
        assert (
            response.data["current_question_text"]
            == "Не передан ответ. Ответьте снова.\nТестовый вопрос?"
        )
        assert response_data.get("answers") == [answer_choice.answer]
        assert response_data.get("result") == []
        assert response_data.get("status") == SurveyStatus.NEW.value

        updated_survey = Survey.objects.get(
            id=survey_with_custom_answer_second_step_reset.id
        )
        assert updated_survey.current_question == question
        assert updated_survey.result == []

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
        question: Question,
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
        assert completed_survey.result == [question.text, "final_answer"]

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
