"""Nivelul de acces la date pentru billing (Plan, Feature, Subscription, Invoice).

Singurul loc care face query-uri pe modelele din billing prin ORM. Fără reguli de business.
"""
from django.db import transaction
from django.db.models import Count, Q

from .models import Feature, Invoice, Plan, Subscription

_ACTIVE = Q(subscriptions__status=Subscription.Status.ACTIVE)


# ---------------------------------------------------------------- Plan

def _plans_with_details():
    """Planurile cu feature-urile (prefetch: un plan are mai multe) și numărul de abonamente active."""
    return Plan.objects.prefetch_related("features").annotate(
        active_subscription_count=Count("subscriptions", filter=_ACTIVE)
    )


def get_all_plans():
    return _plans_with_details().order_by("sort_order", "name")


def get_plan_by_id(pk):
    return _plans_with_details().filter(pk=pk).first()


def count_active_subscriptions_for_plan(plan):
    return Subscription.objects.filter(plan=plan, status=Subscription.Status.ACTIVE).count()


@transaction.atomic
def add_plan(data):
    """Adaugă un plan; `features` se salvează în tabela de legătură PlanFeature."""
    data = dict(data)
    features = data.pop("features", [])
    plan = Plan.objects.create(**data)
    plan.features.set(features)
    return plan


@transaction.atomic
def update_plan(plan, data):
    data = dict(data)
    features = data.pop("features", None)
    for field, value in data.items():
        setattr(plan, field, value)
    plan.save()
    if features is not None:
        plan.features.set(features)
    return plan


# ---------------------------------------------------------------- Feature

def get_all_features():
    """Feature-urile, cu planurile care le includ."""
    return Feature.objects.prefetch_related("plans").order_by("code")


def get_feature_by_id(pk):
    return Feature.objects.filter(pk=pk).first()


def add_feature(data):
    return Feature.objects.create(**data)


def update_feature(feature, data):
    for field, value in data.items():
        setattr(feature, field, value)
    feature.save()
    return feature


def get_active_plans():
    return Plan.objects.filter(is_active=True).order_by("sort_order", "name")


# ---------------------------------------------------------------- Subscription

def get_all_subscriptions(status=None):
    """Abonamentele, cu clientul și planul (select_related: fiecare abonament are un user și un plan)."""
    subscriptions = Subscription.objects.select_related("user", "plan").order_by("-created_at")
    if status:
        subscriptions = subscriptions.filter(status=status)
    return subscriptions


def get_subscription_by_id(pk):
    return Subscription.objects.select_related("user", "plan").filter(pk=pk).first()


def get_subscriptions_for_user(user):
    return Subscription.objects.select_related("plan").filter(user=user).order_by("-created_at")


def get_all_invoices(status=None, search=None):
    """Facturile, cu clientul și planul abonamentului (select_related pe FK-uri)."""
    invoices = Invoice.objects.select_related("user", "subscription__plan").order_by("-issued_at")
    if status:
        invoices = invoices.filter(status=status)
    if search:
        invoices = invoices.filter(Q(number__icontains=search) | Q(user__email__icontains=search))
    return invoices


def get_invoice_by_id(pk):
    return Invoice.objects.select_related("user", "subscription__plan").filter(pk=pk).first()


def count_invoices_by_status():
    rows = Invoice.objects.values("status").annotate(total=Count("id"))
    return {row["status"]: row["total"] for row in rows}


def update_invoice(invoice, **fields):
    for field, value in fields.items():
        setattr(invoice, field, value)
    invoice.save(update_fields=list(fields))
    return invoice


def get_invoices_for_user(user):
    return Invoice.objects.filter(user=user).order_by("-issued_at")


def get_active_subscription_for_user(user):
    return Subscription.objects.select_related("plan").filter(user=user, status=Subscription.Status.ACTIVE).first()


def count_subscriptions_by_status():
    """{status: număr} pentru filtrele din listă."""
    rows = Subscription.objects.values("status").annotate(total=Count("id"))
    return {row["status"]: row["total"] for row in rows}


def add_subscription(**fields):
    return Subscription.objects.create(**fields)


def update_subscription(subscription, **fields):
    for field, value in fields.items():
        setattr(subscription, field, value)
    subscription.save(update_fields=list(fields))
    return subscription


def count_active_subscriptions():
    return Subscription.objects.filter(status=Subscription.Status.ACTIVE).count()


def get_active_subscriptions():
    """Abonamentele active, cu planul încărcat (select_related: fiecare abonament are un singur plan)."""
    return Subscription.objects.filter(status=Subscription.Status.ACTIVE).select_related("plan")
