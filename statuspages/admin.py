from django.contrib import admin

from .models import StatusPage, StatusPageMonitor


class StatusPageMonitorInline(admin.TabularInline):
    model = StatusPageMonitor
    extra = 1


@admin.register(StatusPage)
class StatusPageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "user", "is_public", "custom_domain", "show_branding"]
    list_filter = ["is_public", "show_branding"]
    search_fields = ["title", "slug", "user__email"]
    prepopulated_fields = {"slug": ["title"]}
    autocomplete_fields = ["user"]
    inlines = [StatusPageMonitorInline]
