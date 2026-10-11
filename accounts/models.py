from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email-ul este obligatoriu.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("Superuser-ul trebuie să aibă is_staff=True și is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Clientul aplicației. Autentificare cu email în loc de username."""

    username = None
    email = models.EmailField("email", unique=True)
    timezone = models.CharField(max_length=50, default="Europe/Bucharest")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "utilizator"
        verbose_name_plural = "utilizatori"

    def __str__(self):
        return self.email

    @property
    def current_subscription(self):
        return self.subscriptions.select_related("plan").filter(status="active").first()

    @property
    def current_plan(self):
        subscription = self.current_subscription
        return subscription.plan if subscription else None

    def has_feature(self, code):
        plan = self.current_plan
        return plan is not None and plan.features.filter(code=code).exists()
