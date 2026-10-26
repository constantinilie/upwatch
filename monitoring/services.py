"""Logica de business pentru Monitor. Apelată din views.py; accesul la date se face prin repository.py.

Deocamdată operațiile doar deleagă la repository; aici vor intra regulile aplicației
(ex. limita de monitoare din planul utilizatorului, scrierea în AuditLog).
"""
from . import repository


def monitor_list():
    """Index: toate monitoarele."""
    return repository.get_all()


def monitor_get(pk):
    """Details / Edit: un monitor după id, sau None."""
    return repository.get_by_id(pk)


def monitor_create(data):
    """Create: `data` = form.cleaned_data."""
    return repository.add(data)


def monitor_update(monitor, data):
    """Edit: `data` = form.cleaned_data."""
    return repository.update(monitor, data)
