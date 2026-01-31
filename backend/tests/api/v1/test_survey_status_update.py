from uuid import uuid4, UUID

import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from django.contrib.auth import get_user_model
from questionnaire.constant import SurveyStatus

User = get_user_model()


class TestSurveyProcessing:
    """Тесты для метода processing SurveyViewSet"""

    @staticmethod
    def get_url(survey_id: UUID) -> str:
        """
        Получить url для смены статуса на в процессе

        Args:
            survey_id: uuid опроса

        Returns:
            str: url для смены статуса
        """
        return (
            reverse(
                viewname="survey-detail",
                kwargs={"pk": survey_id},
            )
            + "processing/"
        )

    @pytest.mark.django_db
    def test_processing_success(self, authenticated_client, survey):
        """Тест успешного изменения статуса опроса на <В обработке>"""
        url = self.get_url(survey.id)

        response = authenticated_client.patch(url)

        assert response.status_code == HTTP_200_OK
        survey.refresh_from_db()
        assert survey.status == SurveyStatus.SURVEY_COMPLETED.value

    @pytest.mark.django_db
    def test_processing_unauthorized(self, api_client, survey):
        """Тест доступа без аутентификации"""
        url = self.get_url(survey.id)

        response = api_client.patch(url)

        assert response.status_code == HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_processing_survey_not_found(self, authenticated_client):
        """Тест попытки изменить несуществующий опрос"""
        non_existent_id = uuid4()
        url = self.get_url(non_existent_id)

        response = authenticated_client.patch(url)

        assert response.status_code == HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_processing_wrong_http_method(self, authenticated_client, survey):
        """Тест использования неправильного HTTP метода"""
        url = self.get_url(survey.id)

        response_get = authenticated_client.get(url)
        assert response_get.status_code == HTTP_405_METHOD_NOT_ALLOWED

        response_post = authenticated_client.post(url)
        assert response_post.status_code == HTTP_405_METHOD_NOT_ALLOWED

        response_put = authenticated_client.put(url)
        assert response_put.status_code == HTTP_405_METHOD_NOT_ALLOWED

        response_del = authenticated_client.delete(url)
        assert response_del.status_code == HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.django_db
    def test_processing_already_in_progress(
        self, authenticated_client, survey
    ):
        """Тест изменения статуса опроса, который уже в обработке"""
        survey.status = SurveyStatus.SURVEY_COMPLETED.value
        survey.save()
        url = self.get_url(survey.id)

        response = authenticated_client.patch(url)

        assert response.status_code == HTTP_200_OK
        survey.refresh_from_db()
        assert survey.status == SurveyStatus.SURVEY_COMPLETED.value

    @pytest.mark.django_db
    def test_processing_different_users_surveys(
        self, authenticated_client, survey_other_user
    ):
        """Тест, что пользователь может изменять только свои опросы"""
        url = self.get_url(survey_other_user.id)

        response = authenticated_client.patch(url)

        assert response.status_code == HTTP_404_NOT_FOUND
