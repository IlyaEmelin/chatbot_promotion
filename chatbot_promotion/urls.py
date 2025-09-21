from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("webhook/", include("telegram_bot.urls")),
    path("api/", include("api.urls")),
]
