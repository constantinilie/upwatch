from django.contrib import admin

from .models import Feature, Invoice, Plan, PlanFeature, Subscription


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 1


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "price_monthly", "price_yearly", "max_monitors", "min_check_interval_sec", "is_active"]
    list_editable = ["is_active"]
    inlines = [PlanFeatureInline]


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ["code", "name"]
    search_fields = ["code", "name"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "billing_cycle", "status", "current_period_start", "current_period_end", "cancel_at_period_end"]
    list_filter = ["status", "plan", "billing_cycle"]
    search_fields = ["user__email"]
    autocomplete_fields = ["user"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["number", "user", "amount", "currency", "status", "billing_cycle", "issued_at", "paid_at"]
    list_filter = ["status", "billing_cycle"]
    search_fields = ["number", "user__email"]
    date_hierarchy = "issued_at"
