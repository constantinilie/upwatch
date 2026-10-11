from django.db import connection
from django.db.models import Count
from django.shortcuts import render

from billing.models import Plan
from monitoring.models import Monitor


def test_db(request):
    """Pagina de test: verifică conexiunea la baza de date și afișează date din tabele."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user, version()")
        database, db_user, version = cursor.fetchone()

    plans = Plan.objects.prefetch_related("features").order_by("sort_order")
    monitors = (
        Monitor.objects.select_related("user")
        .annotate(incident_count=Count("incidents"))
        .order_by("user__email", "name")
    )

    context = {
        "db": {
            "engine": connection.vendor,
            "host": connection.settings_dict["HOST"],
            "port": connection.settings_dict["PORT"],
            "database": database,
            "user": db_user,
            "version": version.split(",")[0],
        },
        "plans": plans,
        "monitors": monitors,
    }
    return render(request, "test_db.html", context)
