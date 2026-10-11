"""
Populează baza de date cu date de test.

    python manage.py seed           # prima rulare
    python manage.py seed --reset   # șterge datele de test și le recreează

Toți utilizatorii de test au parola SEED_PASSWORD de mai jos.
Superuserii (is_superuser=True) nu sunt atinși de --reset.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from alerts.models import AlertChannel, AlertEvent, MonitorAlertChannel
from audit.models import AuditLog
from billing.models import BillingCycle, Feature, Invoice, Plan, PlanFeature, Subscription
from monitoring.models import CheckResult, Incident, Monitor
from statuspages.models import StatusPage, StatusPageMonitor

SEED_PASSWORD = "UpWatch123!"
EMAIL_DOMAIN = "upwatch.test"

FEATURES = [
    ("keyword_monitoring", "Monitorizare keyword", "Verifică prezența unui text în răspuns."),
    ("ssl_monitoring", "Monitorizare SSL", "Verifică validitatea și expirarea certificatului."),
    ("webhook_alerts", "Alerte webhook", "Trimite alertele prin HTTP POST (Slack, Discord etc.)."),
    ("custom_domain", "Domeniu custom", "Pagina de status pe domeniul clientului."),
    ("remove_branding", "Fără branding", "Ascunde mesajul „Powered by UpWatch”."),
]

PLANS = [
    {
        "code": "free", "name": "Free", "description": "Pentru proiecte personale.",
        "price_monthly": Decimal("0"), "price_yearly": Decimal("0"),
        "max_monitors": 5, "min_check_interval_sec": 300, "max_status_pages": 1,
        "max_alert_channels": 1, "log_retention_days": 7, "sort_order": 1,
        "features": [],
    },
    {
        "code": "pro", "name": "Pro", "description": "Pentru freelanceri și echipe mici.",
        "price_monthly": Decimal("9.00"), "price_yearly": Decimal("90.00"),
        "max_monitors": 50, "min_check_interval_sec": 60, "max_status_pages": 5,
        "max_alert_channels": 10, "log_retention_days": 90, "sort_order": 2,
        "features": ["keyword_monitoring", "ssl_monitoring", "webhook_alerts"],
    },
    {
        "code": "business", "name": "Business", "description": "Pentru companii.",
        "price_monthly": Decimal("29.00"), "price_yearly": Decimal("290.00"),
        "max_monitors": 200, "min_check_interval_sec": 30, "max_status_pages": 20,
        "max_alert_channels": 50, "log_retention_days": 365, "sort_order": 3,
        "features": ["keyword_monitoring", "ssl_monitoring", "webhook_alerts", "custom_domain", "remove_branding"],
    },
]

# Monitoare per utilizator. "incidents": (acum câte ore a început, durata în minute; None = încă în desfășurare)
MONITORS = {
    "ana": [
        {"name": "Magazin online", "url": "https://www.wikipedia.org", "interval_sec": 60, "base_ms": 180,
         "incidents": [(30, 15, "HTTP 503 Service Unavailable")]},
        {"name": "API plăți", "url": "https://api.github.com", "interval_sec": 60, "base_ms": 240,
         "monitor_type": "keyword", "keyword": "current_user_url", "incidents": [(10, 5, "Keyword negăsit")]},
        {"name": "Certificat SSL magazin", "url": "https://github.com", "interval_sec": 3600, "base_ms": 300,
         "monitor_type": "ssl", "incidents": []},
    ],
    "mihai": [
        {"name": "Blog personal", "url": "https://example.com", "interval_sec": 300, "base_ms": 120,
         "incidents": [(40, 25, "Timeout după 10s")]},
        {"name": "Portofoliu", "url": "https://www.python.org", "interval_sec": 300, "base_ms": 210,
         "paused": True, "incidents": []},
    ],
    "elena": [
        {"name": "Site corporate", "url": "https://www.djangoproject.com", "interval_sec": 30, "base_ms": 160,
         "incidents": []},
        {"name": "API intern", "url": "https://httpbin.org/status/503", "interval_sec": 30, "base_ms": 350,
         "incidents": [(20, 10, "HTTP 503 Service Unavailable"), (2, None, "HTTP 503 Service Unavailable")]},
        {"name": "Portal clienți", "url": "https://www.postgresql.org", "interval_sec": 60, "base_ms": 260,
         "incidents": [(44, 40, "Connection refused")]},
    ],
}

HISTORY_HOURS = 48
CHECK_STEP_MIN = 10  # pentru date de test generăm o verificare la 10 minute, indiferent de interval


class Command(BaseCommand):
    help = "Populeaza baza de date cu date de test (planuri, utilizatori, monitoare, incidente etc.)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Sterge datele de test existente inainte de seed.")

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        self.now = timezone.now()
        self.invoice_seq = 0

        test_users = User.objects.filter(email__endswith=f"@{EMAIL_DOMAIN}")
        if options["reset"]:
            self.reset()
        elif test_users.exists():
            raise CommandError("Datele de test exista deja. Ruleaza: python manage.py seed --reset")

        plans = self.seed_plans()
        users = self.seed_users()
        self.seed_subscriptions(users, plans)
        channels = self.seed_alert_channels(users)
        monitors = self.seed_monitors(users, channels)
        self.seed_status_pages(users, monitors)
        self.seed_audit_logs(users, monitors)

        self.stdout.write(self.style.SUCCESS("Seed finalizat:"))
        for model in [Plan, Feature, PlanFeature, User, Subscription, Invoice, Monitor, CheckResult,
                      Incident, AlertChannel, MonitorAlertChannel, AlertEvent, StatusPage,
                      StatusPageMonitor, AuditLog]:
            self.stdout.write(f"  {model._meta.db_table:<32} {model.objects.count():>6}")
        self.stdout.write(f"Utilizatori de test: *@{EMAIL_DOMAIN}, parola: {SEED_PASSWORD}")

    # ---------- reset ----------

    def reset(self):
        test_users = User.objects.filter(email__endswith=f"@{EMAIL_DOMAIN}", is_superuser=False)
        AuditLog.objects.filter(user__in=test_users).delete()
        Invoice.objects.filter(user__in=test_users).delete()  # PROTECT pe subscription
        Subscription.objects.filter(user__in=test_users).delete()  # PROTECT pe plan
        test_users.delete()  # cascade: monitoare, incidente, canale, pagini de status
        self.stdout.write("Datele de test vechi au fost sterse.")

    # ---------- billing ----------

    def seed_plans(self):
        features = {}
        for code, name, description in FEATURES:
            features[code], _ = Feature.objects.update_or_create(
                code=code, defaults={"name": name, "description": description}
            )

        plans = {}
        for data in PLANS:
            data = dict(data)
            feature_codes = data.pop("features")
            plan, _ = Plan.objects.update_or_create(code=data.pop("code"), defaults=data)
            plan.features.set([features[c] for c in feature_codes])
            plans[plan.code] = plan
        return plans

    def seed_users(self):
        people = [
            ("ana", "Ana", "Popescu"),
            ("mihai", "Mihai", "Ionescu"),
            ("elena", "Elena", "Dumitrescu"),
            ("andrei", "Andrei", "Stan"),
        ]
        users = {}
        for key, first, last in people:
            user = User.objects.create_user(
                email=f"{key}@{EMAIL_DOMAIN}", password=SEED_PASSWORD, first_name=first, last_name=last
            )
            User.objects.filter(pk=user.pk).update(date_joined=self.now - timedelta(days=120))
            users[key] = user
        return users

    def new_invoice(self, subscription, status, period_start, period_end, issued_at):
        self.invoice_seq += 1
        return Invoice.objects.create(
            user=subscription.user,
            subscription=subscription,
            number=f"INV-{issued_at:%Y}-{self.invoice_seq:06d}",
            amount=subscription.plan.price_for(subscription.billing_cycle),
            status=status,
            billing_cycle=subscription.billing_cycle,
            period_start=period_start,
            period_end=period_end,
            card_last4="4242",
            issued_at=issued_at,
            paid_at=issued_at if status == Invoice.Status.PAID else None,
        )

    def subscription(self, user, plan, cycle, status, start, end, created, **extra):
        sub = Subscription.objects.create(
            user=user, plan=plan, billing_cycle=cycle, status=status,
            current_period_start=start, current_period_end=end, **extra,
        )
        Subscription.objects.filter(pk=sub.pk).update(created_at=created)
        return sub

    def seed_subscriptions(self, users, plans):
        now, day = self.now, timedelta(days=1)
        A, C, E = Subscription.Status.ACTIVE, Subscription.Status.CANCELED, Subscription.Status.EXPIRED
        M, Y = BillingCycle.MONTHLY, BillingCycle.YEARLY
        PAID, FAILED = Invoice.Status.PAID, Invoice.Status.FAILED

        # Ana: Free, apoi upgrade la Pro anual acum 40 de zile
        upgrade = now - 40 * day
        self.subscription(users["ana"], plans["free"], M, C, now - 120 * day, None, now - 120 * day, canceled_at=upgrade)
        sub = self.subscription(users["ana"], plans["pro"], Y, A, upgrade, upgrade + 365 * day, upgrade)
        self.new_invoice(sub, PAID, upgrade, upgrade + 365 * day, upgrade)

        # Mihai: doar Free
        self.subscription(users["mihai"], plans["free"], M, A, now - 120 * day, None, now - 120 * day)

        # Elena: Business lunar de 3 luni, reînnoit de 2 ori
        start = now - 75 * day
        periods = [(start + i * 30 * day, start + (i + 1) * 30 * day) for i in range(3)]
        sub = self.subscription(users["elena"], plans["business"], M, A, *periods[-1], start)
        for period_start, period_end in periods:
            self.new_invoice(sub, PAID, period_start, period_end, period_start)

        # Andrei: Pro lunar, reînnoirea a eșuat -> expirat, înapoi pe Free
        start = now - 70 * day
        sub = self.subscription(users["andrei"], plans["pro"], M, E, start + 30 * day, start + 60 * day, start)
        self.new_invoice(sub, PAID, start, start + 30 * day, start)
        self.new_invoice(sub, FAILED, start + 30 * day, start + 60 * day, start + 30 * day)
        self.subscription(users["andrei"], plans["free"], M, A, start + 60 * day, None, start + 60 * day)

    # ---------- alerte ----------

    def seed_alert_channels(self, users):
        channels = {key: [] for key in users}
        for key, user in users.items():
            channels[key].append(AlertChannel.objects.create(
                user=user, name="Email personal", channel_type=AlertChannel.Type.EMAIL, target=user.email,
            ))
        for key, name in [("ana", "Slack echipă"), ("elena", "Discord ops")]:
            channels[key].append(AlertChannel.objects.create(
                user=users[key], name=name, channel_type=AlertChannel.Type.WEBHOOK,
                target=f"https://hooks.{EMAIL_DOMAIN}/{key}/alerts",
            ))
        return channels

    # ---------- monitorizare ----------

    def seed_monitors(self, users, channels):
        monitors = {}
        for key, specs in MONITORS.items():
            monitors[key] = []
            for spec in specs:
                monitor = self.create_monitor(users[key], spec)
                monitor.alert_channels.set(channels[key])
                if not spec.get("paused"):
                    self.create_history(monitor, spec, channels[key])
                monitors[key].append(monitor)
        return monitors

    def create_monitor(self, user, spec):
        paused = spec.get("paused", False)
        monitor = Monitor.objects.create(
            user=user,
            name=spec["name"],
            url=spec["url"],
            monitor_type=spec.get("monitor_type", Monitor.Type.HTTP),
            keyword=spec.get("keyword", ""),
            interval_sec=spec["interval_sec"],
            timeout_sec=min(10, spec["interval_sec"] - 1),
            is_active=not paused,
            status=Monitor.Status.PAUSED if paused else Monitor.Status.PENDING,
        )
        Monitor.objects.filter(pk=monitor.pk).update(created_at=self.now - timedelta(days=60))
        return monitor

    def create_history(self, monitor, spec, channels):
        # ferestrele de down, ca intervale de timp
        windows = []
        for hours_ago, minutes, cause in spec["incidents"]:
            start = self.now - timedelta(hours=hours_ago)
            end = start + timedelta(minutes=minutes) if minutes is not None else None
            windows.append((start, end, cause))

        def down_cause(t):
            for start, end, cause in windows:
                if start <= t and (end is None or t < end):
                    return cause
            return None

        # verificările din ultimele HISTORY_HOURS ore
        results = []
        t = self.now - timedelta(hours=HISTORY_HOURS)
        while t <= self.now:
            cause = down_cause(t)
            if cause is None:
                results.append(CheckResult(
                    monitor=monitor, checked_at=t, is_up=True, status_code=200,
                    response_time_ms=max(40, int(random.gauss(spec["base_ms"], spec["base_ms"] * 0.2))),
                ))
            else:
                timeout = "Timeout" in cause or "refused" in cause
                results.append(CheckResult(
                    monitor=monitor, checked_at=t, is_up=False,
                    status_code=None if timeout else 503,
                    response_time_ms=None if timeout else int(random.gauss(spec["base_ms"] * 3, 50)),
                    error_message=cause,
                ))
            t += timedelta(minutes=CHECK_STEP_MIN)
        CheckResult.objects.bulk_create(results)

        # incidentele și alertele trimise pentru ele
        last_change = self.now - timedelta(hours=HISTORY_HOURS)
        for start, end, cause in windows:
            incident = Incident(monitor=monitor, cause=cause, started_at=start)
            if end is not None:
                incident.resolve(end)
            incident.save()
            for channel in channels:
                AlertEvent.objects.create(incident=incident, alert_channel=channel,
                                          event_type=AlertEvent.EventType.DOWN, sent_at=start + timedelta(seconds=30))
                if end is not None:
                    AlertEvent.objects.create(incident=incident, alert_channel=channel,
                                              event_type=AlertEvent.EventType.UP, sent_at=end + timedelta(seconds=30))
            last_change = max(last_change, end or start)

        last = results[-1]
        monitor.status = Monitor.Status.UP if last.is_up else Monitor.Status.DOWN
        monitor.last_checked_at = last.checked_at
        monitor.last_status_change_at = last_change
        monitor.save(update_fields=["status", "last_checked_at", "last_status_change_at"])

    # ---------- pagini de status ----------

    def seed_status_pages(self, users, monitors):
        page = StatusPage.objects.create(
            user=users["ana"], title="Magazin Ana – Status", slug="magazin-ana",
            description="Starea serviciilor magazinului online.",
        )
        for order, (monitor, name) in enumerate([(monitors["ana"][0], "Magazin"), (monitors["ana"][1], "Plăți")]):
            StatusPageMonitor.objects.create(status_page=page, monitor=monitor, display_name=name, sort_order=order)

        page = StatusPage.objects.create(
            user=users["elena"], title="Elena Corp Status", slug="elena-corp",
            description="Status oficial al serviciilor Elena Corp.",
            custom_domain=f"status.elena-corp.{EMAIL_DOMAIN}", show_branding=False,
        )
        for order, (monitor, name) in enumerate(zip(monitors["elena"], ["Website", "API", "Portal clienți"])):
            StatusPageMonitor.objects.create(status_page=page, monitor=monitor, display_name=name, sort_order=order)

    # ---------- audit ----------

    def seed_audit_logs(self, users, monitors):
        entries = [
            (users["ana"], "user.login", "user", users["ana"].pk, {}, 41),
            (users["ana"], "subscription.upgraded", "subscription", "", {"plan": ["free", "pro"]}, 40),
            (users["ana"], "monitor.created", "monitor", monitors["ana"][0].pk, {}, 39),
            (users["ana"], "monitor.updated", "monitor", monitors["ana"][0].pk, {"interval_sec": [300, 60]}, 38),
            (users["mihai"], "monitor.paused", "monitor", monitors["mihai"][1].pk, {"is_active": [True, False]}, 5),
            (users["elena"], "status_page.published", "status_page", "elena-corp", {}, 20),
            (users["andrei"], "subscription.expired", "subscription", "", {"plan": ["pro", "free"]}, 10),
        ]
        for user, action, entity_type, entity_id, changes, days_ago in entries:
            log = AuditLog.objects.create(
                user=user, action=action, entity_type=entity_type, entity_id=str(entity_id),
                changes=changes, ip_address="127.0.0.1", user_agent="seed",
            )
            AuditLog.objects.filter(pk=log.pk).update(created_at=self.now - timedelta(days=days_ago))
