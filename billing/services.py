"""Logica de business pentru billing. Accesul la date se face prin repository.py."""
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from . import repository
from .models import BillingCycle, Invoice, Subscription

PERIOD_LENGTH = {BillingCycle.MONTHLY: timedelta(days=30), BillingCycle.YEARLY: timedelta(days=365)}


# ---------------------------------------------------------------- Plan

def plan_list():
    return repository.get_all_plans()


def plan_get(pk):
    return repository.get_plan_by_id(pk)


def plan_create(data):
    return repository.add_plan(data)


def plan_update(plan, data):
    """Regulă: un plan cu abonamente active nu poate fi dezactivat (clienții ar rămâne pe un plan inexistent în ofertă)."""
    if plan.is_active and not data.get("is_active", True):
        active = repository.count_active_subscriptions_for_plan(plan)
        if active:
            raise ValidationError(
                f"Planul nu poate fi dezactivat: are {active} abonamente active.", code="plan_in_use"
            )
    return repository.update_plan(plan, data)


# ---------------------------------------------------------------- Feature

def feature_list():
    return repository.get_all_features()


def feature_get(pk):
    return repository.get_feature_by_id(pk)


def feature_create(data):
    return repository.add_feature(data)


def feature_update(feature, data):
    return repository.update_feature(feature, data)


def active_plan_list():
    return repository.get_active_plans()


# ---------------------------------------------------------------- Subscription

def subscription_list(status=None):
    return repository.get_all_subscriptions(status)


def subscription_get(pk):
    return repository.get_subscription_by_id(pk)


def subscription_list_for_user(user):
    return repository.get_subscriptions_for_user(user)


def invoice_list_for_user(user):
    return repository.get_invoices_for_user(user)


def subscription_status_counts():
    return repository.count_subscriptions_by_status()


def period_end_for(plan, billing_cycle, start):
    """Sfârșitul perioadei: planul gratuit nu expiră, cel plătit ține o lună sau un an."""
    if plan.is_free:
        return None
    return start + PERIOD_LENGTH[billing_cycle]


@transaction.atomic
def subscription_create(user, plan, billing_cycle, start_date=None):
    """Atribuie un plan unui client.

    Reguli: clientul are cel mult un abonament activ, deci cel vechi se anulează;
    nu se recreează exact același abonament; perioada se calculează după ciclu.
    """
    start = timezone.now()
    if start_date and start_date != timezone.localdate():
        start = timezone.make_aware(datetime.combine(start_date, time.min))

    current = repository.get_active_subscription_for_user(user)
    if current:
        if current.plan_id == plan.pk and current.billing_cycle == billing_cycle:
            raise ValidationError(f"Clientul are deja abonamentul activ {plan.name} ({current.get_billing_cycle_display()}).")
        repository.update_subscription(current, status=Subscription.Status.CANCELED, canceled_at=timezone.now())

    return repository.add_subscription(
        user=user,
        plan=plan,
        billing_cycle=billing_cycle,
        status=Subscription.Status.ACTIVE,
        current_period_start=start,
        current_period_end=period_end_for(plan, billing_cycle, start),
    )


def subscription_cancel(subscription):
    if subscription.status != Subscription.Status.ACTIVE:
        raise ValidationError("Doar un abonament activ poate fi anulat.")
    return repository.update_subscription(subscription, status=Subscription.Status.CANCELED, canceled_at=timezone.now())


# ---------------------------------------------------------------- Invoice

def invoice_list(status=None, search=None):
    if status not in Invoice.Status.values:
        status = None
    return repository.get_all_invoices(status, (search or "").strip() or None)


def invoice_get(pk):
    return repository.get_invoice_by_id(pk)


def invoice_status_counts():
    return repository.count_invoices_by_status()


def invoice_mark_paid(invoice):
    """Plata (simulată) a fost confirmată. O factură plătită nu se mai modifică."""
    if invoice.status == Invoice.Status.PAID:
        raise ValidationError(f"Factura {invoice.number} este deja plătită.")
    return repository.update_invoice(invoice, status=Invoice.Status.PAID, paid_at=timezone.now())


def invoice_mark_failed(invoice):
    """Plata a eșuat. Se poate marca doar o factură în așteptare."""
    if invoice.status != Invoice.Status.PENDING:
        raise ValidationError(f"Doar o factură în așteptare poate fi marcată ca eșuată ({invoice.number} este {invoice.get_status_display().lower()}).")
    return repository.update_invoice(invoice, status=Invoice.Status.FAILED, paid_at=None)


# ---------------------------------------------------------------- Dashboard

def active_subscription_count():
    return repository.count_active_subscriptions()


def monthly_recurring_revenue():
    """MRR: venitul lunar din abonamentele active (cele anuale contează cu 1/12 din preț)."""
    total = Decimal("0")
    for subscription in repository.get_active_subscriptions():
        if subscription.billing_cycle == BillingCycle.YEARLY:
            total += subscription.plan.price_yearly / 12
        else:
            total += subscription.plan.price_monthly
    return total.quantize(Decimal("0.01"))
