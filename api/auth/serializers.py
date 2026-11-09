"""Serializerele pentru autentificare (login JWT și clientul curent)."""
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from billing import services as billing_services


class ClientTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login cu email + parolă → {access, refresh}; conturile de staff nu primesc token."""

    def validate(self, attrs):
        data = super().validate(attrs)  # verifică emailul, parola și contul activ; setează self.user
        if self.user.is_staff:
            raise exceptions.AuthenticationFailed(
                "Conturile de staff nu au acces la API. Folosește back office-ul.", code="staff_not_allowed"
            )
        return data


class MeSerializer(serializers.Serializer):
    """Clientul autentificat și planul abonamentului activ (null dacă nu are abonament activ)."""

    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    timezone = serializers.CharField()
    date_joined = serializers.DateTimeField()
    plan = serializers.SerializerMethodField()

    def get_plan(self, user):
        subscription = billing_services.active_subscription_for_user(user)
        if subscription is None:
            return None
        plan = subscription.plan
        return {
            "code": plan.code,
            "name": plan.name,
            "billing_cycle": subscription.billing_cycle,
            "current_period_end": subscription.current_period_end,
            "max_monitors": plan.max_monitors,
            "min_check_interval_sec": plan.min_check_interval_sec,
        }
