"""API tests for the accounts endpoints (register, login, me, logout)."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User


@pytest.mark.django_db
class TestRegisterEndpoint:
    def test_register_creates_user_and_returns_safe_payload(self, client):
        url = reverse("auth:register")
        payload = {
            "email": "newbie@example.com",
            "password": "SuperSecret123!",
            "first_name": "New",
            "last_name": "Bie",
        }
        response = client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newbie@example.com").count() == 1
        # password must NOT be echoed back.
        assert "password" not in response.data

    def test_register_rejects_short_password(self, client):
        url = reverse("auth:register")
        response = client.post(
            url, {"email": "x@e.com", "password": "short"}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_rejects_duplicate_email(self, client, user_factory):
        existing = user_factory(email="dup@example.com")
        url = reverse("auth:register")
        response = client.post(
            url,
            {"email": existing.email, "password": "Whatever123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginEndpoint:
    def test_login_returns_access_and_refresh(self, client, user_factory):
        user_factory(email="login@example.com", password="Password123!")
        url = reverse("auth:login")
        response = client.post(
            url,
            {"email": "login@example.com", "password": "Password123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_with_wrong_password_fails(self, client, user_factory):
        user_factory(email="login@example.com", password="Password123!")
        url = reverse("auth:login")
        response = client.post(
            url,
            {"email": "login@example.com", "password": "WrongPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMeEndpoint:
    def test_me_requires_authentication(self, client):
        url = reverse("auth:me")
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_returns_logged_in_user(self, api_client, user_factory):
        user = user_factory(email="me@example.com", first_name="Me")
        api_client.force_authenticate(user=user)
        url = reverse("auth:me")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "me@example.com"
        assert response.data["first_name"] == "Me"


@pytest.mark.django_db
class TestLogoutEndpoint:
    def test_logout_blacklists_refresh(self, api_client, user_factory):
        user = user_factory(email="out@example.com")
        refresh = str(RefreshToken.for_user(user))
        api_client.force_authenticate(user=user)
        url = reverse("auth:logout")
        response = api_client.post(url, {"refresh": refresh}, format="json")
        assert response.status_code == status.HTTP_205_RESET_CONTENT

    def test_logout_without_refresh_returns_400(self, api_client, user_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)
        url = reverse("auth:logout")
        response = api_client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
