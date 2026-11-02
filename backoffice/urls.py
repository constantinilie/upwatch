from django.urls import path

from . import views

app_name = "backoffice"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Catalog
    path("plans/", views.plan_list, name="plan_list"),
    path("plans/new/", views.plan_create, name="plan_create"),
    path("plans/<int:pk>/", views.plan_detail, name="plan_detail"),
    path("plans/<int:pk>/edit/", views.plan_update, name="plan_update"),
    path("features/", views.feature_list, name="feature_list"),
    path("features/new/", views.feature_create, name="feature_create"),
    path("features/<int:pk>/edit/", views.feature_update, name="feature_update"),
    # Clienți
    path("clients/", views.client_list, name="client_list"),
    path("clients/<int:pk>/", views.client_detail, name="client_detail"),
    path("clients/<int:pk>/toggle-active/", views.client_toggle_active, name="client_toggle_active"),
    # Abonamente
    path("subscriptions/", views.subscription_list, name="subscription_list"),
    path("subscriptions/new/", views.subscription_create, name="subscription_create"),
    path("subscriptions/<int:pk>/cancel/", views.subscription_cancel, name="subscription_cancel"),
    # Facturi
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/mark-paid/", views.invoice_mark_paid, name="invoice_mark_paid"),
    path("invoices/<int:pk>/mark-failed/", views.invoice_mark_failed, name="invoice_mark_failed"),
    # Supraveghere
    path("monitors/", views.monitor_list, name="monitor_list"),
    path("monitors/new/", views.monitor_create, name="monitor_create"),
    path("monitors/<int:pk>/", views.monitor_detail, name="monitor_detail"),
    path("monitors/<int:pk>/edit/", views.monitor_update, name="monitor_update"),
    path("monitors/<int:pk>/toggle-active/", views.monitor_toggle_active, name="monitor_toggle_active"),
    path("incidents/", views.incident_list, name="incident_list"),
    path("status-pages/", views.status_page_list, name="status_page_list"),
    path("status-pages/<int:pk>/", views.status_page_detail, name="status_page_detail"),
    path("status-pages/<int:pk>/toggle-public/", views.status_page_toggle_public, name="status_page_toggle_public"),
    path("audit/", views.audit_list, name="audit_list"),
]
