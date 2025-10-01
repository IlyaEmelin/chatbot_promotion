import logging

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path, reverse

from questionnaire.constant import STATUS_CHOICES
from questionnaire.models import (
    AnswerChoice,
    Document,
    Survey,
    Question,
    Comment,
)
from questionnaire.utils import get_docs_zip, get_excel_file

User = get_user_model()
admin.site.unregister(Group)

logger = logging.getLogger(__name__)


class StatusFilter(admin.SimpleListFilter):
    """Фильтр по статусу опроса."""

    title = "Статус заявки"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class DocumentInline(admin.TabularInline):
    """Документы."""

    model = Document
    extra = 0
    readonly_fields = ("image_preview", "download_link")

    @admin.display(description="Предпросмотр")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}"'
                'style="max-height: 100px; max-width: 100px;" /></a>',
                obj.image,
                obj.image,
            )
        return "—"

    @admin.display(description="Скачать")
    def download_link(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank" download>' "Скачать</a>",
                obj.image,
            )
        return "—"


class CommentInline(admin.TabularInline):
    """Комментарии."""

    model = Comment
    extra = 1
    readonly_fields = ("created_at_formatted", "user_display")
    exclude = ("user",)  # Убираем поле пользователя из формы

    @admin.display(description="Пользователь")
    def user_display(self, obj):
        """Отображаем пользователя в readonly режиме."""
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description="Дата создания")
    def created_at_formatted(self, obj):
        if obj.created_at:
            return timezone.localtime(obj.created_at).strftime(
                "%d.%m.%Y %H:%M"
            )
        return "—"

    def get_formset(self, request, obj=None, **kwargs):
        """Автоматически устанавливаем текущего пользователя для новых комментариев."""
        formset = super().get_formset(request, obj, **kwargs)

        class CustomFormSet(formset):
            def save_new(self, form, commit=True):
                instance = form.save(commit=False)
                instance.user = (
                    request.user
                )  # Устанавливаем текущего пользователя
                if commit:
                    instance.save()
                return instance

        return CustomFormSet


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_info",
        "status",
        "documents_count",
        "comments_count",
        "created_at_formatted",
    )
    list_filter = (StatusFilter, "created_at")
    search_fields = ("user__email", "user__phone_number", "created_at")
    readonly_fields = (
        "id",
        "user_info",
        "result_display",
        "current_question",
        "created_at",
        "updated_at",
        "questions_version_uuid",
        "documents_list",
        "comments_list",
    )
    exclude = (
        "user",
        "result",
    )
    list_select_related = ("user", "current_question")
    inlines = (DocumentInline, CommentInline)
    actions = ["download_servey"]

    @admin.action(description="Скачать результаты опроса в формате Excel")
    def download_servey(self, request, queryset):
        return get_excel_file(queryset)

    @admin.display(description="Пользователь")
    def user_info(self, obj):
        user = obj.user
        phone = getattr(user, "phone", "—")
        return format_html(
            "{} {}<br><small>Почта: {}<br>" "Телефон: {}</small>",
            user.first_name or "",
            user.last_name or "",
            user.email,
            phone,
        )

    @admin.display(description="Создана")
    def created_at_formatted(self, obj):
        return timezone.localtime(obj.created_at).strftime("%d.%m.%Y %H:%M")

    @admin.display(description="Документы")
    def documents_count(self, obj):
        return obj.docs.count()

    @admin.display(description="Комментарии")
    def comments_count(self, obj):
        return obj.comments.count()

    @admin.display(description="Результаты опроса")
    def result_display(self, obj):
        result = ""
        for i in range(0, len(obj.result), 2):
            result += f"Вопрос: {obj.result[i]}\nОтвет: {obj.result[i+1]}\n"
        return result

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "download_docs/<uuid:uuid>/",
                self.admin_site.admin_view(get_docs_zip),
                name="download_docs",
            ),
        ]
        return custom_urls + urls

    @admin.display(description="Загруженные документы")
    def documents_list(self, obj):
        documents = obj.docs.all()
        if not documents:
            return "Документы не загружены"

        return format_html(
            '<a class="button" href="{}">Скачать документы</a>',
            reverse("admin:download_docs", args=(obj.id,)),
        )

    documents_list.short_description = "Скачать документы"
    documents_list.allow_tags = True

    @admin.display(description="Комментарии")
    def comments_list(self, obj):
        comments = obj.comments.all().order_by("-created_at")
        if not comments:
            return "Комментарии отсутствуют"

        html = '<div style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 5px;">'
        for comment in comments:
            html += format_html(
                """
                <div style="margin-bottom: 15px; padding: 10px; background: #f9f9f9; border-radius: 5px; border-left: 4px solid #007cba;">
                    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 5px;">
                        <strong style="color: #333;">{}</strong>
                        <small style="color: #666; margin-left: auto;">{}</small>
                    </div>
                    <div style="color: #555; line-height: 1.4;">{}</div>
                </div>
                """,
                comment.user.get_full_name() or comment.user.username,
                timezone.localtime(comment.created_at).strftime(
                    "%d.%m.%Y %H:%M"
                ),
                comment.text,
            )
        html += "</div>"
        return format_html(html)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Документ."""

    list_display = ("survey_short", "image_preview")

    @admin.display(description="Опрос")
    def survey_short(self, obj):
        return f"Опрос {obj.survey.id}"

    @admin.display(description="Изображение")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" '
                'style="max-height: 50px;" /></a>',
                obj.image,
                obj.image,
            )
        return "—"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Вопрос."""

    list_display = (
        "id",
        "text",
        "type",
        "external_table_field_name",
        "updated_uuid",
    )


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    """Вопрос."""

    list_display = (
        "current_question",
        "next_question",
        "answer",
        "new_status",
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Персональная информация",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "patronymic",
                    "email",
                    "phone_number",
                    "telegram_username",
                    "residence",
                )
            },
        ),
        (
            "Подопечный",
            {
                "fields": (
                    "agent_status",
                    "ward_first_name",
                    "ward_last_name",
                    "ward_patronymic",
                    "birthday",
                )
            },
        ),
        (
            "Статус",
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "date_joined",
                    "last_login",
                )
            },
        ),
    )
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "telegram_username",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Комментарии."""

    list_display = ("survey_short", "user_info", "text", "created_at")
    readonly_fields = ("user_info", "created_at_formatted")
    exclude = ["created_at"]
    list_filter = ("survey", "user", "created_at")

    def get_readonly_fields(self, request, obj=None):
        """Делаем поле пользователя readonly при редактировании."""
        if obj:  # При редактировании существующего комментария
            return self.readonly_fields + ("user",)
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        """Устанавливаем текущего пользователя по умолчанию для нового комментария."""
        form = super().get_form(request, obj, **kwargs)

        if not obj:  # Только для создания нового комментария
            form.base_fields["user"].initial = request.user
            form.base_fields["user"].disabled = (
                True  # Делаем поле недоступным для изменения
            )

        return form

    @admin.display(description="Опрос")
    def survey_short(self, obj):
        return f"Опрос {obj.survey.id}"

    @admin.display(description="Пользователь")
    def user_info(self, obj):
        user = obj.user
        phone = getattr(user, "phone", "—")
        return format_html(
            "{} ({} {})<br><small>Почта: {}<br>" "Телефон: {}</small>",
            user.username,
            user.first_name or "",
            user.last_name or "",
            user.email,
            phone,
        )

    @admin.display(description="Дата создания")
    def created_at_formatted(self, obj):
        return timezone.localtime(obj.created_at).strftime("%d.%m.%Y %H:%M")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Для нового комментария устанавливаем текущего пользователя
            obj.user = request.user
        super().save_model(request, obj, form, change)
