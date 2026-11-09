"""Nivelul de acces la date pentru monitoring (echivalent NivelAccesDate / MonitorAccessor).

Singurul loc care face query-uri pe Monitor și Incident prin ORM. Fără reguli de business.
"""
from django.db.models import Count, Q

from .models import Incident, Monitor


# ---------------------------------------------------------------- Monitor

def _with_details():
    return Monitor.objects.select_related("user").annotate(incident_count=Count("incidents"))


def get_all(status=None, search=None):
    """Monitoarele, cu proprietarul și numărul de incidente; opțional filtrate după status / căutare."""
    monitors = _with_details()
    if status:
        monitors = monitors.filter(status=status)
    if search:
        monitors = monitors.filter(
            Q(name__icontains=search) | Q(url__icontains=search) | Q(user__email__icontains=search)
        )
    return monitors.order_by("user__email", "name")


def get_by_user(user, status=None, search=None):
    """Monitoarele unui client; opțional filtrate după status / căutare (nume, URL)."""
    monitors = _with_details().filter(user=user)
    if status:
        monitors = monitors.filter(status=status)
    if search:
        monitors = monitors.filter(Q(name__icontains=search) | Q(url__icontains=search))
    return monitors.order_by("name")


def get_by_id(pk):
    """Un monitor după id, sau None dacă nu există."""
    return _with_details().filter(pk=pk).first()


def get_by_id_for_user(pk, user):
    """Un monitor după id, doar dacă aparține clientului; altfel None."""
    return _with_details().filter(pk=pk, user=user).first()


def add(data):
    """Adaugă un monitor nou (AddEntity)."""
    return Monitor.objects.create(**data)


def update(monitor, data):
    """Actualizează un monitor existent (UpdateEntity)."""
    for field, value in data.items():
        setattr(monitor, field, value)
    monitor.save()
    return monitor


def count_all():
    return Monitor.objects.count()


def count_by_status(status):
    return Monitor.objects.filter(status=status).count()


def count_monitors_by_status():
    rows = Monitor.objects.values("status").annotate(total=Count("id"))
    return {row["status"]: row["total"] for row in rows}


# ---------------------------------------------------------------- Incident

def get_incidents(status=None):
    """Incidentele, cu monitorul și proprietarul lui (select_related pe FK-uri); cele în desfășurare primele."""
    incidents = Incident.objects.select_related("monitor__user")
    if status:
        incidents = incidents.filter(status=status)
    return incidents.order_by("status", "-started_at")  # "ongoing" < "resolved" alfabetic


def get_incidents_for_monitor(monitor):
    return Incident.objects.filter(monitor=monitor).order_by("-started_at")


def count_incidents_by_status():
    rows = Incident.objects.values("status").annotate(total=Count("id"))
    return {row["status"]: row["total"] for row in rows}


def count_ongoing_incidents():
    return Incident.objects.filter(status=Incident.Status.ONGOING).count()
