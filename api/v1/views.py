from uuid import UUID

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import (
    GenericViewSet,
)
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
)

from questionnaire.models import Survey, Question, AnswerChoice
from .serializers import (
    SurveyCreateSerializer,
    SurveyUpdateSerializer,
    SurveyReadSerializer,
)

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
    serializer = SurveyCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors},
            status=HTTP_400_BAD_REQUEST,
        )

    serializer.save(
        user=user,
        status="draft",
        result=[],
        questions_version_uuid=serializer.validated_data[
            "current_question"
        ].updated_uuid,
    )

    return Response(serializer.data)


@api_view(("PUT",))
@permission_classes((AllowAny,))
# TODO @permission_classes((IsAuthenticated, ))
def update_survey(request: Request, pk: UUID) -> Response:
    """
    Обновляет опрос через SurveyUpdateSerializer

    Args:
        request: запрос
        pk: UUID опроса

    Returns:
        Response: ответ с данными обновленного опроса
    """

    # TODO user == request.user добавить эту проверку в права
    user = User.objects.first()

    # Получаем объект survey
    survey = get_object_or_404(Survey, pk=pk)

    # Создаем сериализатор с instance и data
    serializer = SurveyUpdateSerializer(
        instance=survey,
        data=request.data,
        partial=True,  # Разрешаем частичное обновление
    )

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors},
            status=HTTP_400_BAD_REQUEST,
        )

    serializer.save()

    return Response(serializer.data)
