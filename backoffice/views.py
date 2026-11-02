"""Controller-ele back office-ului (paginile de administrare, doar pentru staff).

Datele se iau doar prin serviciile app-urilor de domeniu (accounts, billing, monitoring).
"""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from accounts import services as account_services
from audit import services as audit_services
from billing import services as billing_services
from billing.models import Invoice, Subscription
from monitoring import services as monitoring_services
from monitoring.models import Incident, Monitor
from statuspages import services as status_page_services

from .forms import FeatureForm, MonitorForm, PlanForm, SubscriptionForm


def _post_data(request):
    """Datele formularului doar la POST (un POST gol trebuie tot validat, nu tratat ca GET)."""
    return request.POST if request.method == "POST" else None


def _status_filters(choices, counts):
    """Pastilele de filtrare de deasupra listelor: (valoare, etichetă, număr)."""
    return [("", "Toate", sum(counts.values()))] + [(value, label, counts.get(value, 0)) for value, label in choices]


def _or_404(obj, message):
    if obj is None:
        raise Http404(message)
    return obj


# ---------------------------------------------------------------- Dashboard

@staff_member_required
@require_GET
def dashboard(request):
    """Pagina principală: câteva cifre despre platformă."""
    stats = {
        "clients": account_services.client_count(),
        "active_subscriptions": billing_services.active_subscription_count(),
        "mrr": billing_services.monthly_recurring_revenue(),
        "monitors": monitoring_services.monitor_count(),
        "monitors_down": monitoring_services.monitor_down_count(),
        "ongoing_incidents": monitoring_services.ongoing_incident_count(),
    }
    return render(request, "backoffice/dashboard.html", {"stats": stats})


# ---------------------------------------------------------------- Planuri

@staff_member_required
@require_GET
def plan_list(request):
    """Index: toate planurile."""
    return render(request, "backoffice/plan_list.html", {"plans": billing_services.plan_list()})


@staff_member_required
@require_GET
def plan_detail(request, pk):
    """Details: limitele și feature-urile unui plan."""
    plan = _or_404(billing_services.plan_get(pk), "Planul nu există.")
    return render(request, "backoffice/plan_detail.html", {"plan": plan})


@staff_member_required
@require_http_methods(["GET", "POST"])
def plan_create(request):
    """Create: GET afișează formularul gol, POST validează și salvează."""
    form = PlanForm(_post_data(request))
    if request.method == "POST" and form.is_valid():
        plan = billing_services.plan_create(form.cleaned_data)
        messages.success(request, f"Planul „{plan.name}” a fost adăugat.")
        return redirect("backoffice:plan_detail", pk=plan.pk)
    return render(request, "backoffice/plan_form.html", {"form": form})


@staff_member_required
@require_http_methods(["GET", "POST"])
def plan_update(request, pk):
    """Edit: GET afișează formularul precompletat, POST validează și salvează."""
    plan = _or_404(billing_services.plan_get(pk), "Planul nu există.")
    title = plan.name
    was_active = plan.is_active  # form.is_valid() modifică instanța înainte de regula din service
    form = PlanForm(_post_data(request), instance=plan)
    if request.method == "POST" and form.is_valid():
        plan.is_active = was_active
        try:
            billing_services.plan_update(plan, form.cleaned_data)
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, f"Planul „{plan.name}” a fost actualizat.")
            return redirect("backoffice:plan_detail", pk=plan.pk)
    return render(request, "backoffice/plan_form.html", {"form": form, "plan": plan, "title": title})


# ---------------------------------------------------------------- Feature-uri

@staff_member_required
@require_GET
def feature_list(request):
    """Index: toate feature-urile, cu planurile care le includ."""
    return render(request, "backoffice/feature_list.html", {"features": billing_services.feature_list()})


@staff_member_required
@require_http_methods(["GET", "POST"])
def feature_create(request):
    form = FeatureForm(_post_data(request))
    if request.method == "POST" and form.is_valid():
        feature = billing_services.feature_create(form.cleaned_data)
        messages.success(request, f"Feature-ul „{feature.name}” a fost adăugat.")
        return redirect("backoffice:feature_list")
    return render(request, "backoffice/feature_form.html", {"form": form})


@staff_member_required
@require_http_methods(["GET", "POST"])
def feature_update(request, pk):
    feature = _or_404(billing_services.feature_get(pk), "Feature-ul nu există.")
    title = feature.name
    form = FeatureForm(_post_data(request), instance=feature)
    if request.method == "POST" and form.is_valid():
        billing_services.feature_update(feature, form.cleaned_data)
        messages.success(request, f"Feature-ul „{feature.name}” a fost actualizat.")
        return redirect("backoffice:feature_list")
    return render(request, "backoffice/feature_form.html", {"form": form, "feature": feature, "title": title})


