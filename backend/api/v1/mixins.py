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

    def get_revert_success(self, obj: Survey) -> bool:
        """
        Успешность отката

        Args:
            obj: опрос

        Returns:
            bool: успешность отката
        """
        return self.context.get("revert_success", False)

    @staticmethod
    def _get_last_question(instance: Survey, validated_data) -> Question:
        """
        Получить прошлый вопрос

        Args:
            instance: опрос

        Returns:
            Question: прошлый вопрос
        """
        last_question = None
        if (current_question := instance.current_question) and (
            result := instance.result
        ):
            add_telegram = validated_data.pop("add_telegram", True)
            question_text, answer_text = result[-2], result[-1]
            if previous_answers := current_question.previous_answers.all():
                if not add_telegram and previous_answers:
                    previous_answers = set(
                        (
                            previous_answer.current_question.previous_answers.first()
                            if previous_answer.current_question.external_table_field_name
                            == "User.telegram_username"
                            else previous_answer
                        )
                        for previous_answer in previous_answers
                    )

                name_match_previous_answer = tuple(
                    previous_answer
                    for previous_answer in previous_answers
                    if (
                        previous_answer.answer == answer_text
                        and previous_answer.current_question.text
                        == question_text
                    )
                )
                if len(name_match_previous_answer) == 1:
                    last_question = name_match_previous_answer[
                        0
                    ].current_question
                else:
                    none_match_previous_answer = tuple(
                        previous_answer
                        for previous_answer in previous_answers
                        if (
                            previous_answer.answer is None
                            and previous_answer.current_question.text
                            == question_text
                        )
                    )
                    if len(none_match_previous_answer) == 1:
                        last_question = none_match_previous_answer[
                            0
                        ].current_question
        return last_question
