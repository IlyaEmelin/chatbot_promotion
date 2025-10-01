from idlelib.browser import file_open
from random import choices
from string import digits
from uuid import UUID
import base64
import logging

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError
from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    BooleanField,
    SerializerMethodField,
    SlugRelatedField,
    ImageField,
)

from api.yadisk import YandexDiskUploader
from questionnaire.models import Survey, Question, Document, Comment
from users.models import User


logger = logging.getLogger(__name__)


DECODE_ERROR = "Ошибка кодировки изображения - {}"


class QuestionSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"


class SurveyReadSerializer(ModelSerializer):
    """Сериализатор для чтения опроса"""

    current_question_text = SlugRelatedField(
        source="current_question",
        slug_field="text",
        read_only=True,
    )
    answers = SerializerMethodField()

    class Meta:
        model = Survey
        fields = ("id", "current_question_text", "answers", "result")

    def get_answers(self, obj) -> list[str | None]:
        """
        Варианты ответа

        Args:
            obj: объект

        Returns:
            list[str| None]: варианты ответа None произвольный ответ
        """
        if current_question := obj.current_question:
            return list(
                current_question.answers.all().values_list(
                    "answer",
                    flat=True,
                )
            )
        else:
            return []


class SurveyCreateSerializer(ModelSerializer):
    """Сериализатор для создания опроса"""

    restart_question = BooleanField(
        required=False,
        default=False,
    )

    class Meta:
        model = Survey
        fields = (
            "restart_question",
            "status",
            "result",
            "questions_version_uuid",
        )

    @staticmethod
    def __get_question_start() -> Question:
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

    def create(self, validated_data):
        restart_question = validated_data.pop("restart_question", False)
        question_start = self.__get_question_start()

        survey_obj, created = Survey.objects.get_or_create(
            user=validated_data.get("user"),
            defaults={
                "current_question": question_start,
                "status": "new",
                "result": [],
                "questions_version_uuid": question_start.updated_uuid,
            },
        )
        if created:
            logger.debug("Создан опрос %", survey_obj)
        elif (
            restart_question
            and survey_obj.current_question is None
            and survey_obj.status in ("processing", "completed")
        ):
            survey_obj.current_question = question_start
            survey_obj.status = "new"
            survey_obj.result = []
            survey_obj.docs.all().delete()
            survey_obj.save()

        return survey_obj

    def to_representation(self, instance):
        return SurveyReadSerializer(instance, context=self.context).data


