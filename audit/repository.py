"""Nivelul de acces la date pentru jurnalul de audit (doar citire)."""
from .models import AuditLog


def get_entries(action=None, search=None):
    entries = AuditLog.objects.select_related("user").order_by("-created_at")
    if action:
        entries = entries.filter(action=action)
    if search:
        entries = entries.filter(user__email__icontains=search)
    return entries


def get_actions():
    """Acțiunile distincte din jurnal, pentru filtru."""
    return AuditLog.objects.order_by("action").values_list("action", flat=True).distinct()
