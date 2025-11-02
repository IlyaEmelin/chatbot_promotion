from uuid import UUID

import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)


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
    def test_processing_revert(self, authenticated_client, survey):
        """Тест успешного отката ответа из опроса, когда опрос пустой"""
        url = self.__get_url(survey.id)

        response = authenticated_client.patch(url)

        assert response.status_code == HTTP_200_OK

    @pytest.mark.django_db
    def test_processing_revert(self, authenticated_client, survey):
        """Тест успешного отката ответа из опроса, когда опрос не пустой"""
        url = self.__get_url(survey.id)

        response = authenticated_client.patch(url)

        assert response.status_code == HTTP_200_OK
