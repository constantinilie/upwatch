from django import forms

from .models import Monitor


MIN_INTERVAL_SEC = 30


class MonitorForm(forms.ModelForm):
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
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://exemplu.ro"}),
            "monitor_type": forms.Select(attrs={"class": "form-select"}),
            "keyword": forms.TextInput(attrs={"class": "form-control"}),
            "http_method": forms.Select(attrs={"class": "form-select"}),
            "interval_sec": forms.NumberInput(attrs={"class": "form-control", "min": MIN_INTERVAL_SEC}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "user": forms.Select(attrs={"class": "form-select"}),
        }

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
