"""Controllerele pentru autentificare. Tokenurile sunt JWT (vezi SIMPLE_JWT în settings)."""
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import ClientTokenObtainPairSerializer, MeSerializer


class LoginAPIView(TokenObtainPairView):
    """POST /api/v1/auth/token/  {email, password} → {access, refresh}"""

    serializer_class = ClientTokenObtainPairSerializer


class MeAPIView(APIView):
    """GET /api/v1/auth/me/  clientul din token și planul lui."""

    def get(self, request):
        return Response(MeSerializer(request.user).data)
