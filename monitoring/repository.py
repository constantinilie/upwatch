"""Nivelul de acces la date pentru Monitor (echivalent NivelAccesDate / MonitorAccessor).

Singurul loc care face query-uri pe Monitor prin ORM. Fără reguli de business.
"""
from django.db.models import Count

from .models import Monitor


def _with_details():
    return Monitor.objects.select_related("user").annotate(incident_count=Count("incidents"))


def get_all():
    """Toate monitoarele, cu proprietarul și numărul de incidente."""
    return _with_details().order_by("user__email", "name")


def get_by_id(pk):
    """Un monitor după id, sau None dacă nu există."""
    return _with_details().filter(pk=pk).first()


def add(data):
    """Adaugă un monitor nou (AddEntity)."""
    return Monitor.objects.create(**data)


def update(monitor, data):
    """Actualizează un monitor existent (UpdateEntity)."""
    for field, value in data.items():
        setattr(monitor, field, value)
    monitor.save()
    return monitor
