from django.conf import settings
from django.db import models
from django.utils import timezone


class AlertChannel(models.Model):
    """Destinație pentru alerte: o adresă de email sau un URL de webhook."""

    class Type(models.TextChoices):
        EMAIL = "email", "Email"
        WEBHOOK = "webhook", "Webhook"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="alert_channels")
    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=10, choices=Type.choices, default=Type.EMAIL)
    target = models.CharField(max_length=500)  # adresa de email sau URL-ul webhook-ului
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_channel_type_display()})"


class MonitorAlertChannel(models.Model):
    """Tabela de legătură M:N între Monitor și AlertChannel."""

    monitor = models.ForeignKey("monitoring.Monitor", on_delete=models.CASCADE)
    alert_channel = models.ForeignKey(AlertChannel, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["monitor", "alert_channel"], name="unique_monitor_alert_channel"),
        ]

    def __str__(self):
        return f"{self.monitor} → {self.alert_channel}"


class AlertEvent(models.Model):
    """O alertă trimisă pe un canal pentru un incident."""

    class EventType(models.TextChoices):
        DOWN = "down", "Down"
        UP = "up", "Up"

    class Status(models.TextChoices):
        SENT = "sent", "Trimisă"
        FAILED = "failed", "Eșuată"

    incident = models.ForeignKey("monitoring.Incident", on_delete=models.CASCADE, related_name="alert_events")
    alert_channel = models.ForeignKey(AlertChannel, on_delete=models.CASCADE, related_name="alert_events")
    event_type = models.CharField(max_length=4, choices=EventType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SENT)
    error_message = models.CharField(max_length=500, blank=True)
    sent_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.get_event_type_display()} → {self.alert_channel} ({self.get_status_display()})"
