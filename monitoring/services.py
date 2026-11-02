"""Logica de business pentru monitoring. Accesul la date se face prin repository.py.

Aici intră regulile aplicației (ex. pauza unui monitor, mai târziu limita de monitoare din plan).
"""
from django.core.exceptions import ValidationError

from . import repository
from .models import Incident, Monitor


# ---------------------------------------------------------------- Monitor

def monitor_list(status=None, search=None):
    """Index: monitoarele, opțional filtrate după status și căutare (nume, URL, email proprietar)."""
    if status not in Monitor.Status.values:
        status = None
    return repository.get_all(status, (search or "").strip() or None)


def monitor_list_for_user(user):
    """Monitoarele unui client (pagina clientului din back office)."""
    return repository.get_by_user(user)


def monitor_get(pk):
    """Details / Edit: un monitor după id, sau None."""
    return repository.get_by_id(pk)


def monitor_create(data):
    """Create: `data` = form.cleaned_data."""
    return repository.add(data)


def monitor_update(monitor, data):
    """Edit: `data` = form.cleaned_data."""
    return repository.update(monitor, data)


def monitor_set_active(monitor, is_active):
    """Pune pe pauză / reactivează un monitor (ex. un monitor abuziv sau care țintește un site greșit).

    Un monitor pe pauză nu mai e verificat; la reactivare starea redevine „în așteptare” până la prima verificare.
    """
    if monitor.is_active == is_active:
        state = "activ" if is_active else "pe pauză"
        raise ValidationError(f"Monitorul „{monitor.name}” este deja {state}.")
    status = Monitor.Status.PENDING if is_active else Monitor.Status.PAUSED
    return repository.update(monitor, {"is_active": is_active, "status": status})


def monitor_status_counts():
    return repository.count_monitors_by_status()


def monitor_count():
    return repository.count_all()


def monitor_down_count():
    return repository.count_by_status(Monitor.Status.DOWN)


# ---------------------------------------------------------------- Incident

def incident_list(status=None):
    if status not in Incident.Status.values:
        status = None
    return repository.get_incidents(status)


def incident_list_for_monitor(monitor):
    return repository.get_incidents_for_monitor(monitor)


def incident_status_counts():
    return repository.count_incidents_by_status()


def ongoing_incident_count():
    return repository.count_ongoing_incidents()
