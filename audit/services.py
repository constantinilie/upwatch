"""Logica pentru jurnalul de audit. Jurnalul se citește din back office, nu se modifică."""
from . import repository


def entry_list(action=None, search=None):
    return repository.get_entries(action or None, (search or "").strip() or None)


def action_list():
    return list(repository.get_actions())
