from uuid import UUID

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from questionnaire.constant import SurveyStatus
from questionnaire.models import Survey, Question


class TestSurveyRevert:
    """
    Тестирование отмены ответа по последни во
    """

    @staticmethod
    def __get_url(survey_id: UUID):
        """
        Получить url для ссылки отмены ответа в опросе

        Args:
            survey_id: идентификатор UUID опроса

        Returns:
            str: url для отмены
        """
        return (
            reverse(
                viewname="survey-detail",
                kwargs={"pk": survey_id},
            )
            + "revert/"
        )

    @pytest.mark.django_db
    def test_processing_revert(
        self,
        authenticated_client: APIClient,
        survey: Survey,
        question: Question,
    ):
        """Тест успешного отката ответа из опроса, когда опрос пустой"""
        url = self.__get_url(survey.id)

        response = authenticated_client.patch(url)

        assert response.status_code == HTTP_200_OK

        survey.refresh_from_db()
        assert survey.current_question == question
        assert survey.result == []
        assert survey.status == SurveyStatus.NEW.value
        assert survey.questions_version_uuid == question.updated_uuid
        assert survey.updated_at == question.updated_at

    @pytest.mark.django_db
    def test_processing_revert(
        self,
        authenticated_client,
        survey_with_custom_answer_second_step,
        question: Question,
        next_question: Question,
    ):
        """Тест успешного отката ответа из опроса, когда опрос не пустой"""
        url = self.__get_url(survey_with_custom_answer_second_step.id)

        response = authenticated_client.patch(url)

        assert response.status_code == HTTP_200_OK

        survey_with_custom_answer_second_step.refresh_from_db()
        assert (
            survey_with_custom_answer_second_step.current_question == question
        )
        assert survey_with_custom_answer_second_step.result == []
        assert (
            survey_with_custom_answer_second_step.status
            == SurveyStatus.NEW.value
        )
        assert (
            survey_with_custom_answer_second_step.questions_version_uuid
            == question.updated_uuid
        )
        # TODO updated_at пока не обновляет так как
        #  нам придется пробежать все вопросы включая новый текущий
        assert (
            survey_with_custom_answer_second_step.updated_at
            == next_question.updated_at
        )
