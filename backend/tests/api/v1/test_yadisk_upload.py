from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework import status

from questionnaire.models import Document


@pytest.mark.django_db
class TestDocumentViewSet:
    """Тесты для DocumentViewSet с mock YandexDiskUploader"""

    base64_image = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAA"
        "AADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    )
    base64_prefix = "data:image/png;base64,"
    invalid_image = f"{base64_prefix},invalid_base64_data"
    download_url = "https://mock-download.url/test.png"
    list_view_name = "document-list"
    detail_view_kwargs = staticmethod(lambda x, y: {"survey_pk": x, "pk": y})
    list_view_kwargs = staticmethod(lambda x: {"survey_pk": x})
    data_image = staticmethod(lambda x: {"image": x})
    invalid_pk_kwargs = {"survey_pk": uuid4()}

    def test_create_document_with_base64_image(
            self, authenticated_client, mock_yandex_disk_uploader, survey
    ):
        """Тест создания документа с base64 изображением"""
        initial_count = Document.objects.count()
        image_data = f'{self.base64_prefix}{self.base64_image}'
        url = reverse(self.list_view_name, kwargs=self.list_view_kwargs(survey.pk))
        data = self.data_image(image_data)

        response = authenticated_client.post(url, data, format='json')
        new_record = Document.objects.latest('id')

        assert response.status_code == status.HTTP_201_CREATED
        assert "image" in response.data
        assert response.data["image"] == self.download_url
        assert Document.objects.count() == initial_count + 1
        assert new_record.survey == survey
        assert new_record.image == self.download_url
        mock_yandex_disk_uploader["mock_get"].assert_called()
        mock_yandex_disk_uploader["mock_put"].assert_called()

    def test_create_document_invalid_base64(self, authenticated_client, survey):
        """Тест создания документа с невалидным base64"""
        url = reverse(self.list_view_name, kwargs=self.list_view_kwargs(survey.pk))
        data = self.data_image(self.invalid_image)

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'image' in response.data

    def test_user_list_documents(
            self, authenticated_client, survey, document_factory
    ):
        """Тест получения списка документов обычным пользователем"""
        document_factory.create_batch(3, survey=survey)
        url = reverse(self.list_view_name, kwargs=self.list_view_kwargs(survey.pk))

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4

    def test_admin_list_documents(
            self, authenticated_admin, survey, document_factory
    ):
        """Тест получения списка документов админом"""
        document_factory.create_batch(3, survey=survey)
        url = reverse(self.list_view_name, kwargs=self.list_view_kwargs(survey.pk))

        response = authenticated_admin.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4

    def test_delete_document(self, authenticated_client, survey, document):
        """Тест удаления документа"""
        url = reverse(
            'document-detail',
            kwargs=self.detail_view_kwargs(survey.pk, document.pk)
        )

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        documents = Document.objects.filter(survey=survey)

        assert len(documents) == 0

    def test_create_document_unauthenticated(self, client, survey):
        """Тест создания документа без аутентификации"""
        image_data = f'{self.base64_prefix}{self.base64_image}'
        url = reverse(self.list_view_name, kwargs=self.list_view_kwargs(survey.pk))
        data = self.data_image(image_data)

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_document_nonexistent_survey(self, authenticated_client,):
        """Тест создания документа для несуществующего опроса"""
        image_data = f'{self.base64_prefix}{self.base64_image}'
        url = reverse(self.list_view_name, kwargs=self.invalid_pk_kwargs)
        data = self.data_image(image_data)

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
