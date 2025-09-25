import os
from urllib.parse import urlparse

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .constant import STATUS_CHOICES
from .models import Document, Survey


class StatusFilter(admin.SimpleListFilter):
    """Фильтр по статусу опроса."""

    title = 'Статус заявки'
    parameter_name = 'status'

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
    readonly_fields = ('image_preview', 'download_link')

    @admin.display(description='Предпросмотр')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}"'
                'style="max-height: 100px; max-width: 100px;" /></a>',
                obj.image, obj.image
            )
        return '—'

    @admin.display(description='Скачать')
    def download_link(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank" download>'
                'Скачать</a>',
                obj.image
            )
        return '—'


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user_info',
        'status_badge',
        'current_question',
        'documents_count',
        'created_at_formatted',
    )
    list_filter = (
        StatusFilter, 'created_at', 'current_question'
    )
    search_fields = (
        'user__email',
        'user__phone',
        'created_at'
    )
    readonly_fields = (
        'id',
        'user_info',
        'created_at',
        'updated_at',
        'questions_version_uuid',
        'result_display',
        'documents_list'
    )
    list_select_related = ('user', 'current_question')
    inlines = (DocumentInline,)

    @admin.display(description='Пользователь')
    def user_info(self, obj):
        user = obj.user
        phone = getattr(user, 'phone', '—')
        return format_html(
            '{} {}<br><small>Почта: {}<br>'
            'Телефон: {}</small>',
            user.first_name or '',
            user.last_name or '',
            user.email,
            phone
        )

    @admin.display(description='Статус')
    def status_badge(self, obj):
        status_colors = {
            'draft': 'gray',
            'new': 'blue',
            'waiting_docs': 'orange',
            'processing': 'purple',
            'completed': 'green'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: '
            'white; padding: 4px 8px; border-radius: '
            '12px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )

    @admin.display(description='Создана')
    def created_at_formatted(self, obj):
        return timezone.localtime(
            obj.created_at).strftime('%d.%m.%Y %H:%M')

    @admin.display(description='Документы')
    def documents_count(self, obj):
        return obj.docs.count()

    @admin.display(description='Результаты опроса')
    def result_display(self, obj):
        if obj.result:
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; '
                'border-radius: 5px; max-height: 300px; '
                'overflow: auto;">{}</pre>',
                str(obj.result)
            )
        return 'Нет данных'

    @admin.display(description='Загруженные документы')
    def documents_list(self, obj):
        documents = obj.docs.all()
        if not documents:
            return "Документы не загружены"

        html = '<div style="max-height: 200px; overflow-y: auto;">'
        for doc in documents:
            filename = os.path.basename(urlparse(doc.image).path)
            html += format_html(
                '''
                <div style="display: flex; align-items: '
                'center; margin-bottom: 10px; padding: 5px; background: '
                'white; border-radius: 3px;">
                    <a href="{}" target="_blank" style="margin-right: 10px;">
                        <img src="{}" style="max-height: 50px; '
                        'max-width: 50px;">
                    </a>
                    <div>
                        <div><strong>{}</strong></div>
                        <a href="{}" target="_blank" download>Скачать</a>
                    </div>
                </div>
                ''',
                doc.image, doc.image, filename, doc.image
            )
        html += '</div>'
        return format_html(html)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Документ."""

    list_display = ('survey_short', 'image_preview')

    @admin.display(description='Опрос')
    def survey_short(self, obj):
        return f'Опрос {obj.survey.id}'

    @admin.display(description='Изображение')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" '
                'style="max-height: 50px;" /></a>',
                obj.image, obj.image
            )
        return '—'
