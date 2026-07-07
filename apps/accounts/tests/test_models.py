"""Tests for the custom User model and its manager."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_hashes_password(self):
        user = User.objects.create_user(
            email="alice@example.com",
            password="Password123!",
            first_name="Alice",
            last_name="Wonderland",
        )
        # password attribute is the HASH, not plaintext.
        assert user.password != "Password123!"
        assert user.check_password("Password123!") is True

    def test_create_user_normalizes_email(self):
        # domain part is lowercased; local part is preserved.
        user = User.objects.create_user(email="Bob@EXAMPLE.com", password="x" * 8)
        assert user.email == "Bob@example.com"

    def test_create_user_requires_email(self):
        with pytest.raises(ValueError, match="email"):
            User.objects.create_user(email="", password="x" * 8)

    def test_create_superuser_sets_staff_and_superuser_flags(self):
        su = User.objects.create_superuser(email="root@example.com", password="x" * 8)
        assert su.is_staff is True
        assert su.is_superuser is True

    def test_email_must_be_unique(self):
        User.objects.create_user(email="dup@example.com", password="x" * 8)
        with pytest.raises(Exception):
            User.objects.create_user(email="dup@example.com", password="y" * 8)

    def test_str_representation(self):
        user = User(email="str@example.com", password="x" * 8)
        assert str(user) == "str@example.com"

    def test_full_name_property(self):
        user = User(first_name="Jane", last_name="Doe", email="j@e.com")
        assert user.full_name == "Jane Doe"
