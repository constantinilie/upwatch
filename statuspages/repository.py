"""Nivelul de acces la date pentru paginile de status. Singurul loc care face query-uri pe StatusPage prin ORM."""
from django.db.models import Count, Prefetch

from .models import StatusPage, StatusPageMonitor


def _with_details():
    return StatusPage.objects.select_related("user").annotate(monitor_count=Count("page_monitors"))


def get_all():
    return _with_details().order_by("title")


def get_by_id(pk):
    """O pagină, cu monitoarele ei (în ordinea de afișare) și proprietarul fiecărui monitor."""
    entries = StatusPageMonitor.objects.select_related("monitor").order_by("sort_order")
    return (
        _with_details()
        .prefetch_related(Prefetch("page_monitors", queryset=entries))
        .filter(pk=pk)
        .first()
    )


def update(status_page, **fields):
    for field, value in fields.items():
        setattr(status_page, field, value)
    status_page.save(update_fields=[*fields, "updated_at"])
    return status_page
