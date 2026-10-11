from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "action", "entity_type", "entity_id", "ip_address"]
    list_filter = ["action", "entity_type"]
    search_fields = ["action", "entity_id", "user__email"]
    date_hierarchy = "created_at"

    # jurnalul e doar pentru citire
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
