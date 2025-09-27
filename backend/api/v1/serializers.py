import base64
import logging
from random import choices
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError
from rest_framework.serializers import (
    ModelSerializer,
    UUIDField,
    IntegerField,
    CharField,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    BooleanField,
    SerializerMethodField,
    SlugRelatedField,
    ImageField,
)

from api.yadisk import upload_file_and_get_url
from questionnaire.models import Survey, Question, Document
from users.models import User

User = get_user_model()

logger = logging.getLogger(__name__)


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
        user = validated_data.get("user")

        # Вместо get_or_create используем фильтрацию и first()
        existing_survey = Survey.objects.filter(
            user=user, status__in=["new", "processing"]  # Ищем активные опросы
        ).first()

        if existing_survey:
            if restart_question and existing_survey.current_question is None:
                # Перезапускаем завершенный опрос
                existing_survey.current_question = question_start
                existing_survey.status = "new"
                existing_survey.result = []
                existing_survey.questions_version_uuid = (
                    question_start.updated_uuid
                )
                existing_survey.save()
                logger.debug("Опрос %s перезапущен", existing_survey.id)
            else:
                # Возвращаем существующий активный опрос
                logger.debug(
                    "Найден существующий опрос %s", existing_survey.id
                )
            return existing_survey
        else:
            # Создаем новый опрос
            survey_obj = Survey.objects.create(
                user=user,
                current_question=question_start,
                status="new",
                result=[],
                questions_version_uuid=question_start.updated_uuid,
            )
            logger.debug("Создан новый опрос %s", survey_obj.id)
            return survey_obj

    def to_representation(self, instance):
        return SurveyReadSerializer(instance, context=self.context).data


class SurveyUpdateSerializer(ModelSerializer):
    """Сериализатор для обновления опроса"""

    answer = CharField(required=False, allow_blank=True, allow_null=True)
    current_question_text = SerializerMethodField(read_only=True)
    answers = SerializerMethodField(read_only=True)

    class Meta:
        model = Survey
        fields = ("answer", "current_question_text", "answers")
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
        if current_question := instance.current_question:
            next_question, answer_text = self.__get_next_answer_choice(
                answer, current_question
            )

            result = instance.result or []
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
                    except ValidationError as e:
                        logger.error(
                            "Ошибка валидации %s",
                            e,
                            exc_info=True,
                        )
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
                    except Exception as e:
                        logger.error(
                            "Базовая ошибка %s",
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
    def __get_next_answer_choice(answer, question):
        """Перенесенная логика из views.py"""
        if not answer:
            question.text = (
                "Не передан ответ. Ответьте снова.\n" + question.text
            )
            return question, None

        if select_answer_choice := question.answers.filter(
            answer=answer
        ).first():
            return select_answer_choice.next_question, answer

        if select_answer_choice := question.answers.filter(
            answer=None
        ).first():
            return select_answer_choice.next_question, answer

        question.text = "Некорректный ответ. Ответьте снова.\n" + question.text
        return question, None

    def to_representation(self, instance):
        return SurveyReadSerializer(instance, context=self.context).data


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f"{self.parent.context['user']}_"
                f"{''.join(choices('123456789', k=10))}." + ext,
            )
            url = upload_file_and_get_url(data)
        return url

    def to_representation(self, value):
        return value


class DocumentSerializer(ModelSerializer):
    """Сериализатор для документов"""

    image = Base64ImageField()

    class Meta:
        model = Document
        fields = (
            "survey",
            "image",
        )
        read_only_fields = ("survey",)