class SurveyUpdateSerializer(ModelSerializer):
    """Сериализатор для обновления опроса"""

    answer = CharField(required=False, allow_blank=True, allow_null=True)
    current_question_text = SerializerMethodField(read_only=True)
    answers = SerializerMethodField(read_only=True)
    add_telegram = BooleanField(
        required=False,
        default=True,
    )

    class Meta:
        model = Survey
        fields = (
            "answer",
            "current_question_text",
            "answers",
            "add_telegram",
        )
        read_only_fields = ("current_question_text", "answers")

    def get_current_question_text(self, obj):
        return obj.current_question.text if obj.current_question else None

    def get_answers(self, obj):
        if obj.current_question:
            return list(
                obj.current_question.answers.all().values_list(
                    "answer", flat=True
                )
            )
        return []

    def update(self, instance, validated_data):
        answer = validated_data.get("answer")
        add_telegram = validated_data.pop("add_telegram", True)

        if current_question := instance.current_question:
            next_question, new_status, answer_text = (
                self.__get_next_answer_choice(answer, current_question)
            )

            result = instance.result or []
            if (
                not add_telegram
                and next_question
                and next_question.external_table_field_name
                == "User.telegram_username"
            ):
                logger.debug(
                    "Пропуск вопроса @username для телеграм, в телеграм боте."
                )
                next_question = next_question.answers.first().next_question

            if answer_text:
                result.extend((current_question.text, answer_text))

            if current_question and (
                field_name := current_question.external_table_field_name
            ):
                self.__save_external_field(
                    instance,
                    field_name,
                    answer_text,
                )

            instance.current_question = next_question
            instance.status = "new" if next_question else "waiting_docs"
            instance.result = result
            if new_status:
                instance.status = new_status

            if next_question:
                instance.questions_version_uuid = UUID(
                    int=(
                        instance.questions_version_uuid.int
                        ^ next_question.updated_uuid.int
                    )
                )

            if next_question and instance.updated_at:
                instance.updated_at = max(
                    next_question.updated_at, instance.updated_at
                )
            elif next_question:
                instance.updated_at = next_question.updated_at

            instance.save()
        return instance

    @staticmethod
    def __save_external_field(
        survey: Survey,
        field_name: str,
        answer_text: str,
    ) -> None:
        """
        Сохранение поля во внешние таблицы

        Args:
            survey: текущий опрос
            field_name: имя поля для сохранения
            answer_text: сохраняемое значение
        """
        logger.debug(
            "Попытка сохранения принятого значения во внешнее поле таблицы."
        )
        try:
            table_name, field_name = field_name.split(".")
            if table_name == "User":
                user = survey.user
                if hasattr(User, field_name):
                    try:
                        logger.debug(
                            "Сохранение для пользователя %s.\n'%s': '%s'",
                            str(user),
                            field_name,
                            answer_text,
                        )

                        setattr(user, field_name, answer_text)
                        user.full_clean()
                        user.save()
                    except IntegrityError as e:
                        logger.error(
                            "Ошибка целостности данных %s",
                            e,
                            exc_info=True,
                        )
                    except DatabaseError as e:
                        logger.error(
                            "Ошибка базы данных %s",
                            e,
                            exc_info=True,
                        )

                else:
                    logger.error(
                        f"Поле {field_name} не найдено "
                        f"в таблице {str(User)}."
                    )
            else:
                logger.error(
                    f"Не корректное имя модели: {table_name}\n"
                    "При попытке сохранить поле "
                    "во внешнюю таблицу.\n"
                )
        except ValueError as exp:
            logger.error(
                (
                    "Не корректный формат поля "
                    "'external_table_field_name' %s\n"
                ),
                str(exp),
                exc_info=True,
            )

    @staticmethod
    def __get_next_answer_choice(
        answer: str | None,
        question: Question,
    ) -> tuple[Question, str | None, str | None]:
        """
        Получить следующий вопрос

        Args:
            answer: текст ответа
            question: текущий вопрос

        Returns:
            Question: следующий вопрос
            str | None: смена статуса опроса после ответа
            str | None: текст ответа
        """
        if not answer:
            question.text = (
                "Не передан ответ. Ответьте снова.\n" + question.text
            )
            return question, None, None

        if select_answer_choice := question.answers.filter(
            answer=answer
        ).first():
            return (
                select_answer_choice.next_question,
                select_answer_choice.new_status,
                answer,
            )

        if select_answer_choice := question.answers.filter(
            answer=None
        ).first():
            return (
                select_answer_choice.next_question,
                select_answer_choice.new_status,
                answer,
            )

        question.text = "Некорректный ответ. Ответьте снова.\n" + question.text
        return question, None, None

    def to_representation(self, instance):
        return SurveyReadSerializer(instance, context=self.context).data


class Base64ImageField(ImageField):
    """Класс поля для изображений документов."""

    def to_internal_value(self, data):
        if (isinstance(data, str)
                and data.startswith("data:image")
                or data.startswith("data:application/pdf")):
            file_format, file_str = data.split(";base64,")
            try:
                return ContentFile(
                    base64.b64decode(file_str),
                    name=f"{self.parent.context['user']}"
                    f'{"".join(choices(digits, k=10))}.'
                    + file_format.split("/")[-1],
                )
            except Exception as e:
                logger.error(DECODE_ERROR.format(e))
                raise ValidationError(DECODE_ERROR.format(e))

    def to_representation(self, value):
        return value


class DocumentSerializer(ModelSerializer):
    """Сериализатор для документов."""

    image = Base64ImageField()

    class Meta:
        model = Document
        fields = (
            "survey",
            "image",
        )
        read_only_fields = ("survey",)

    def create(self, validated_data):
        data = validated_data.pop('image')
        try:
            url = YandexDiskUploader(
                settings.DISK_TOKEN,
            ).upload_file(data.name, data.read())
        except Exception:
            raise
        document = Document.objects.create(**validated_data, image=url)
        return document


class CommentSerializer(ModelSerializer):
    """Сериализатор для комментариев."""

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("id", "survey", "user", "created_at")
