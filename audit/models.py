from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Istoricul acțiunilor: cine, ce, pe ce obiect, când și de unde. Doar inserări."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    action = models.CharField(max_length=50)  # ex. monitor.created, subscription.upgraded
    entity_type = models.CharField(max_length=50, blank=True)  # ex. monitor
    entity_id = models.CharField(max_length=50, blank=True)
    changes = models.JSONField(default=dict, blank=True)  # {"interval_sec": [300, 60]}
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="auditlog_user_time_idx"),
            models.Index(fields=["entity_type", "entity_id"], name="auditlog_entity_idx"),
        ]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.user or '-'} {self.action}"
