from django.urls import path

from .views import create_survey, update_survey

urlpatterns = [
    path("surveys/", create_survey, name="create_survey"),
    path("surveys/", update_survey, name="update_survey"),
]
