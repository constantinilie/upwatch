"""Logica de business pentru User. Accesul la date se face prin repository.py."""
from django.core.exceptions import ValidationError

from . import repository

STATUS_FILTERS = {"active": True, "inactive": False}


def client_list(search=None, status=None):
    """Clienții, cu căutare după email / nume și filtru activ / inactiv."""
    return repository.get_clients(search=(search or "").strip() or None, is_active=STATUS_FILTERS.get(status))


def client_get(pk):
    return repository.get_client_by_id(pk)


def client_set_active(user, is_active):
    """Activează / dezactivează contul unui client. Un cont inactiv nu se mai poate autentifica.

    Regulă: din back office se gestionează doar clienții, nu conturile de staff.
    """
    if user.is_staff:
        raise ValidationError("Conturile de staff nu se gestionează de aici.")
    return repository.set_active(user, is_active)


def client_count():
    return repository.count_clients()


def all_client_list():
    return repository.get_all_clients()


def active_client_list():
    return repository.get_active_clients()
