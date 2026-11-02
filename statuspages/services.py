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
