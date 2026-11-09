"""Maparea automată Monitor (modelul bazei de date) → MonitorSummary (modelul controllerului).

Câmpurile cu același nume (id, name, url, status, last_checked_at, incident_count) sunt copiate automat;
aici se declară doar regulile pentru câmpurile care diferă.
"""
from automapper import create_mapper

from monitoring.models import Monitor

from .summary import MonitorSummary

mapper = create_mapper()
mapper.add(Monitor, MonitorSummary, fields_mapping={"type": "Monitor.monitor_type"})


def to_summary(monitor):
    # is_paused e valoarea inversă a lui is_active, deci se calculează pentru fiecare monitor
    return mapper.map(monitor, fields_mapping={"is_paused": not monitor.is_active})
