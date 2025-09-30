from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.html import format_html

from django.urls import path, reverse

from questionnaire.constant import STATUS_CHOICES
from questionnaire.models import AnswerChoice, Document, Survey, Question
from questionnaire.utils import get_docs_zip, get_excel_file

User = get_user_model()


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


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_info",
        "status",
        "documents_count",
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
    )
    exclude = ("user", "result",)
    list_select_related = ("user", "current_question")
    inlines = (DocumentInline,)
    actions = ['download_servey']

    @admin.action(description='Скачать результаты опроса в формате Excel')
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

    @admin.display(description="Результаты опроса")
    def result_display(self, obj):
        result = ''
        for i in range(0, len(obj.result), 2):
            result += f'Вопрос: {obj.result[i]}\nОтвет: {obj.result[i+1]}\n'
        return result

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'download_docs/<uuid:uuid>/',
                self.admin_site.admin_view(get_docs_zip),
                name='download_docs',
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
            reverse('admin:download_docs', args=(obj.id,))
        )
    documents_list.short_description = 'Скачать документы'
    documents_list.allow_tags = True


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

    list_display = ("text", "type")


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    """Вопрос."""

    list_display = ("current_question", "next_question", "answer")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password'
            )
        }),
        ('Персональная информация', {
            'fields': (
                'first_name',
                'last_name',
                'patronymic',
                'email',
                'phone_number',
                'telegram_username',
                'residence'
            )
        }),
        ('Подопечный', {
            'fields': (
                'agent_status',
                'ward_first_name',
                'ward_last_name',
                'ward_patronymic',
                'birthday',
            )
        }),
        ('Статус', {
            'fields': (
                'is_active',
                'is_superuser',
                'date_joined',
                'last_login'
            )
        })
    )
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'telegram_username'
    )
