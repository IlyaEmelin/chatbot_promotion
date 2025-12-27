import logging

from django.core.exceptions import ValidationError
from rest_framework.serializers import (
    SerializerMethodField,
)

from questionnaire.models import Comment, Document, Question, Survey

logger = logging.getLogger(__name__)


class SurveyQuestionStartMixin:
    """
    Миксин стартового вопроса
    """

    @staticmethod
    def _get_question_start() -> Question:
        """
        Получить стартовый вопрос

        Returns:
            Question: стартовый вопрос
        """
        question_start = Question.objects.filter(type="start").first()
        if not question_start:
            text = "Не существует стартового вопроса для опроса."
            logger.error(text)
            raise ValidationError(text)
        return question_start


class SurveyQuestionAnswers:
    """
    Миксин текущего вопроса и вариантов ответа
    """

    def get_current_question_text(self, obj: Survey) -> str:
        """
        Получить текст текущего вопроса

        Args:
            obj: опрос

        Returns:
            str: текст текущего вопроса
        """
        return obj.current_question.text if obj.current_question else None

    def get_answers(self, obj: Survey) -> list[str | None]:
        """
        Получить варианты ответа для текущего вопроса

        Args:
            obj: опрос

        Returns:
            list[str|None]: варианты ответа
        """
        if current_question := obj.current_question:
            return list(
                current_question.answers.all().values_list(
                    "answer",
                    flat=True,
                )
            )
        return []
