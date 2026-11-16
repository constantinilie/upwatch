"""Logica de business pentru User. Accesul la date se face prin repository.py."""
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import transaction

from billing import services as billing_services
from billing.models import BillingCycle

from . import repository

STATUS_FILTERS = {"active": True, "inactive": False}


def client_list(search=None, status=None):
    """Clienții, cu căutare după email / nume și filtru activ / inactiv."""
    return repository.get_clients(search=(search or "").strip() or None, is_active=STATUS_FILTERS.get(status))


def client_get(pk):
    return repository.get_client_by_id(pk)


def client_set_active(user, is_active):
    """Activează / dezactivează contul unui client. Un cont inactiv nu se mai poate autentifica.

    Regulă: din back office se gestionează doar clienții, nu conturile de staff.
    """
    if user.is_staff:
        raise ValidationError("Conturile de staff nu se gestionează de aici.")
    return repository.set_active(user, is_active)


def client_count():
    return repository.count_clients()


def all_client_list():
    return repository.get_all_clients()


def active_client_list():
    return repository.get_active_clients()


@transaction.atomic
def client_register(email, password, first_name="", last_name=""):
    """Self-service sign-up: creates the client and puts them on the Free plan.

    Rules: the email must not be taken (case-insensitive); the account and the subscription
    are created in one transaction, so a failure never leaves a client without a plan.
    """
    if repository.email_exists(email):
        raise ValidationError({"email": "Există deja un cont cu acest email."})

    plan = billing_services.default_plan()
    if plan is None:
        raise ImproperlyConfigured("The default plan is missing or inactive; clients cannot register.")

    user = repository.add_client(email, password, first_name=first_name, last_name=last_name)
    billing_services.subscription_create(user, plan, BillingCycle.MONTHLY)
    return user
