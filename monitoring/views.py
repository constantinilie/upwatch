from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from . import services
from .forms import MonitorForm


def _get_monitor_or_404(pk):
    monitor = services.monitor_get(pk)
    if monitor is None:
        raise Http404("Monitorul nu există.")
    return monitor


@require_GET
def monitor_list(request):
    """Index: lista tuturor monitoarelor."""
    return render(request, "monitoring/monitor_list.html", {"monitors": services.monitor_list()})


@require_GET
def monitor_detail(request, pk):
    """Details: detaliile unui monitor."""
    return render(request, "monitoring/monitor_detail.html", {"monitor": _get_monitor_or_404(pk)})


@require_http_methods(["GET", "POST"])
def monitor_create(request):
    """Create: GET afișează formularul gol, POST validează și salvează."""
    if request.method == "POST":
        form = MonitorForm(request.POST)
        if form.is_valid():
            monitor = services.monitor_create(form.cleaned_data)
            messages.success(request, f"Monitorul „{monitor.name}” a fost adăugat.")
            return redirect("monitoring:monitor_detail", pk=monitor.pk)
    else:
        form = MonitorForm()
    return render(request, "monitoring/monitor_form.html", {"form": form})


@require_http_methods(["GET", "POST"])
def monitor_update(request, pk):
    """Edit: GET afișează formularul precompletat, POST validează și salvează."""
    monitor = _get_monitor_or_404(pk)
    title = monitor.name  # form.is_valid() modifică instanța, așa că numele original se păstrează separat
    if request.method == "POST":
        form = MonitorForm(request.POST, instance=monitor)
        if form.is_valid():
            services.monitor_update(monitor, form.cleaned_data)
            messages.success(request, f"Monitorul „{monitor.name}” a fost actualizat.")
            return redirect("monitoring:monitor_detail", pk=monitor.pk)
    else:
        form = MonitorForm(instance=monitor)
    return render(request, "monitoring/monitor_form.html", {"form": form, "monitor": monitor, "title": title})
