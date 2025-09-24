import logging
from uuid import UUID

from django.contrib.auth import get_user_model
from rest_framework.serializers import (
    ModelSerializer,
    UUIDField,
    IntegerField,
    CharField,
    ListField,
    ValidationError,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    BooleanField,
    SerializerMethodField,
    SlugRelatedField,
)

from api.yadisk import upload_files_to_yadisk
from questionnaire.models import Survey, Question, Document

User = get_user_model()

logger = logging.getLogger(__name__)


EMPTY_ANSWER = 'Не передан ответ. Ответьте снова.\n'
INCORRECT_ANSWER = 'Некорректный ответ. Ответьте снова.\n'

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
        fields = ("id", "current_question_text", "answers")

    def get_answers(self, obj):
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
        question_start = Question.objects.filter(type="start_web").first()
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
                "status": "draft",
                "result": [],
                "questions_version_uuid": question_start.updated_uuid,
            },
        )
        if created:
            logger.debug("Создан опрос %", survey_obj)
        elif restart_question and survey_obj.current_question is None:
            survey_obj.current_question = question_start
        return survey_obj

    def to_representation(self, instance):
        return SurveyReadSerializer(instance, context=self.context).data


class DocumentSerializer(ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'image', 'survey',)


class SurveyImgUploadSerializer(ModelSerializer):
    images = DocumentSerializer(many=True,)
    class Meta:
        model = Survey

class SurveyUpdateSerializer(ModelSerializer):
    """Сериализатор для обновления опроса"""

    answer = CharField(required=False, allow_blank=True, allow_null=True)
    current_question_text = SerializerMethodField(read_only=True)
    answers = SerializerMethodField(read_only=True)
    images = ListField(required=False, allow_empty=True, allow_null=True)

    class Meta:
        model = Survey
        fields = ('answer', 'current_question_text', 'answers', 'images',)
        read_only_fields = ('current_question_text', 'answers',)

    def get_current_question_text(self, obj):
        return obj.current_question.text if obj.current_question else None

    def get_answers(self, obj):
        if obj.current_question:
            return list(
                obj.current_question.answers.all().values_list(
                    'answer', flat=True
                )
            )
        return []

    @staticmethod
    def create_documents(survey, urls):
        Document.objects.bulk_create(
            Document(
                survey=survey, image=url,
            ) for url in urls
        )
        # RecipeIngredient.objects.bulk_create(
        #     RecipeIngredient(
        #         recipe=recipe, ingredient_id=i[0], amount=i[1],
        #     ) for i in ingredients_amounts
        # )

    def update(self, instance, validated_data):
        answer = validated_data.get('answer')
        images = validated_data.get('images', [])
        question = instance.current_question

        if question:
            if images:
                try:
                    urls = upload_files_to_yadisk(
                        images,
                        str(instance.questions_version_uuid)[:12]
                    )
                    self.create_documents(instance, urls)
                    answer = 'Загружены документы'
                except Exception:
                    raise
            next_question, answer_text = self.__get_next_answer_choice(
                answer, question
            )

            result = instance.result or []
            if answer_text:
                result.extend((question.text, answer_text))

            instance.current_question = next_question
            instance.status = 'draft' if next_question else 'processing'
            instance.result = result

            if next_question:
                instance.questions_version_uuid = UUID(
                    int=(
                        instance.questions_version_uuid.int
                        ^ next_question.updated_uuid.int
                    )
                )

            if next_question and next_question.updated_at and instance.updated_at:
                instance.updated_at = max(
                    next_question.updated_at, instance.updated_at
                )
            elif next_question:
                instance.updated_at = next_question.updated_at

            instance.save()
        return instance

    @staticmethod
    def __get_next_answer_choice(answer, question):
        """Перенесенная логика из views.py"""
        if not answer:
            question.text = (EMPTY_ANSWER + question.text)
            return question, None

        if select_answer_choice := question.answers.filter(
            answer=answer
        ).first():
            return select_answer_choice.next_question, answer

        if select_answer_choice := question.answers.filter(
            answer=None
        ).first():
            return select_answer_choice.next_question, answer

        question.text = INCORRECT_ANSWER + question.text
        return question, None

    def to_representation(self, instance):
        return SurveyReadSerializer(instance, context=self.context).data
