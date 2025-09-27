# test_survey_external_fields.py
import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK
from questionnaire.models import Survey, Question, AnswerChoice
from users.models import User


@pytest.mark.django_db
class TestSurveyUpdateExternalFields:
    """Тесты для проверки сохранения полей пользователя через external_table_field_name"""

    def test_update_survey_saves_user_first_name(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест сохранения имени пользователя через external_table_field_name"""
        # Создаем вопрос с external_table_field_name для сохранения в User.first_name
        question.external_table_field_name = "User.first_name"
        question.save()

        # Создаем AnswerChoice для перехода к следующему вопросу
        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="42345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "Иван"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        # Проверяем, что поле пользователя сохранилось
        survey.user.refresh_from_db()
        assert survey.user.first_name == "Иван"

    def test_update_survey_saves_user_last_name(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест сохранения фамилии пользователя"""
        question.external_table_field_name = "User.last_name"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="52345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "Петров"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        survey.user.refresh_from_db()
        assert survey.user.last_name == "Петров"

    def test_update_survey_saves_user_email(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест сохранения email пользователя"""
        question.external_table_field_name = "User.email"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="62345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "newemail@example.com"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        survey.user.refresh_from_db()
        assert survey.user.email == "newemail@example.com"

    def test_update_survey_saves_user_phone_number(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест сохранения номера телефона пользователя"""
        question.external_table_field_name = "User.phone_number"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="72345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "+79161234567"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        survey.user.refresh_from_db()
        assert survey.user.phone_number == "+79161234567"

    def test_update_survey_saves_user_residence(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест сохранения города проживания пользователя"""
        question.external_table_field_name = "User.residence"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="82345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "Москва"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        survey.user.refresh_from_db()
        assert survey.user.residence == "Москва"

    def test_update_survey_saves_user_telegram_username(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест сохранения Telegram username пользователя"""
        question.external_table_field_name = "User.telegram_username"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="92345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "@testuser"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        survey.user.refresh_from_db()
        assert survey.user.telegram_username == "@testuser"

    def test_update_survey_saves_user_patronymic(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест сохранения отчества пользователя"""
        question.external_table_field_name = "User.patronymic"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="a2345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "Сергеевич"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        survey.user.refresh_from_db()
        assert survey.user.patronymic == "Сергеевич"

    def test_update_survey_saves_user_birthday(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест сохранения даты рождения пользователя"""
        question.external_table_field_name = "User.birthday"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="b2345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "01.12.2000"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        survey.user.refresh_from_db()
        assert str(survey.user.birthday) == "01.12.2000"

    def test_update_survey_saves_multiple_user_fields_sequential(
        self,
        authenticated_client,
        user,
        question,
    ):
        """
        Тест последовательного сохранения нескольких полей пользователя через разные вопросы

        Args:
            authenticated_client: аутенфицированный клиент
            user: пользователь
            question: вопрос.
        """
        survey = Survey.objects.create(
            user=user,
            current_question=question,
            status="new",
            result=[],
            questions_version_uuid="32345678-1234-1234-1234-123456789012",
        )

        # Первый вопрос - сохраняем имя
        question.external_table_field_name = "User.first_name"
        question.save()

        # Создаем второй вопрос для перехода
        second_question = Question.objects.create(
            text="Второй вопрос",
            updated_uuid="c2345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=second_question,
            answer=None,
        )

        # Первый запрос - сохраняем имя
        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "next"}

        response = authenticated_client.put(url, data, format="json")
        assert response.status_code == HTTP_200_OK

        # Второй вопрос - сохраняем фамилию
        second_question.external_table_field_name = "User.last_name"
        second_question.save()

        # Создаем третий вопрос для перехода
        third_question = Question.objects.create(
            text="Третий вопрос",
            updated_uuid="d2345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=second_question,
            next_question=third_question,
            answer=None,
        )

        # Второй запрос - сохраняем фамилию
        data = {"answer": "next2"}
        response = authenticated_client.put(url, data, format="json")
        assert response.status_code == HTTP_200_OK

        # Проверяем, что оба поля сохранились
        user.refresh_from_db()
        assert user.first_name == "next"
        assert user.last_name == "next2"

    def test_update_survey_with_custom_answer_saves_user_field(
        self,
        authenticated_client,
        survey_with_custom_answer,
        question_with_custom_answer,
    ):
        """Тест сохранения поля пользователя с пользовательским ответом"""
        question_with_custom_answer.external_table_field_name = (
            "User.residence"
        )
        question_with_custom_answer.save()

        url = reverse(
            "survey-detail", kwargs={"pk": survey_with_custom_answer.id}
        )
        custom_answer = "Санкт-Петербург"
        data = {"answer": custom_answer}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        survey_with_custom_answer.user.refresh_from_db()
        assert survey_with_custom_answer.user.residence == custom_answer

    def test_update_survey_external_field_empty_value(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест сохранения пустого значения в поле пользователя"""
        question.external_table_field_name = "User.residence"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="e2345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": ""}  # Пустое значение

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        survey.user.refresh_from_db()
        assert survey.user.residence == None

    def test_update_survey_external_field_none_value(
        self,
        authenticated_client,
        survey,
        question,
    ):
        """Тест сохранения None значения в поле пользователя"""
        question.external_table_field_name = "User.patronymic"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="f2345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": None}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

        survey.user.refresh_from_db()
        assert survey.user.patronymic is None

    def test_update_survey_with_invalid_external_field_format(
        self,
        authenticated_client,
        survey,
        question,
        caplog,
    ):
        """Тест обработки некорректного формата external_table_field_name"""
        question.external_table_field_name = "InvalidFormat"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="g2345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "some_value"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

    def test_update_survey_with_nonexistent_user_field(
        self,
        authenticated_client,
        survey,
        question,
        caplog,
    ):
        """Тест обработки несуществующего поля пользователя"""
        question.external_table_field_name = "User.nonexistent_field"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="h2345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "some_value"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK

    def test_update_survey_with_nonexistent_model_name(
        self,
        authenticated_client,
        survey,
        question,
        caplog,
    ):
        """Тест обработки несуществующего имени модели"""
        question.external_table_field_name = "InvalidModel.first_name"
        question.save()

        next_question = Question.objects.create(
            text="Следующий вопрос",
            updated_uuid="i2345678-1234-1234-1234-123456789012",
        )
        AnswerChoice.objects.create(
            current_question=question,
            next_question=next_question,
            answer=None,
        )

        url = reverse("survey-detail", kwargs={"pk": survey.id})
        data = {"answer": "some_value"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == HTTP_200_OK
