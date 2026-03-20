from django.urls import path

from .views import CaseDetailView, CaseListCreateView, CaseStageAdvanceView, health_check

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("cases/", CaseListCreateView.as_view(), name="case-list-create"),
    path("cases/<int:case_id>/", CaseDetailView.as_view(), name="case-detail"),
    path("cases/<int:case_id>/stage/", CaseStageAdvanceView.as_view(), name="case-stage-advance"),
]
