from django.urls import path

from . import views

urlpatterns = [
    path("", views.MonitorListAPIView.as_view(), name="monitor_list"),
    path("<int:pk>/", views.MonitorDetailAPIView.as_view(), name="monitor_detail"),
]
