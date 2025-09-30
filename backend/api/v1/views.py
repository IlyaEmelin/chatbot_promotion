import logging

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
)

from questionnaire.constant import STATUS_CHOICES
from questionnaire.models import Survey, Document, Comment
from .permissions import (
    AuthorOrStaffOnly,
    NestedAuthorOrStaffOnly,
    NestedAuthorStaffOnly
)
from .serializers import (
    SurveyCreateSerializer,
    SurveyUpdateSerializer,
    SurveyReadSerializer,
    DocumentSerializer,
    CommentSerializer,
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
    permission_classes = (
        IsAuthenticated,
        AuthorOrStaffOnly,
    )
    # TODO: permission_classes = (IsAuthenticated,)
    filter_backends = (SurveyFilterBackend,)

    @action(('patch',), detail=True,)
    def processing(self, request, pk):
        """Метод смены статуса опроса на <В обработке>."""
        survey = self.get_object()
        survey.status = STATUS_CHOICES[2][0]
        survey.save()
        return Response(self.get_serializer(survey).data)

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
        # TODO user = request.user
        user = User.objects.first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=user)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Обновляет опрос через SurveyUpdateSerializer
        """
        # TODO: user = request.user
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
        serializer.save(user=user)

        return Response(serializer.data)


class DocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    """ViewSet для работы с документами."""

    queryset = Document.objects.all()
    permission_classes = (NestedAuthorOrStaffOnly,)
    serializer_class = DocumentSerializer

    def get_serializer_context(self):
        """Добавляем переменную из URL в контекст сериализатора."""
        context = super().get_serializer_context()
        survey = get_object_or_404(Survey, id=self.kwargs.get("survey_pk"))
        context["user"] = survey.user.username
        return context

    def perform_create(self, serializer):
        serializer.save(survey=Survey.objects.get(pk=self.kwargs["survey_pk"]))


class CommentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet для работы с комментариями."""

    queryset = Comment.objects.all()
    permission_classes = (NestedAuthorStaffOnly,)
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(
            survey=get_object_or_404(Survey, pk=self.kwargs["survey_pk"]),
            user=self.request.user,
        )

    def perform_destroy(self, instance):
        get_object_or_404(Survey, pk=self.kwargs["survey_pk"])
        instance.delete()
