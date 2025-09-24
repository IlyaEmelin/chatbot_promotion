import logging

from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
)

from questionnaire.models import Survey, Question
from .serializers import (
    SurveyCreateSerializer,
    SurveyUpdateSerializer,
    SurveyReadSerializer,
)
from .filter import SurveyFilterBackend

User = get_user_model()
logger = logging.getLogger(__name__)


class SurveyViewSet(
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    """
    ViewSet для работы с опросами
    """

    queryset = Survey.objects.all()
    # permission_classes = [AllowAny]
    permission_classes = (IsAuthenticated,)
    # TODO: заменить на IsAuthenticated
    # permission_classes = [IsAuthenticated]
    filter_backends = (SurveyFilterBackend,)

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия
        """
        if self.action == "create":
            return SurveyCreateSerializer
        elif self.action == "update":
            return SurveyUpdateSerializer
        return SurveyReadSerializer

    def get_queryset(self):
        """
        Возвращает только опросы текущего пользователя
        """
        # TODO если пользователь не IsAuthenticated return queryset.none()
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            return (
                queryset.filter(user=self.request.user)
                .prefetch_related(
                    "current_question",
                )
                .order_by("-created_at")
            )
        return queryset.prefetch_related(
            "current_question",
        ).order_by("-created_at")

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Создает новый опрос для аутентифицированного пользователя

        Args:
            request: запрос для создания опроса
            *args:
            **kwargs:

        Returns:
            Response: ответ на запрос создания
        """
        # TODO: user = request.user
        user = User.objects.first()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=user)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Обновляет опрос через SurveyUpdateSerializer
        """
        # TODO: user == request.user добавить эту проверку в права
        user = User.objects.first()

        # Получаем объект survey
        survey = self.get_object()

        # Создаем сериализатор с instance и data
        serializer = SurveyUpdateSerializer(
            instance=survey,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
