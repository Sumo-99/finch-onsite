from django.urls import path

from .views import health_check, intake_extract

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("intake-extract/", intake_extract, name="intake-extract"),
]
