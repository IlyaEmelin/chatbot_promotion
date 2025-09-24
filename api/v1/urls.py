from django.urls import path, include
from rest_framework_nested import routers

from .views import SurveyViewSet, DocumentViewSet

router = routers.DefaultRouter()
router.register(r"surveys", SurveyViewSet, basename="survey")
docs_router = routers.NestedSimpleRouter(router, r"surveys", lookup="survey")
docs_router.register(r"docs", DocumentViewSet, basename="document")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(docs_router.urls)),
]
