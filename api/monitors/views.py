"""Controllerul pentru Monitor (echivalent MonitoareController din ASP.NET Web API).

Clientul vede doar monitoarele lui; datele vin prin monitoring/services.py → repository.py,
iar MonitorSummarySerializer mapează modelul bazei de date (Monitor) în răspunsul API-ului.
La Post / Put, MonitorSerializer validează body-ul și formează răspunsul.
"""
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring import services as monitoring_services

from .serializers import MonitorSerializer, MonitorSummarySerializer


def _not_found(pk):
    return Response({"detail": f"Monitorul cu id {pk} nu există."}, status=status.HTTP_404_NOT_FOUND)


def _save(save, *args):
    """Rulează create / update din services; o regulă de business încălcată devine 400 cu erorile pe câmpuri."""
    try:
        return save(*args)
    except ValidationError as error:
        raise serializers.ValidationError(serializers.as_serializer_error(error))


class MonitorListAPIView(APIView):
    """/api/v1/monitors/"""

    def get(self, request):
        """Get: monitoarele clientului; opțional ?status=pending|up|down|paused și ?search=text (nume, URL)."""
        monitors = monitoring_services.monitor_list_for_user(
            request.user, request.query_params.get("status"), request.query_params.get("search")
        )
        return Response(MonitorSummarySerializer(monitors, many=True).data)

    def post(self, request):
        """Post: adaugă un monitor pentru client → 201 cu monitorul creat, sau 400 cu erorile."""
        serializer = MonitorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        monitor = _save(monitoring_services.monitor_create_for_user, request.user, serializer.validated_data)
        monitor = monitoring_services.monitor_get_for_user(monitor.pk, request.user)  # recitit, cu incident_count
        location = reverse("api:monitor_detail", args=[monitor.pk])
        return Response(MonitorSerializer(monitor).data, status=status.HTTP_201_CREATED, headers={"Location": location})


class MonitorDetailAPIView(APIView):
    """/api/v1/monitors/<id>/"""

    def get(self, request, pk):
        """Get(int id): un monitor al clientului. 404 și dacă monitorul există, dar e al altui client."""
        monitor = monitoring_services.monitor_get_for_user(pk, request.user)
        if monitor is None:
            return _not_found(pk)
        return Response(MonitorSummarySerializer(monitor).data)

    def put(self, request, pk):
        """Put: actualizează un monitor al clientului → 200 cu monitorul actualizat, 400 sau 404."""
        monitor = monitoring_services.monitor_get_for_user(pk, request.user)
        if monitor is None:
            return _not_found(pk)
        serializer = MonitorSerializer(monitor, data=request.data)
        serializer.is_valid(raise_exception=True)
        monitor = _save(monitoring_services.monitor_update_for_user, monitor, serializer.validated_data)
        return Response(MonitorSerializer(monitor).data)

    def delete(self, request, pk):
        """Delete: soft delete of a client's monitor → 204 without body, or 404.

        The row stays in the database (is_deleted=True) together with its incidents and checks;
        afterwards Get / Get(id) / Put no longer find it and answer 404."""
        monitor = monitoring_services.monitor_get_for_user(pk, request.user)
        if monitor is None:
            return _not_found(pk)
        _save(monitoring_services.monitor_delete, monitor)
        return Response(status=status.HTTP_204_NO_CONTENT)
