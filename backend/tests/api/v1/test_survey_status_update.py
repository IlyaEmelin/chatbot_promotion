import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from questionnaire.models import Survey
from questionnaire.constant import SurveyStatus

User = get_user_model()


class TestSurveyProcessing:
    """Тесты для метода processing SurveyViewSet"""

    other_user_data = {
        "username": "otheruser",
        "email": "other@example.com",
        "password": "otherpass123",
    }

    @staticmethod
    def get_url(survey_id):
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
        assert response.status_code == status.HTTP_200_OK
        survey.refresh_from_db()
        assert survey.status == SurveyStatus.PROCESSING.value

    @pytest.mark.django_db
    def test_processing_unauthorized(self, api_client, survey):
        """Тест доступа без аутентификации"""
        url = self.get_url(survey.id)
        response = api_client.patch(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_processing_survey_not_found(self, authenticated_client):
        """Тест попытки изменить несуществующий опрос"""
        non_existent_id = uuid.uuid4()
        url = self.get_url(non_existent_id)
        response = authenticated_client.patch(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_processing_wrong_http_method(self, authenticated_client, survey):
        """Тест использования неправильного HTTP метода"""
        url = self.get_url(survey.id)
        response_get = authenticated_client.get(url)
        assert response_get.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        response_post = authenticated_client.post(url)
        assert response_post.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        response_put = authenticated_client.put(url)
        assert response_put.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        response_del = authenticated_client.delete(url)
        assert response_del.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.django_db
    def test_processing_already_in_progress(
        self, authenticated_client, survey
    ):
        """Тест изменения статуса опроса, который уже в обработке"""
        survey.status = SurveyStatus.PROCESSING.value
        survey.save()
        url = self.get_url(survey.id)
        response = authenticated_client.patch(url)
        assert response.status_code == status.HTTP_200_OK
        survey.refresh_from_db()
        assert survey.status == SurveyStatus.PROCESSING.value

    @pytest.mark.django_db
    def test_processing_different_users_surveys(
        self, authenticated_client, question
    ):
        """Тест, что пользователь может изменять только свои опросы"""
        other_user = User.objects.create_user(**self.other_user_data)
        other_user_survey = Survey.objects.create(
            user=other_user,
            current_question=question,
            status=SurveyStatus.NEW.value,
            result=[],
            questions_version_uuid=uuid.uuid4(),
        )
        url = self.get_url(other_user_survey.id)
        response = authenticated_client.patch(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
