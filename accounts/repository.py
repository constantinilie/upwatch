"""Nivelul de acces la date pentru User. Singurul loc care face query-uri pe User prin ORM."""
from django.db.models import Count, Prefetch, Q

from billing.models import Subscription

from .models import User


def _clients_with_details():
    """Clienții (non-staff), cu numărul de monitoare și abonamentul activ încărcat dinainte.

    prefetch_related: un client are mai multe abonamente; păstrăm doar pe cel activ în `active_subscriptions`.
    """
    active = Subscription.objects.filter(status=Subscription.Status.ACTIVE).select_related("plan")
    return (
        User.objects.filter(is_staff=False)
        .annotate(monitor_count=Count("monitors", distinct=True))
        .prefetch_related(Prefetch("subscriptions", queryset=active, to_attr="active_subscriptions"))
    )


def get_clients(search=None, is_active=None):
    clients = _clients_with_details()
    if search:
        clients = clients.filter(
            Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )
    if is_active is not None:
        clients = clients.filter(is_active=is_active)
    return clients.order_by("email")


def get_client_by_id(pk):
    return _clients_with_details().filter(pk=pk).first()


def set_active(user, is_active):
    user.is_active = is_active
    user.save(update_fields=["is_active"])
    return user


def count_clients():
    """Numărul de clienți (utilizatori care nu sunt staff)."""
    return User.objects.filter(is_staff=False).count()


def get_all_clients():
    """Toți clienții (non-staff), pentru liste de selecție unde contează și cei dezactivați."""
    return User.objects.filter(is_staff=False).order_by("email")


def get_active_clients():
    """Clienții activi (non-staff), pentru liste de selecție."""
    return User.objects.filter(is_staff=False, is_active=True).order_by("email")
