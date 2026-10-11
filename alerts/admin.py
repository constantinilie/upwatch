from django.contrib import admin

from .models import AlertChannel, AlertEvent


@admin.register(AlertChannel)
class AlertChannelAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "channel_type", "target", "is_active"]
    list_filter = ["channel_type", "is_active"]
    search_fields = ["name", "target", "user__email"]
    autocomplete_fields = ["user"]


@admin.register(AlertEvent)
class AlertEventAdmin(admin.ModelAdmin):
    list_display = ["incident", "alert_channel", "event_type", "status", "sent_at"]
    list_filter = ["event_type", "status"]
    date_hierarchy = "sent_at"
