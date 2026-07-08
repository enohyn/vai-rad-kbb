"""
Project-wide pytest configuration and shared fixtures.

This file is auto-discovered by pytest and its fixtures are available to every
test in the repo (like a global beforeEach helper).
"""

import datetime
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.annotations.models import AnnotatedImage
from apps.tasks.models import Task


@pytest.fixture
def api_client():
    """A DRF APIClient that supports force_authenticate()."""
    return APIClient()


@pytest.fixture
def user_factory(db):
    """Return a callable that creates a user with unique defaults."""
    counter = {"n": 0}

    def make(**kwargs):
        counter["n"] += 1
        n = counter["n"]
        defaults = {
            "email": f"user{n}@example.com",
            "password": "Password123!",
            "first_name": "Test",
            "last_name": f"User{n}",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return make


@pytest.fixture
def task_factory(db):
    counter = {"n": 0}

    def make(user, **kwargs):
        counter["n"] += 1
        defaults = {
            "title": f"Task {counter['n']}",
            "due_date": datetime.date.today(),
        }
        defaults.update(kwargs)
        return Task.objects.create(user=user, **defaults)

    return make


@pytest.fixture
def image_factory(db):
    counter = {"n": 0}

    def make(user, **kwargs):
        counter["n"] += 1
        buf = io.BytesIO()
        Image.new("RGB", (2, 2), "red").save(buf, format="PNG")
        buf.seek(0)
        upload = SimpleUploadedFile(
            f"img{counter['n']}.png", buf.getvalue(), content_type="image/png"
        )
        return AnnotatedImage.objects.create(user=user, image=upload, **kwargs)

    return make


@pytest.fixture
def png_upload():
    """Returns a callable that builds an in-memory PNG SimpleUploadedFile."""

    def make(name="t.png"):
        buf = io.BytesIO()
        Image.new("RGB", (4, 4), "blue").save(buf, format="PNG")
        buf.seek(0)
        return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")

    return make
