"""API tests for the tasks endpoints."""

import datetime

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestTaskAPI:
    def test_list_requires_auth(self, api_client):
        r = api_client.get(reverse("tasks:task-list"))
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_and_list_task(self, api_client, user_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)
        due = datetime.date(2025, 1, 15).isoformat()
        # create
        r = api_client.post(
            reverse("tasks:task-list"),
            {"title": "Demo", "due_date": due, "tags": ["urgent"]},
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["user"] == user.id
        # list
        r = api_client.get(reverse("tasks:task-list"))
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data) == 1

    def test_filter_by_date(self, api_client, user_factory, task_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)
        d1 = datetime.date(2025, 1, 1)
        d2 = datetime.date(2025, 1, 2)
        task_factory(user, due_date=d1, title="A")
        task_factory(user, due_date=d2, title="B")
        r = api_client.get(reverse("tasks:task-list"), {"date": d1.isoformat()})
        assert r.status_code == status.HTTP_200_OK
        titles = [t["title"] for t in r.data]
        assert "A" in titles and "B" not in titles

    def test_isolation_between_users(self, api_client, user_factory, task_factory):
        u1, u2 = user_factory(), user_factory()
        task_factory(u1, title="private")
        api_client.force_authenticate(user=u2)
        r = api_client.get(reverse("tasks:task-list"))
        assert r.status_code == status.HTTP_200_OK
        assert r.data == []

    def test_update_status_dragdrop(self, api_client, user_factory, task_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)
        t = task_factory(user)
        r = api_client.patch(
            reverse("tasks:task-detail", args=[t.id]),
            {"status": "done", "position": 5.5},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        t.refresh_from_db()
        assert t.status == "done"
        assert t.position == 5.5

    def test_delete_task(self, api_client, user_factory, task_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)
        t = task_factory(user)
        r = api_client.delete(reverse("tasks:task-detail", args=[t.id]))
        assert r.status_code == status.HTTP_204_NO_CONTENT