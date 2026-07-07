"""
Views for the accounts (auth) app.

Each view (or "endpoint") is a class-based view from DRF. The framework maps
HTTP verbs to methods: GET -> retrieve, POST -> create, etc.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ - create a new user.

    AllowAny because the caller isn't authenticated yet (they're signing up).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PUT /api/auth/me/ - fetch or update the currently logged-in user.

    We ignore any id in the URL and always operate on request.user, so users
    can only ever edit their own profile.
    """

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LogoutView(generics.GenericAPIView):
    """POST /api/auth/logout/ - blacklist the refresh token.

    JWTs are stateless, so "logout" means storing the refresh token in a
    deny-list so it can no longer be used to mint new access tokens. The
    short-lived access token will simply expire on its own.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)
