"""Logica de business pentru paginile de status. Accesul la date se face prin repository.py."""
from django.core.exceptions import ValidationError

from . import repository


def status_page_list():
    return repository.get_all()


def status_page_get(pk):
    return repository.get_by_id(pk)


def status_page_set_public(status_page, is_public):
    """Publică / retrage o pagină de status (ex. retragerea unei pagini cu conținut problematic)."""
    if status_page.is_public == is_public:
        state = "publică" if is_public else "retrasă"
        raise ValidationError(f"Pagina „{status_page.title}” este deja {state}.")
    return repository.update(status_page, is_public=is_public)


def status_page_delete(status_page):
    """Hard delete. Safe because no history (incidents, checks, invoices) depends on a status page;
    only the page-monitor links disappear, the monitors themselves stay.
    A public page must be withdrawn first, so visitors don't hit a 404 by surprise."""
    if status_page.is_public:
        raise ValidationError(f"Pagina „{status_page.title}” este publică. Retrage-o înainte de a o șterge.")
    repository.delete(status_page)
