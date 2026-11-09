"""Modelul returnat de API pentru un monitor (diferit de modelul tabelei monitoring_monitor)."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MonitorSummary:
    """Rezumatul unui monitor, cât să fie afișat într-o listă din panoul clientului.

    Față de modelul Monitor: are doar 8 câmpuri, `type` în loc de `monitor_type`,
    `is_paused` în loc de `is_active` și `incident_count` calculat din tabela de incidente.
    """

    id: int
    name: str
    url: str
    type: str
    status: str
    is_paused: bool
    last_checked_at: datetime | None
    incident_count: int
