"""Serializerele pentru autentificare (login JWT și clientul curent)."""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from billing import services as billing_services


class ClientTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login cu email + parolă → {access, refresh}; conturile de staff nu primesc token."""

    def validate(self, attrs):
        # Emails are stored lowercase (see RegisterSerializer), so Ana@x.ro must log in as ana@x.ro.
        attrs[self.username_field] = attrs[self.username_field].strip().lower()
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


class RegisterSerializer(serializers.Serializer):
    """Sign-up body. Checks only the shape of the data; account rules live in accounts/services.py."""

    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, trim_whitespace=False, style={"input_type": "password"})
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")

    def validate_email(self, email):
        # Stored lowercase so the same address cannot be registered twice with different casing.
        return email.strip().lower()

    def validate(self, attrs):
        # Run Django's AUTH_PASSWORD_VALIDATORS; an unsaved user lets the similarity check compare
        # the password with the email and the name.
        candidate = get_user_model()(email=attrs["email"], first_name=attrs["first_name"], last_name=attrs["last_name"])
        try:
            validate_password(attrs["password"], user=candidate)
        except ValidationError as error:
            raise serializers.ValidationError({"password": list(error.messages)})
        return attrs