# ---------------------------------------------------------------- Abonamente

@staff_member_required
@require_GET
def subscription_list(request):
    """Index: abonamentele, cu date din 3 tabele (client, plan, abonament) și filtru pe status."""
    status = request.GET.get("status") or ""
    if status not in Subscription.Status.values:
        status = ""
    context = {
        "subscriptions": billing_services.subscription_list(status or None),
        "filters": _status_filters(Subscription.Status.choices, billing_services.subscription_status_counts()),
        "current_status": status,
    }
    return render(request, "backoffice/subscription_list.html", context)


@staff_member_required
@require_http_methods(["GET", "POST"])
def subscription_create(request):
    """Create: GET afișează formularul gol, POST atribuie planul clientului."""
    form = SubscriptionForm(_post_data(request))
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            subscription = billing_services.subscription_create(
                data["user"], data["plan"], data["billing_cycle"], data["start_date"]
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(
                request, f"Clientul {subscription.user.email} a fost abonat la planul {subscription.plan.name}."
            )
            return redirect("backoffice:subscription_list")
    return render(request, "backoffice/subscription_form.html", {"form": form})


@staff_member_required
@require_POST
def subscription_cancel(request, pk):
    """Anulează un abonament activ (doar POST, din butonul din listă)."""
    subscription = _or_404(billing_services.subscription_get(pk), "Abonamentul nu există.")
    try:
        billing_services.subscription_cancel(subscription)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        messages.success(request, f"Abonamentul lui {subscription.user.email} la {subscription.plan.name} a fost anulat.")
    return redirect("backoffice:subscription_list")


# ---------------------------------------------------------------- Clienți

@staff_member_required
@require_GET
def client_list(request):
    """Index: clienții, cu planul curent și numărul de monitoare; căutare și filtru activ / inactiv."""
    search = request.GET.get("q", "")
    status = request.GET.get("status", "")
    context = {
        "clients": account_services.client_list(search, status),
        "search": search,
        "current_status": status if status in account_services.STATUS_FILTERS else "",
    }
    return render(request, "backoffice/client_list.html", context)


@staff_member_required
@require_GET
def client_detail(request, pk):
    """Details: datele clientului, cu abonamentele, monitoarele și facturile lui."""
    client = _or_404(account_services.client_get(pk), "Clientul nu există.")
    context = {
        "client": client,
        "subscriptions": billing_services.subscription_list_for_user(client),
        "monitors": monitoring_services.monitor_list_for_user(client),
        "invoices": billing_services.invoice_list_for_user(client),
    }
    return render(request, "backoffice/client_detail.html", context)


@staff_member_required
@require_POST
def client_toggle_active(request, pk):
    """Activează / dezactivează contul clientului (doar POST, din pagina clientului)."""
    client = _or_404(account_services.client_get(pk), "Clientul nu există.")
    try:
        account_services.client_set_active(client, not client.is_active)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        state = "activat" if client.is_active else "dezactivat"
        messages.success(request, f"Contul {client.email} a fost {state}.")
    return redirect("backoffice:client_detail", pk=client.pk)


# ---------------------------------------------------------------- Facturi

@staff_member_required
@require_GET
def invoice_list(request):
    """Index: facturile, cu filtru pe status și căutare după număr / email."""
    status = request.GET.get("status") or ""
    if status not in Invoice.Status.values:
        status = ""
    search = request.GET.get("q", "")
    context = {
        "invoices": billing_services.invoice_list(status or None, search),
        "filters": _status_filters(Invoice.Status.choices, billing_services.invoice_status_counts()),
        "current_status": status,
        "search": search,
    }
    return render(request, "backoffice/invoice_list.html", context)


@staff_member_required
@require_GET
def invoice_detail(request, pk):
    invoice = _or_404(billing_services.invoice_get(pk), "Factura nu există.")
    return render(request, "backoffice/invoice_detail.html", {"invoice": invoice})


def _change_invoice_status(request, pk, action, success):
    invoice = _or_404(billing_services.invoice_get(pk), "Factura nu există.")
    try:
        action(invoice)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        messages.success(request, f"Factura {invoice.number} a fost marcată ca {success}.")
    return redirect("backoffice:invoice_detail", pk=invoice.pk)


@staff_member_required
@require_POST
def invoice_mark_paid(request, pk):
    return _change_invoice_status(request, pk, billing_services.invoice_mark_paid, "plătită")


@staff_member_required
@require_POST
def invoice_mark_failed(request, pk):
    return _change_invoice_status(request, pk, billing_services.invoice_mark_failed, "eșuată")


# ---------------------------------------------------------------- Monitoare (mutate din Lab 5)

@staff_member_required
@require_GET
def monitor_list(request):
    """Index: toate monitoarele, cu filtru pe status și căutare."""
    status = request.GET.get("status") or ""
    if status not in Monitor.Status.values:
        status = ""
    search = request.GET.get("q", "")
    context = {
        "monitors": monitoring_services.monitor_list(status or None, search),
        "filters": _status_filters(Monitor.Status.choices, monitoring_services.monitor_status_counts()),
        "current_status": status,
        "search": search,
    }
    return render(request, "backoffice/monitor_list.html", context)


@staff_member_required
@require_GET
def monitor_detail(request, pk):
    """Details: monitorul și incidentele lui."""
    monitor = _or_404(monitoring_services.monitor_get(pk), "Monitorul nu există.")
    context = {"monitor": monitor, "incidents": monitoring_services.incident_list_for_monitor(monitor)}
    return render(request, "backoffice/monitor_detail.html", context)


@staff_member_required
@require_http_methods(["GET", "POST"])
def monitor_create(request):
    """Create: GET afișează formularul gol, POST validează și salvează."""
    form = MonitorForm(_post_data(request))
    if request.method == "POST" and form.is_valid():
        monitor = monitoring_services.monitor_create(form.cleaned_data)
        messages.success(request, f"Monitorul „{monitor.name}” a fost adăugat.")
        return redirect("backoffice:monitor_detail", pk=monitor.pk)
    return render(request, "backoffice/monitor_form.html", {"form": form})


@staff_member_required
@require_http_methods(["GET", "POST"])
def monitor_update(request, pk):
    """Edit: GET afișează formularul precompletat, POST validează și salvează."""
    monitor = _or_404(monitoring_services.monitor_get(pk), "Monitorul nu există.")
    title = monitor.name  # form.is_valid() modifică instanța, așa că numele original se păstrează separat
    form = MonitorForm(_post_data(request), instance=monitor)
    if request.method == "POST" and form.is_valid():
        monitoring_services.monitor_update(monitor, form.cleaned_data)
        messages.success(request, f"Monitorul „{monitor.name}” a fost actualizat.")
        return redirect("backoffice:monitor_detail", pk=monitor.pk)
    return render(request, "backoffice/monitor_form.html", {"form": form, "monitor": monitor, "title": title})


@staff_member_required
@require_POST
def monitor_toggle_active(request, pk):
    """Pune pe pauză / reactivează monitorul (doar POST)."""
    monitor = _or_404(monitoring_services.monitor_get(pk), "Monitorul nu există.")
    try:
        monitoring_services.monitor_set_active(monitor, not monitor.is_active)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        state = "reactivat" if monitor.is_active else "pus pe pauză"
        messages.success(request, f"Monitorul „{monitor.name}” a fost {state}.")
    return redirect("backoffice:monitor_detail", pk=monitor.pk)


# ---------------------------------------------------------------- Incidente (doar citire)

@staff_member_required
@require_GET
def incident_list(request):
    """Index: incidentele, cele în desfășurare primele."""
    status = request.GET.get("status") or ""
    if status not in Incident.Status.values:
        status = ""
    context = {
        "incidents": monitoring_services.incident_list(status or None),
        "filters": _status_filters(Incident.Status.choices, monitoring_services.incident_status_counts()),
        "current_status": status,
    }
    return render(request, "backoffice/incident_list.html", context)


# ---------------------------------------------------------------- Pagini de status

@staff_member_required
@require_GET
def status_page_list(request):
    return render(request, "backoffice/status_page_list.html", {"pages": status_page_services.status_page_list()})


@staff_member_required
@require_GET
def status_page_detail(request, pk):
    page = _or_404(status_page_services.status_page_get(pk), "Pagina de status nu există.")
    return render(request, "backoffice/status_page_detail.html", {"page": page})


@staff_member_required
@require_POST
def status_page_toggle_public(request, pk):
    """Publică / retrage pagina de status (doar POST)."""
    page = _or_404(status_page_services.status_page_get(pk), "Pagina de status nu există.")
    try:
        status_page_services.status_page_set_public(page, not page.is_public)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        state = "publicată" if page.is_public else "retrasă"
        messages.success(request, f"Pagina „{page.title}” a fost {state}.")
    return redirect("backoffice:status_page_detail", pk=page.pk)


# ---------------------------------------------------------------- Audit (doar citire)

@staff_member_required
@require_GET
def audit_list(request):
    """Index: jurnalul de audit, cu filtru pe acțiune și căutare după email, 50 de intrări pe pagină."""
    action = request.GET.get("action", "")
    search = request.GET.get("q", "")
    actions = audit_services.action_list()
    if action not in actions:
        action = ""
    page = Paginator(audit_services.entry_list(action, search), 50).get_page(request.GET.get("page"))
    context = {"page": page, "actions": actions, "current_action": action, "search": search}
    return render(request, "backoffice/audit_list.html", context)

