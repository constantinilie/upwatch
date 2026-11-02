"""ViewModel-urile back office-ului (formularele pentru Create / Edit)."""
from django import forms
from django.utils import timezone

from accounts import services as account_services
from billing import services as billing_services
from billing.models import BillingCycle, Feature, Plan
from monitoring.models import Monitor


class BootstrapFormMixin:
    """Pune clasele Bootstrap pe widget-uri, ca să nu le declarăm la fiecare câmp."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxSelectMultiple):
                continue  # bifele sunt randate individual în template
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class PlanForm(BootstrapFormMixin, forms.ModelForm):
    """ViewModel pentru plan: datele planului + feature-urile incluse (tabela PlanFeature)."""

    features = forms.ModelMultipleChoiceField(
        queryset=Feature.objects.order_by("code"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Feature-uri incluse",
    )

    class Meta:
        model = Plan
        fields = [
            "code", "name", "description", "price_monthly", "price_yearly", "currency",
            "max_monitors", "min_check_interval_sec", "max_status_pages", "max_alert_channels",
            "log_retention_days", "sort_order", "is_active", "features",
        ]
        labels = {
            "code": "Cod",
            "name": "Nume",
            "description": "Descriere",
            "price_monthly": "Preț lunar",
            "price_yearly": "Preț anual",
            "currency": "Monedă",
            "max_monitors": "Monitoare maxime",
            "min_check_interval_sec": "Interval minim de verificare (secunde)",
            "max_status_pages": "Pagini de status maxime",
            "max_alert_channels": "Canale de alertă maxime",
            "log_retention_days": "Retenția istoricului (zile)",
            "sort_order": "Ordine de afișare",
            "is_active": "Activ (apare în ofertă)",
        }
        help_texts = {"code": "Identificator intern, ex. pro. Unic."}
        error_messages = {"code": {"unique": "Există deja un plan cu acest cod."}}
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}

    def _non_negative(self, name):
        value = self.cleaned_data[name]
        if value is not None and value < 0:
            raise forms.ValidationError("Prețul nu poate fi negativ.")
        return value

    def clean_price_monthly(self):
        return self._non_negative("price_monthly")

    def clean_price_yearly(self):
        return self._non_negative("price_yearly")


class FeatureForm(BootstrapFormMixin, forms.ModelForm):
    """ViewModel pentru feature."""

    class Meta:
        model = Feature
        fields = ["code", "name", "description"]
        labels = {"code": "Cod", "name": "Nume", "description": "Descriere"}
        help_texts = {"code": "Identificator folosit în cod, ex. webhook_alerts. Unic."}
        error_messages = {"code": {"unique": "Există deja un feature cu acest cod."}}
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}


class ClientChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, user):
        name = user.get_full_name()
        return f"{user.email} ({name})" if name else user.email


class PlanChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, plan):
        if plan.is_free:
            return f"{plan.name} – gratuit"
        return f"{plan.name} – {plan.price_monthly} {plan.currency}/lună · {plan.price_yearly} {plan.currency}/an"


class SubscriptionForm(BootstrapFormMixin, forms.Form):
    """ViewModel pentru abonament (echivalent CarViewModel): combină date din 3 tabele.

    - clientul        → accounts_user      (cheie străină Subscription.user)
    - planul          → billing_plan       (cheie străină Subscription.plan)
    - ciclul și data  → billing_subscription
    """

    user = ClientChoiceField(queryset=None, label="Client", empty_label="— alege clientul —")
    plan = PlanChoiceField(queryset=None, label="Plan", empty_label="— alege planul —")
    billing_cycle = forms.ChoiceField(choices=BillingCycle.choices, initial=BillingCycle.MONTHLY, label="Ciclu de facturare")
    start_date = forms.DateField(
        label="Începe la",
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        help_text="Abonamentul activ existent al clientului va fi anulat.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # listele de selecție vin tot prin servicii, nu direct din ORM
        self.fields["user"].queryset = account_services.active_client_list()
        self.fields["plan"].queryset = billing_services.active_plan_list()


MIN_INTERVAL_SEC = 30


class MonitorForm(BootstrapFormMixin, forms.ModelForm):
    """ViewModel-ul pentru Create / Edit monitor (echivalent MonitorViewModel din ASP.NET MVC).

    Câmpurile, tipurile și validările sunt preluate din modelul Monitor:
    casete text (name, url, keyword, interval_sec), liste de selecție (monitor_type, http_method, user)
    și checkbox (is_active). Constrângerile modelului (ex. keyword obligatoriu pentru tipul keyword)
    sunt verificate la form.is_valid().
    """

    class Meta:
        model = Monitor
        fields = ["name", "url", "monitor_type", "keyword", "http_method", "interval_sec", "is_active", "user"]
        labels = {
            "name": "Nume",
            "url": "URL",
            "monitor_type": "Tip monitor",
            "keyword": "Keyword",
            "http_method": "Metodă HTTP",
            "interval_sec": "Interval verificare (secunde)",
            "is_active": "Activ",
            "user": "Proprietar",
        }
        help_texts = {
            "keyword": "Obligatoriu doar pentru tipul Keyword.",
        }
        widgets = {
            "url": forms.URLInput(attrs={"placeholder": "https://exemplu.ro"}),
            "interval_sec": forms.NumberInput(attrs={"min": MIN_INTERVAL_SEC}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # proprietarul poate fi doar un client (nu un cont de staff); lista vine prin servicii
        self.fields["user"].queryset = account_services.all_client_list()
        self.fields["user"].empty_label = "— alege clientul —"

    def clean_interval_sec(self):
        # timeout_sec nu e în formular, deci constrângerea timeout < interval din model nu se verifică aici
        interval = self.cleaned_data["interval_sec"]
        if interval < MIN_INTERVAL_SEC:
            raise forms.ValidationError(f"Intervalul minim este {MIN_INTERVAL_SEC} de secunde.")
        return interval

    def clean(self):
        cleaned = super().clean()
        # mesaj clar pe câmp; altfel apare mesajul generic al constrângerii din model
        if cleaned.get("monitor_type") == Monitor.Type.KEYWORD and not cleaned.get("keyword"):
            self.add_error("keyword", "Completează keyword-ul pentru un monitor de tip Keyword.")
        return cleaned
