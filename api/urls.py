from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "api"

urlpatterns = [
    path("auth/token/", views.LoginAPIView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", views.MeAPIView.as_view(), name="me"),
]
