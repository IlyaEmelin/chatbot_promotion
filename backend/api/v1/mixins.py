import logging

from django.core.exceptions import ValidationError

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
