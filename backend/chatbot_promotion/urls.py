from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from api.custom_generator import DividedСategoriesSchemaGenerator


schema_view = get_schema_view(
    openapi.Info(
        title="ChatBOT API",
        default_version="v1",
        description="Документация для приложения чат-бота",
        contact=openapi.Contact(email="example@example.ru"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=DividedСategoriesSchemaGenerator,
)


urlpatterns = [
    path("pro-admin-dvizh/", admin.site.urls),
    path("telegram/webhook/", include("telegram_bot.urls")),
    path("api/", include("api.urls")),
    path(
        "swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
