from django.urls import path

from .views import AuthTokenView, CaseReportView, health_check, intake_extract

urlpatterns = [
    path("auth/token/", AuthTokenView.as_view(), name="auth-token"),
    path("health/", health_check, name="health-check"),
    path("cases/<int:case_id>/report/", CaseReportView.as_view(), name="case-report"),
    path("intake-extract/", intake_extract, name="intake-extract"),
]
