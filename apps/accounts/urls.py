"""
URL routes for the accounts (auth) app.

These are mounted under /api/auth/ by config/urls.py, so the full paths are:
  POST /api/auth/login/          -> obtain access + refresh JWT
  POST /api/auth/login/refresh/  -> obtain a fresh access token
  POST /api/auth/logout/         -> blacklist a refresh token
  POST /api/auth/register/       -> create a new user account
  GET  /api/auth/me/             -> return the logged-in user's profile
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import LogoutView, MeView, RegisterView

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
]
