import time
import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from questionnaire.models import Comment

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestCommentViewSet:
    """Тесты для CommentViewSet"""

    @staticmethod
    def get_list_url(survey_id):
        return reverse(
            viewname='comment-list',
            kwargs={'survey_pk': survey_id},
        )

    @staticmethod
    def get_detail_url(survey_id, comment_id):
        return reverse(
            viewname='comment-detail',
            kwargs={
                'survey_pk': survey_id,
                'pk': comment_id
            },
        )

    def test_create_comment_as_admin(
            self, authenticated_admin, admin_user, survey, comment_data,
    ):
        """Тест создания комментария администратором"""
        response = authenticated_admin.post(
            self.get_list_url(survey.id), comment_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.count() == 1
        assert Comment.objects.first().text == comment_data['text']
        assert Comment.objects.first().survey == survey
        assert Comment.objects.first().user == admin_user

    def test_create_comment_as_regular_user_should_fail(
            self, authenticated_client, survey, comment_data
    ):
        """Тест что обычный пользователь не может создать комментарий"""
        response = authenticated_client.post(
            self.get_list_url(survey.id), comment_data
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.count() == 0

    def test_create_comment_unauthenticated_should_fail(
            self, api_client, survey, comment_data
    ):
        """Тест что неаутентифицированный пользователь
        не может создать комментарий"""
        url = self.get_list_url(survey.id)
        response = api_client.post(url, comment_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Comment.objects.count() == 0

    def test_create_comment_with_empty_text_should_fail(
            self, authenticated_admin, admin_user, survey
    ):
        """Тест создания комментария с пустым текстом"""
        response = authenticated_admin.post(
            self.get_list_url(survey.id), {"text": ""}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Comment.objects.count() == 0

    def test_create_comment_with_missing_text_should_fail(
            self, authenticated_admin, admin_user, survey
    ):
        """Тест создания комментария без текста"""
        response = authenticated_admin.post(self.get_list_url(survey.id), {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Comment.objects.count() == 0

    def test_create_comment_for_nonexistent_survey_should_fail(
            self, authenticated_admin, admin_user, comment_data
    ):
        """Тест создания комментария для несуществующего опроса"""
        response = authenticated_admin.post(
            self.get_list_url(uuid.uuid4()),
            comment_data
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Comment.objects.count() == 0

    # Тесты удаления комментария

    def test_delete_comment_as_admin(self, authenticated_admin, admin_user, comment):
        """Тест удаления комментария администратором"""
        response = authenticated_admin.delete(
            self.get_detail_url(comment.survey.pk, comment.pk)
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Comment.objects.count() == 0

    def test_delete_comment_as_regular_user_should_fail(
            self, authenticated_client, user, comment
    ):
        """Тест что обычный пользователь не может удалить комментарий"""
        response = authenticated_client.delete(
            self.get_detail_url(comment.survey.pk, comment.pk)
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.count() == 1

    def test_delete_comment_unauthenticated_should_fail(
            self, api_client, comment
    ):
        """Тест что неаутентифицированный пользователь
        не может удалить комментарий"""
        response = api_client.delete(
            self.get_detail_url(comment.survey.pk, comment.pk)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Comment.objects.count() == 1

    def test_delete_nonexistent_comment_should_fail(
            self, authenticated_admin, survey
    ):
        """Тест удаления несуществующего комментария"""
        response = authenticated_admin.delete(
            self.get_detail_url(survey.pk, 1)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_comment_from_nonexistent_survey_should_fail(
            self, authenticated_admin, admin_user, comment
    ):
        """Тест удаления комментария из несуществующего опроса"""
        response = authenticated_admin.delete(
            self.get_detail_url(uuid.uuid4(), comment.pk)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    # Тесты модели

    def test_comment_creation(self, survey, admin_user):
        """Тест создания модели комментария"""
        comment = Comment.objects.create(
            survey=survey,
            user=admin_user,
            text="Test comment"
        )

        assert comment.survey == survey
        assert comment.user == admin_user
        assert comment.text == "Test comment"
        assert comment.created_at is not None

    def test_comment_ordering(self, survey, admin_user):
        """Тест порядка комментариев"""
        comment1 = Comment.objects.create(
            survey=survey, user=admin_user, text="First comment",
        )
        time.sleep(0.1)
        comment2 = Comment.objects.create(
            survey=survey, user=admin_user, text="Second comment"
        )

        comments = Comment.objects.all()

        assert comments[0] == comment2
        assert comments[1] == comment1

    # Тесты связей

    def test_comment_cascade_delete_with_survey(self, survey, admin_user):
        """Тест каскадного удаления комментариев при удалении опроса"""
        Comment.objects.create(
            survey=survey, user=admin_user, text="Test comment"
        )

        assert Comment.objects.count() == 1
        survey.delete()
        assert Comment.objects.count() == 0
