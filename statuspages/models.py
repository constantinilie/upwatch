from django.conf import settings
from django.db import models


class StatusPage(models.Model):
    """Pagină publică de status, accesibilă la /status/<slug>."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="status_pages")
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=60, unique=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    custom_domain = models.CharField(max_length=255, unique=True, null=True, blank=True)  # feature custom_domain
    show_branding = models.BooleanField(default=True)  # False doar cu feature remove_branding
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    monitors = models.ManyToManyField(
        "monitoring.Monitor", through="StatusPageMonitor", related_name="status_pages", blank=True
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class StatusPageMonitor(models.Model):
    """Ce monitoare apar pe o pagină de status, cu nume public și ordine."""

    status_page = models.ForeignKey(StatusPage, on_delete=models.CASCADE, related_name="page_monitors")
    monitor = models.ForeignKey("monitoring.Monitor", on_delete=models.CASCADE, related_name="page_entries")
    display_name = models.CharField(max_length=100, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        constraints = [
            models.UniqueConstraint(fields=["status_page", "monitor"], name="unique_status_page_monitor"),
        ]

    def __str__(self):
        return self.display_name or str(self.monitor)
