"""Serializerele pentru Monitor."""
from rest_framework import serializers

from monitoring.models import Monitor


class MonitorSummarySerializer(serializers.ModelSerializer):
    """Modelul returnat de Get și Get(id): rezumatul unui monitor, mapat automat din Monitor.

    ModelSerializer generează singur câmpurile cu același nume ca în model (id, name, url, status,
    last_checked_at); aici se declară doar cele care diferă de tabelă.
    """

    type = serializers.CharField(source="monitor_type")
    is_paused = serializers.SerializerMethodField()
    incident_count = serializers.IntegerField(read_only=True)  # adnotare din repository

    class Meta:
        model = Monitor
        fields = ["id", "name", "url", "type", "status", "is_paused", "last_checked_at", "incident_count"]

    def get_is_paused(self, monitor):
        return not monitor.is_active


class MonitorSerializer(serializers.ModelSerializer):
    """Un singur serializer pentru intrare și ieșire.

    - câmpurile editabile (name, url, monitor_type, ...) sunt citite din body la POST / PUT și apar în răspuns;
    - câmpurile read_only (status, is_active, incident_count, ...) apar doar în răspuns;
    - proprietarul nu e expus: e mereu clientul din token (request.user).

    Aici se validează doar forma datelor; limitele din planul clientului le verifică monitoring/services.py.
    """

    monitor_type_label = serializers.CharField(source="get_monitor_type_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    incident_count = serializers.IntegerField(read_only=True)  # adnotare din repository

    class Meta:
        model = Monitor
        fields = [
            "id",
            "name",
            "url",
            "monitor_type",
            "monitor_type_label",
            "keyword",
            "http_method",
            "expected_status_code",
            "interval_sec",
            "timeout_sec",
            "is_active",
            "status",
            "status_label",
            "incident_count",
            "last_checked_at",
            "last_status_change_at",
            "created_at",
            "updated_at",
        ]
        # pauza / reluarea schimbă și starea monitorului, deci is_active nu se editează direct
        read_only_fields = [
            "is_active", "status", "last_checked_at", "last_status_change_at", "created_at", "updated_at",
        ]

    def validate(self, attrs):
        # câmpurile lipsă din body se iau din monitorul existent (PUT) sau din valorile implicite ale modelului (POST)
        def value(field):
            if field in attrs:
                return attrs[field]
            if self.instance is not None:
                return getattr(self.instance, field)
            return Monitor._meta.get_field(field).get_default()

        errors = {}
        if value("monitor_type") == Monitor.Type.KEYWORD and not value("keyword"):
            errors["keyword"] = "Completează keyword-ul pentru un monitor de tip Keyword."
        if value("timeout_sec") >= value("interval_sec"):
            errors["timeout_sec"] = "Timeout-ul trebuie să fie mai mic decât intervalul de verificare."
        if errors:
            raise serializers.ValidationError(errors)
        return attrs
