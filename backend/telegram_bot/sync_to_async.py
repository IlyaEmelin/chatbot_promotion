import logging
from asgiref.sync import sync_to_async

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from telegram import User as TelegramUser

from api.v1.serializers import (
    SurveyUpdateSerializer,
    SurveyCreateSerializer,
    DocumentSerializer,
)

from questionnaire.models import Survey, Question, Document

User = get_user_model()

logger = logging.getLogger(__name__)


@sync_to_async
def write_document_db(
    survey_obj: Survey,
    content_file: ContentFile,
) -> None:
    """
    Сохранение файлов в базу

    Args:
        survey_obj: опрос
        content_file: файл
    """
    serializer = DocumentSerializer(
        data={
            "image": content_file,
        },
        context={"user": survey_obj.user},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save(survey=survey_obj)


@sync_to_async
def save_survey_data(
    user_obj: User,
    survey_obj: Survey,
    user_message: str,
) -> tuple[str, list[None | str]]:
    """
    Сохранить "Опрос" через сериализатор

    Args:
        user_obj: пользователь
        survey_obj: опрос,
        user_message: пользовательское сообщение

    Returns:
        str: Вопрос
        list[None|str]: варианты ответа
    """
    serializer = SurveyUpdateSerializer(
        instance=survey_obj,
        data={
            "answer": user_message,
            "add_telegram": False,
        },
        partial=True,
    )
    serializer.is_valid(raise_exception=True)
    serializer.save(user=user_obj)
    data = serializer.data
    return (
        data.get("current_question_text"),
        data.get("answers"),
    )


@sync_to_async
def get_or_create_user(user: TelegramUser) -> User:
    """
    Создать найти пользователя

    Args:
        user:

    Returns:

    """
    user_obj, created = User.objects.get_or_create(
        telegram_username="@" + user.username,
        defaults={
            "username": user.username,
            "telegram_username": "@" + user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            # TODO При первичной авторизации не задается но потом просят задать
            "password": "unusable_password",
        },
    )
    if created:
        logger.debug("Создан пользователь: %s", user_obj)
    return user_obj


@sync_to_async
def get_start_question() -> Question | None:
    """
    Стартовый вопрос

    Returns:
        Question | None: вопрос
    """
    return Question.objects.filter(type="start_telegram").first()


@sync_to_async
def change_processing(survey_obj: Survey) -> None:
    """
    Выставление статуса <В обработке>

    Args:
        survey_obj: объект опроса
    """
    survey_obj.status = "processing"
    survey_obj.save()


@sync_to_async
def get_or_create_survey(
    user_obj: User,
    restart_question: bool,
) -> tuple[
    str,
    list[str | None],
    list[str],
    Survey,
]:
    """
    Получить или создать опрос

    Args:
        user_obj: пользователь
        restart_question: перезапустить опрос

    Returns:
        str: текст текущего вопроса
        list[str|None]: варианта ответа
        list[str]: данные ответы
        Survey: объект вопроса
    """
    create_serializer = SurveyCreateSerializer(
        data={"restart_question": restart_question},
    )
    create_serializer.is_valid(raise_exception=True)
    create_serializer.save(user=user_obj)
    data = create_serializer.data
    return (
        data.get("current_question_text"),
        data.get("answers"),
        data.get("result"),
        create_serializer.instance,
    )


@sync_to_async
def get_survey_documents(survey_obj: Survey) -> list[Document]:
    """
    Получить документы опроса

    Args:
        survey_obj: объект опроса

    Returns:
        list: список документов
    """
    documents = survey_obj.docs.all()
    return list(documents)
