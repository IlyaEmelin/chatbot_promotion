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

    text = TextField(verbose_name="Текст")
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
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self) -> str:
        return self.text[:MAX_LEN_STRING]


class AnswerChoice(Model):
    """Вариант ответа"""

    last_question = ForeignKey(
        Question,
        on_delete=CASCADE,
        verbose_name="Предыдущий вопрос",
        related_name="last_questions",
    )
    next_question = ForeignKey(
        Question,
        on_delete=CASCADE,
        verbose_name="Следующий вопрос",
        null=True,
        blank=True,
        related_name="next_questions",
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
                name="unique_last_next_question",
                fields=(
                    "last_question",
                    "next_question",
                    "answer",
                ),
            ),
            UniqueConstraint(
                name="unique_last_question_answer",
                fields=(
                    "last_question",
                    "answer",
                ),
            ),
        )

    def __str__(self):
        next_q_text = (
            self.next_question[:MAX_LEN_STRING]
            if self.next_question
            else "КОНЕЦ"
        )
        last_q_text = str(self.last_question)[:MAX_LEN_STRING]
        answer_text = (
            self.answer[:MAX_LEN_STRING] if self.answer else "Пользовательский"
        )
        return f"{answer_text} от {last_q_text} к {next_q_text}"


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
    current_question = ForeignKey(
        Question,
        on_delete=SET_NULL,
        related_name="surveys",
        verbose_name="Текущий вопрос",
        null=True,
        blank=True,
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
