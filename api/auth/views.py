"""Controllerele pentru autentificare. Tokenurile sunt JWT (vezi SIMPLE_JWT în settings)."""
from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts import services as account_services

from .serializers import ClientTokenObtainPairSerializer, MeSerializer, RegisterSerializer


class LoginAPIView(TokenObtainPairView):
    """POST /api/v1/auth/token/  {email, password} → {access, refresh}"""

    serializer_class = ClientTokenObtainPairSerializer


class MeAPIView(APIView):
    """GET /api/v1/auth/me/  clientul din token și planul lui."""

    def get(self, request):
        return Response(MeSerializer(request.user).data)


class RegisterAPIView(APIView):
    """POST /api/v1/auth/register/  {email, password, first_name?, last_name?} → 201 {access, refresh}

    Public endpoint: no token is required (it overrides the default IsClient permission).
    The new client is logged in right away, so the response has the same shape as the login.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_scope = "register"  # rate limit per IP, see DEFAULT_THROTTLE_RATES in settings

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = account_services.client_register(**serializer.validated_data)
        except ValidationError as error:
            # A broken business rule (e.g. email already taken) becomes a 400 with field errors.
            raise serializers.ValidationError(serializers.as_serializer_error(error))

        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)}, status=status.HTTP_201_CREATED)
