"""Logica de business pentru monitoring. Accesul la date se face prin repository.py.

Aici intră regulile aplicației (ex. pauza unui monitor, limitele de monitoare din planul clientului).
"""
from django.core.exceptions import ValidationError

from billing import services as billing_services

from . import repository
from .models import Incident, Monitor


# ---------------------------------------------------------------- Monitor

def monitor_list(status=None, search=None):
    """Index: monitoarele, opțional filtrate după status și căutare (nume, URL, email proprietar)."""
    if status not in Monitor.Status.values:
        status = None
    return repository.get_all(status, (search or "").strip() or None)


def monitor_list_for_user(user, status=None, search=None):
    """Monitoarele unui client (pagina clientului din back office, API-ul clientului)."""
    if status not in Monitor.Status.values:
        status = None
    return repository.get_by_user(user, status, (search or "").strip() or None)


def monitor_get(pk):
    """Details / Edit: un monitor după id, sau None."""
    return repository.get_by_id(pk)


def monitor_get_for_user(pk, user):
    """Un monitor al clientului după id, sau None (inclusiv dacă monitorul e al altui client)."""
    return repository.get_by_id_for_user(pk, user)


def monitor_create(data):
    """Create: `data` = form.cleaned_data."""
    return repository.add(data)


def monitor_update(monitor, data):
    """Edit: `data` = form.cleaned_data."""
    return repository.update(monitor, data)


def _active_plan(user):
    """Planul abonamentului activ al clientului; fără abonament activ nu poate crea / modifica monitoare."""
    subscription = billing_services.active_subscription_for_user(user)
    if subscription is None:
        raise ValidationError("Nu ai un abonament activ. Alege un plan ca să poți adăuga monitoare.")
    return subscription.plan


def _check_interval(plan, interval_sec):
    minimum = plan.min_check_interval_sec
    if interval_sec < minimum:
        raise ValidationError({"interval_sec": f"Planul {plan.name} permite un interval de minim {minimum} de secunde."})


def monitor_create_for_user(user, data):
    """Create din API-ul clientului: proprietarul e clientul, iar limitele vin din planul lui.

    Reguli: abonament activ, cel mult plan.max_monitors monitoare, interval >= plan.min_check_interval_sec.
    """
    plan = _active_plan(user)
    if repository.count_by_user(user) >= plan.max_monitors:
        raise ValidationError(
            f"Ai atins limita de {plan.max_monitors} monitoare a planului {plan.name}. Alege un plan superior."
        )
    _check_interval(plan, data.get("interval_sec", Monitor._meta.get_field("interval_sec").default))
    return repository.add({**data, "user": user})


def monitor_update_for_user(monitor, data):
    """Update din API-ul clientului: aceleași reguli de interval ca la creare."""
    plan = _active_plan(monitor.user)
    _check_interval(plan, data.get("interval_sec", monitor.interval_sec))
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


def monitor_delete(monitor):
    """Soft delete. A monitor cannot be hard-deleted: incidents, check results, alert events and
    status page entries reference it with CASCADE, so a physical delete would wipe its history."""
    if monitor.is_deleted:
        raise ValidationError(f"Monitorul „{monitor.name}” este deja șters.")
    return repository.soft_delete(monitor)


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
