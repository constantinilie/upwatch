"""Serializerele pentru Monitor."""
from rest_framework import serializers

from monitoring.models import Monitor


class MonitorSerializer(serializers.ModelSerializer):
    """Un singur serializer pentru intrare și ieșire.

    - câmpurile editabile (name, url, monitor_type, ...) apar în răspuns și vor fi citite din body la POST / PUT;
    - câmpurile read_only (status, is_active, incident_count, ...) apar doar în răspuns;
    - proprietarul nu e expus: e mereu clientul din token (request.user).
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
