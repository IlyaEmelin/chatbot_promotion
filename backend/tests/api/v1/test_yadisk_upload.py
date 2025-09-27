from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestDocumentViewSet:
    """Тесты для DocumentViewSet с mock YandexDiskUploader"""

    base64_image = ('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAA'
                    'AADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==')
    base64_prefix = 'data:image/png;base64,'
    invalid_image = f'{base64_prefix},invalid_base64_data'
    download_url = 'https://mock-download.url/test.png'
    list_view_name = 'document-list'
    detail_view_kwargs = staticmethod(lambda x, y: {'survey_pk': x, 'pk': y})
    list_view_kwargs = staticmethod(lambda x: {'survey_pk': x})
    data_image = staticmethod(lambda x: {'image': x})
    invalid_pk_kwargs = {'survey_pk': uuid4()}
    patch_path = 'api.v1.serializers.YandexDiskUploader'

    def test_create_document_with_base64_image(self, client, mock_yandex_disk_uploader, user, survey):
        """Тест создания документа с base64 изображением"""
        client.force_login(user)
        image_data = f'{self.base64_prefix}{self.base64_image}'
        url = reverse(self.list_view_name, kwargs=self.list_view_kwargs(survey.pk))
        with patch(self.patch_path) as mock_uploader_class:
            mock_uploader_instance = MagicMock()
            mock_uploader_instance.upload_file.return_value = self.download_url
            mock_uploader_class.return_value = mock_uploader_instance
            data = self.data_image(image_data)
            response = client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['image'] == self.download_url
            mock_uploader_instance.upload_file.assert_called_once()

    def test_create_document_invalid_base64(self, client, user, survey):
        """Тест создания документа с невалидным base64"""
        client.force_login(user)
        url = reverse(self.list_view_name, kwargs=self.list_view_kwargs(survey.pk))
        data = self.data_image(self.invalid_image)
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'image' in response.data

    def test_list_documents(self, client, user, survey, document_factory):
        """Тест получения списка документов"""
        client.force_login(user)
        document_factory.create_batch(3, survey=survey)
        url = reverse(self.list_view_name, kwargs=self.list_view_kwargs(survey.pk))
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_delete_document(self, client, user, survey, document):
        """Тест удаления документа"""
        client.force_login(user)
        url = reverse(
            'document-detail',
            kwargs=self.detail_view_kwargs(survey.pk, document.pk)
        )
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_create_document_unauthenticated(self, client, survey):
        """Тест создания документа без аутентификации"""
        image_data = f'{self.base64_prefix}{self.base64_image}'
        url = reverse(self.list_view_name, kwargs=self.list_view_kwargs(survey.pk))
        data = self.data_image(image_data)
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_document_nonexistent_survey(self, client, user):
        """Тест создания документа для несуществующего опроса"""
        client.force_login(user)
        image_data = f'{self.base64_prefix}{self.base64_image}'
        url = reverse(self.list_view_name, kwargs=self.invalid_pk_kwargs)  # Несуществующий ID
        data = self.data_image(image_data)
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_yandex_disk_uploader_integration(self, client, user, survey, mock_yandex_disk_uploader):
        """Тест интеграции с YandexDiskUploader через mock"""
        client.force_login(user)
        image_data = f'{self.base64_prefix}{self.base64_image}'
        url = reverse(self.list_view_name, kwargs=self.list_view_kwargs(survey.pk))
        with patch(self.patch_path) as mock_uploader_class:
            mock_uploader_class.return_value = mock_yandex_disk_uploader
            data = self.data_image(image_data)
            response = client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            mock_yandex_disk_uploader.upload_file.assert_called_once()
