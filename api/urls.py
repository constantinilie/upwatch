"""Rutele API-ului, câte un subfolder pentru fiecare entitate (montate sub /api/v1/ în config/urls.py)."""
from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("auth/", include("api.auth.urls")),
]
