from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    """Doar clienții (conturi active, care nu sunt staff) folosesc API-ul; staff-ul are back office-ul."""

    message = "API-ul este disponibil doar pentru clienți."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active and not user.is_staff)
