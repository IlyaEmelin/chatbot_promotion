from django.db.models import (
    Model,
    CharField,
    TextField,
    ForeignKey,
    DateTimeField,
    OneToOneField,
    UUIDField,
    JSONField,
    CASCADE,
    SET_NULL,
    UniqueConstraint,
)
from django.contrib.auth import get_user_model
from uuid import uuid4

from .constant import (
    MAX_LEN_STRING,
    STATUS_CHOICES,
    STATUS_LEN,
    QUICK_SELECTION_LEN,
    ANSWER_LEN,
)

User = get_user_model()


class Question(Model):
    """
    Вопрос из опросника
    """

    text = TextField(verbose_name="Техт")
    updated_at = DateTimeField(
        auto_now=True,
        verbose_name="Дата последнего изменения",
    )
    updated_uuid = UUIDField(
        default=uuid4,
        editable=False,
        verbose_name="UUID последнего изменения",
    )

    def save(
        self,
        *args,
        **kwargs,
    ):
        """
        Переопределение сохранения

        Args:
            *args: аргументы
            **kwargs: именованные аргументы
        """
        self.updated_uuid = uuid4()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self) -> str:
        if parent := self.parent:
            return f"{self.text[: MAX_LEN_STRING]} (родитель: {parent.id})"
        return f"{self.text[: MAX_LEN_STRING]} корневая подписка"


class AnswerChoice(Model):
    """Вариант ответа"""

    last_question = ForeignKey(
        Question,
        on_delete=CASCADE,
        verbose_name="Преведущий вопрос",
    )
    next_question = ForeignKey(
        Question,
        on_delete=CASCADE,
        verbose_name="Следующий вопрос",
    )
    answer = CharField(
        max_length=ANSWER_LEN,
        verbose_name="Вариант ответа(None - пользовательский)",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответа"
        constraints = (
            UniqueConstraint(
                fields=(
                    "last_question",
                    "next_question",
                )
            ),
            UniqueConstraint(
                fields=(
                    "last_question",
                    "answer",
                )
            ),
        )

    def __str__(self):
        return (
            f"{self.answer[:MAX_LEN_STRING] if self.answer else None} "
            f"от { str(self.last_question)[:MAX_LEN_STRING]} "
            f"к {str(self.next_question)[:MAX_LEN_STRING]}"
        )


class Survey(Model):
    """Опрос"""

    id = UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="UUID опроса",
    )
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="surveys",
        verbose_name="Пользователь",
    )
    question = OneToOneField(
        Question,
        on_delete=SET_NULL,
        related_name="survey",
        verbose_name="Вопрос опроса",
    )
    status = CharField(
        max_length=STATUS_LEN,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Статус опроса",
    )
    result = JSONField(
        verbose_name="Результаты опроса",
        null=True,
        blank=True,
        default=list,  # или default=list в зависимости от структуры данных
        help_text="JSON структура с ответами пользователя на вопросы опроса",
    )
    # UUID версии вопросов (для отслеживания версии анкеты)
    questions_version_uuid = UUIDField(
        default=uuid4,
        editable=False,
        verbose_name="UUID версии вопросов",
    )
    created_at = DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания опроса",
    )
    updated_at = DateTimeField(
        auto_now=True,
        verbose_name="Дата последнего изменения",
    )

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"

    def __str__(self) -> str:
        return f"Опрос пользователя {self.user} (статус: {self.status})"
