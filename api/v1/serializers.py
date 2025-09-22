from uuid import UUID

from django.contrib.auth import get_user_model
from rest_framework.serializers import (
    ModelSerializer,
    UUIDField,
    IntegerField,
    CharField,
    ValidationError,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    SlugRelatedField,
)

from questionnaire.models import Survey, Question

User = get_user_model()


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

    current_question = PrimaryKeyRelatedField(
        required=True,
        queryset=Question.objects.all(),
    )

    class Meta:
        model = Survey
        fields = ("current_question",)

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

    def validate(self, attrs):
        if not self.instance.current_question:
            raise ValidationError("Не задан текущий вопрос")
        return attrs

    def update(self, instance, validated_data):
        answer = validated_data.get("answer")
        question = instance.current_question

        next_question, answer_text = self.__get_next_answer_choice(
            answer, question
        )

        result = instance.result or []
        if answer_text:
            result.extend((question.text, answer_text))

        instance.current_question = next_question
        instance.status = "draft" if next_question else "processing"
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
    def __get_next_answer_choice(answer, question):
        """Перенесенная логика из views.py"""
        if not answer:
            question.text = "Не передан ответ. Ответе снова.\n" + question.text
            return question, None

        if select_answer_choice := question.answers.filter(
            answer=answer
        ).first():
            return select_answer_choice.next_question, answer

        if select_answer_choice := question.answers.filter(
            answer=None
        ).first():
            return select_answer_choice.next_question, answer

        question.text = "Не корректный ответ. Ответе снова.\n" + question.text
        return question, None

    def to_representation(self, instance):
        return SurveyReadSerializer(instance, context=self.context).data
