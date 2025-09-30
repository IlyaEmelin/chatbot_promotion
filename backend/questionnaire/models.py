from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    Index,
    JSONField,
    Model,
    SET_NULL,
    TextField,
    UniqueConstraint,
    UUIDField,
)
from django.contrib.auth import get_user_model
from uuid import uuid4

from .constant import (
    ANSWER_LEN,
    FILE_URL_MAX_LEN,
    MAX_LEN_STRING,
    STATUS_CHOICES,
    STATUS_LEN,
    QUESTION_TYPE,
    QUESTION_TYPE_LEN,
    EXTERNAL_TABLE_FIELD_NAME_CHOICES,
)

User = get_user_model()


class Question(Model):
    """Вопрос из опросника"""

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
    type = CharField(
        max_length=QUESTION_TYPE_LEN,
        choices=QUESTION_TYPE,
        default="standart",
        verbose_name="Тип вопроса",
    )
    external_table_field_name = CharField(
        max_length=QUESTION_TYPE_LEN,
        choices=EXTERNAL_TABLE_FIELD_NAME_CHOICES,
        verbose_name="Имя поля по внешней таблице",
        null=True,
        blank=True,
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
        return f"{self.text[:MAX_LEN_STRING-10]} ({self.type})"


class AnswerChoice(Model):
    """Вариант ответа"""

    current_question = ForeignKey(
        Question,
        on_delete=CASCADE,
        verbose_name="Предыдущий вопрос",
        related_name="answers",
    )
    next_question = ForeignKey(
        Question,
        on_delete=CASCADE,
        verbose_name="Следующий вопрос",
        null=True,
        blank=True,
        related_name="previous_answers",
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
                name="unique_last_question_answer",
                fields=(
                    "current_question",
                    "answer",
                ),
            ),
        )

    def __str__(self):
        next_q_text = (
            str(self.next_question)[:MAX_LEN_STRING]
            if self.next_question
            else "КОНЕЦ"
        )
        last_q_text = str(self.current_question)[:MAX_LEN_STRING]
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
        default="new",
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
    created_at = DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания опроса",
    )
    questions_version_uuid = UUIDField(
        default=uuid4,
        editable=False,
        verbose_name="UUID версии вопросов",
    )
    updated_at = DateTimeField(
        verbose_name="Дата последнего изменения ветки опросов",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"
        ordering = ("-created_at",)
        indexes = (Index(fields=["created_at"]),)

    def __str__(self) -> str:
        return f"Опрос пользователя {self.user} (статус: {self.status})"


class Document(Model):
    """Документ"""

    image = CharField(
        max_length=FILE_URL_MAX_LEN,
        verbose_name='Изображение документа',
    )
    survey = ForeignKey(
        Survey,
        on_delete=CASCADE,
        related_name='docs',
        verbose_name='Опрос',
    )

    class Meta:
        verbose_name = 'документ'
        verbose_name_plural = 'Документы'

    def __str__(self):
        return f'Документ, привязанный к опросу {self.survey}.'


class Comment(Model):
    """Комментарий"""

    text = TextField(
        verbose_name='Текст',
    )
    survey = ForeignKey(
        Survey,
        on_delete=CASCADE,
        verbose_name='Опрос',
    )
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='Пользователь',
    )
    created_at = DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания комментария',
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('-created_at',)

    def __str__(self):
        return f'Комментарий к опросу {self.survey}.'
