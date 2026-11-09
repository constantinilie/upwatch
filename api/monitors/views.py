"""Controllerul pentru Monitor (echivalent MonitoareController din ASP.NET Web API).

Clientul vede doar monitoarele lui; datele vin prin monitoring/services.py → repository.py,
iar modelul bazei de date (Monitor) e mapat automat în modelul controllerului (MonitorSummary).
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring import services as monitoring_services

from .mapping import to_summary
from .serializers import MonitorSummarySerializer


class MonitorListAPIView(APIView):
    """/api/v1/monitors/"""

    def get(self, request):
        """Get: monitoarele clientului; opțional ?status=pending|up|down|paused și ?search=text (nume, URL)."""
        monitors = monitoring_services.monitor_list_for_user(
            request.user, request.query_params.get("status"), request.query_params.get("search")
        )
        summaries = [to_summary(monitor) for monitor in monitors]
        return Response(MonitorSummarySerializer(summaries, many=True).data)


class MonitorDetailAPIView(APIView):
    """/api/v1/monitors/<id>/"""

    def get(self, request, pk):
        """Get(int id): un monitor al clientului. 404 și dacă monitorul există, dar e al altui client."""
        monitor = monitoring_services.monitor_get_for_user(pk, request.user)
        if monitor is None:
            return Response({"detail": f"Monitorul cu id {pk} nu există."}, status=status.HTTP_404_NOT_FOUND)
        return Response(MonitorSummarySerializer(to_summary(monitor)).data)
