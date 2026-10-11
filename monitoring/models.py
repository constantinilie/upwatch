from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Monitor(models.Model):
    """Ținta monitorizată: URL, tip, interval și starea curentă."""

    class Type(models.TextChoices):
        HTTP = "http", "HTTP"
        KEYWORD = "keyword", "Keyword"
        SSL = "ssl", "Certificat SSL"

    class Method(models.TextChoices):
        GET = "GET", "GET"
        HEAD = "HEAD", "HEAD"
        POST = "POST", "POST"

    class Status(models.TextChoices):
        PENDING = "pending", "În așteptare"
        UP = "up", "Up"
        DOWN = "down", "Down"
        PAUSED = "paused", "Pe pauză"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="monitors")
    name = models.CharField(max_length=100)
    monitor_type = models.CharField(max_length=10, choices=Type.choices, default=Type.HTTP)
    url = models.URLField(max_length=500)
    http_method = models.CharField(max_length=7, choices=Method.choices, default=Method.GET)
    expected_status_code = models.PositiveSmallIntegerField(default=200)
    keyword = models.CharField(max_length=200, blank=True)  # doar pentru tipul keyword
    request_headers = models.JSONField(default=dict, blank=True)
    interval_sec = models.PositiveIntegerField(default=300)
    timeout_sec = models.PositiveIntegerField(default=10)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    is_active = models.BooleanField(default=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_status_change_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    alert_channels = models.ManyToManyField(
        "alerts.AlertChannel", through="alerts.MonitorAlertChannel", related_name="monitors", blank=True
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            # folosit de scheduler pentru a găsi monitoarele de verificat
            models.Index(fields=["is_active", "last_checked_at"], name="monitor_due_idx"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(timeout_sec__lt=F("interval_sec")), name="monitor_timeout_lt_interval"),
            models.CheckConstraint(
                condition=~Q(monitor_type="keyword") | ~Q(keyword=""),
                name="monitor_keyword_required_for_keyword_type",
            ),
        ]

    def __str__(self):
        return self.name


class CheckResult(models.Model):
    """Rezultatul unei singure verificări a unui monitor."""

    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, related_name="check_results")
    checked_at = models.DateTimeField(default=timezone.now)
    is_up = models.BooleanField()
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-checked_at"]
        indexes = [
            models.Index(fields=["monitor", "-checked_at"], name="checkresult_monitor_time_idx"),
        ]

    def __str__(self):
        return f"{self.monitor} @ {self.checked_at:%Y-%m-%d %H:%M} – {'UP' if self.is_up else 'DOWN'}"


class Incident(models.Model):
    """Perioadă de nefuncționare: începe la up→down, se închide la down→up."""

    class Status(models.TextChoices):
        ONGOING = "ongoing", "În desfășurare"
        RESOLVED = "resolved", "Rezolvat"

    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, related_name="incidents")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ONGOING)
    cause = models.CharField(max_length=255, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)
    duration_sec = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["monitor", "-started_at"], name="incident_monitor_time_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(resolved_at__isnull=True) | Q(resolved_at__gte=F("started_at")),
                name="incident_resolved_after_started",
            ),
        ]

    def __str__(self):
        return f"{self.monitor} – {self.started_at:%Y-%m-%d %H:%M}"

    def resolve(self, when=None):
        self.resolved_at = when or timezone.now()
        self.duration_sec = int((self.resolved_at - self.started_at).total_seconds())
        self.status = self.Status.RESOLVED
