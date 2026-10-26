from django.urls import path
from . import views

app_name = "monitoring"
urlpatterns = [
    path("", views.monitor_list, name="monitor_list"),                 # Index
    path("<int:pk>/", views.monitor_detail, name="monitor_detail"),    # Details
    path("new/", views.monitor_create, name="monitor_create"),         # Create
    path("<int:pk>/edit/", views.monitor_update, name="monitor_update"),  # Edit
]