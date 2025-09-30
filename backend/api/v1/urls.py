from django.urls import path, include
from rest_framework_nested import routers

from .views import SurveyViewSet, DocumentViewSet, CommentViewSet

router = routers.DefaultRouter()
router.register(r"surveys", SurveyViewSet, basename="survey")
surveys_router = routers.NestedSimpleRouter(
    router,
    parent_prefix=r"surveys",
    lookup="survey",
)
surveys_router.register(r"docs", DocumentViewSet, basename="document")
surveys_router.register(r"comments", CommentViewSet, basename="comment")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(surveys_router.urls)),
]
