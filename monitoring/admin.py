from django.contrib import admin

from alerts.models import MonitorAlertChannel

from .models import CheckResult, Incident, Monitor


class MonitorAlertChannelInline(admin.TabularInline):
    model = MonitorAlertChannel
    extra = 0


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "monitor_type", "url", "interval_sec", "status", "is_active", "last_checked_at"]
    list_filter = ["status", "monitor_type", "is_active"]
    search_fields = ["name", "url", "user__email"]
    autocomplete_fields = ["user"]
    inlines = [MonitorAlertChannelInline]


@admin.register(CheckResult)
class CheckResultAdmin(admin.ModelAdmin):
    list_display = ["monitor", "checked_at", "is_up", "status_code", "response_time_ms"]
    list_filter = ["is_up", "monitor"]
    date_hierarchy = "checked_at"
    list_select_related = ["monitor"]


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ["monitor", "status", "cause", "started_at", "resolved_at", "duration_sec"]
    list_filter = ["status"]
    date_hierarchy = "started_at"
    list_select_related = ["monitor"]
