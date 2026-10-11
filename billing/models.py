from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class BillingCycle(models.TextChoices):
    MONTHLY = "monthly", "Lunar"
    YEARLY = "yearly", "Anual"


class Feature(models.Model):
    """Funcționalitate activabilă per plan (feature flag), ex. webhook_alerts."""

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.name


class Plan(models.Model):
    """Free / Pro / Business: prețuri și limite."""

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="EUR")

    max_monitors = models.PositiveIntegerField()
    min_check_interval_sec = models.PositiveIntegerField()
    max_status_pages = models.PositiveIntegerField()
    max_alert_channels = models.PositiveIntegerField()
    log_retention_days = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    features = models.ManyToManyField(Feature, through="PlanFeature", related_name="plans", blank=True)

    class Meta:
        ordering = ["sort_order"]
        constraints = [
            models.CheckConstraint(condition=Q(price_monthly__gte=0), name="plan_price_monthly_gte_0"),
            models.CheckConstraint(condition=Q(price_yearly__gte=0), name="plan_price_yearly_gte_0"),
        ]

    def __str__(self):
        return self.name

    @property
    def is_free(self):
        return self.price_monthly == 0

    def price_for(self, billing_cycle):
        return self.price_yearly if billing_cycle == BillingCycle.YEARLY else self.price_monthly


class PlanFeature(models.Model):
    """Tabela de legătură M:N între Plan și Feature."""

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["plan", "feature"], name="unique_plan_feature"),
        ]

    def __str__(self):
        return f"{self.plan} – {self.feature}"


class Subscription(models.Model):
    """Abonamentul unui utilizator la un plan. Maxim unul activ per utilizator."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Activ"
        CANCELED = "canceled", "Anulat"
        EXPIRED = "expired", "Expirat"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    billing_cycle = models.CharField(max_length=10, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField(null=True, blank=True)  # NULL pentru planul Free
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="active"),
                name="one_active_subscription_per_user",
            ),
            models.CheckConstraint(
                condition=Q(current_period_end__isnull=True) | Q(current_period_end__gt=F("current_period_start")),
                name="subscription_period_end_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.user} – {self.plan} ({self.get_status_display()})"


class Invoice(models.Model):
    """Factură simulată, emisă la upgrade sau reînnoire."""

    class Status(models.TextChoices):
        PENDING = "pending", "În așteptare"
        PAID = "paid", "Plătită"
        FAILED = "failed", "Eșuată"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invoices")
    subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT, related_name="invoices")
    number = models.CharField(max_length=20, unique=True)  # ex. INV-2026-000123
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default="EUR")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    billing_cycle = models.CharField(max_length=10, choices=BillingCycle.choices)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    card_last4 = models.CharField(max_length=4, blank=True)  # simulat, ex. 4242
    issued_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_at"]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gte=0), name="invoice_amount_gte_0"),
            models.CheckConstraint(condition=Q(period_end__gt=F("period_start")), name="invoice_period_end_after_start"),
        ]

    def __str__(self):
        return self.number
