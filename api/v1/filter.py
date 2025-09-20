from rest_framework.filters import BaseFilterBackend


class SurveyFilterBackend(BaseFilterBackend):
    """Кастомный фильтр для опросов"""

    def filter_queryset(self, request, queryset, view):
        statuses = request.query_params.getlist("statuses")
        if statuses:
            queryset = queryset.filter(status__in=statuses)

        return queryset
