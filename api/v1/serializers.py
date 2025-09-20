from django.shortcuts import get_object_or_404
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
                current_question.next_answer_choice.all().values_list(
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
