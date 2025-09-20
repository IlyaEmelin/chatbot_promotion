from uuid import UUID

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import (
    GenericViewSet,
)
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
)

from questionnaire.models import Survey, Question, AnswerChoice

User = get_user_model()


@api_view(("POST",))
@permission_classes((AllowAny,))
# TODO @permission_classes([IsAuthenticated])
def create_survey(request: Request) -> Response:
    """
    Создает новый опрос для аутентифицированного пользователя

    Args:
        request: запрос

    Returns:

    """

    # TODO user = request.user
    user = User.objects.first()
    question_id = request.data.get("question_id")
    question = get_object_or_404(
        Question,
        pk=question_id,
    )
    survey = Survey.objects.create(
        user=request.user,
        current_question=question,
        status="draft",
        result=[],
        questions_version_uuid=question.updated_uuid,
    )
    return Response(
        {
            "id": survey.id,
            "question": question.text,
            "answers": [
                answer_choice.answer
                for answer_choice in (question.last_answer_choice or [])
            ],
        }
    )


def __get_next_answer_choice(
    answer: str | None,
    question: Question,
) -> tuple[Question, str | None]:
    """

    Args:
        answer: ответ полученный на вопрос
        question: вопрос текущий

    Returns:
        Question: следующий вопрос
        str|None: ответ
    """
    if not answer:
        question.text = "Не переда ответ. Ответе снова.\n" + question.text
        return question, None

    try:
        select_answer_choice = next(
            answer_choice
            for answer_choice in question.next_answer_choice
            if answer_choice.answer == answer
        )
        return select_answer_choice.next_question, answer
    except StopIteration:
        try:
            select_answer_choice = next(
                answer_choice
                for answer_choice in question.last_answer_choice
                if answer_choice.answer is None
            )
            return select_answer_choice.next_question, answer
        except StopIteration:
            pass
    question.text = "Не корректный ответ. Ответе снова.\n" + question.text
    return question, None


@api_view
@permission_classes((AllowAny,))
# TODO @permission_classes((IsAuthenticated, ))
def update_survey(request: Request) -> Response:
    """
    Создает новый опрос для аутентифицированного пользователя

    Args:
        request: запрос

    Returns:

    """

    # TODO user = request.user
    user = User.objects.first()
    survey_id, answer = (
        request.data.get("survey_id"),
        request.data.get("answer"),
    )
    survey = get_object_or_404(
        Survey,
        pk=survey_id,
    )
    if question := survey.current_question:
        next_question, answer_text = __get_next_answer_choice(
            answer,
            question,
        )

        result = survey.result or []
        if answer_text:
            result.extend(
                (
                    question.text,
                    answer_text,
                )
            )

        survey.objects.update(
            current_question=next_question,
            status="draft" if next_question else "processing",
            result=result,
            questions_version_uuid=(
                UUID(
                    survey.questions_version_uuid.int
                    ^ next_question.updated_uuid.int
                )
                if next_question
                else survey.questions_version_uuid
            ),
            updated_at=(
                max(next_question.updated_at, survey.updated_at)
                if survey.updated_at
                else (
                    next_question.updated_at
                    if next_question
                    else survey.updated_at
                )
            ),
        )

        return Response(
            {
                "id": survey.id,
                "question": question.text,
                "answers": [
                    answer_choice.answer
                    for answer_choice in (question.next_answer_choice or [])
                ],
            }
        )
    raise ValidationError("Не задан текущий вопрос")
