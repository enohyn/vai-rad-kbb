"""Model-level tests for tasks."""

import datetime

import pytest

from apps.tasks.models import Task


@pytest.mark.django_db
class TestTaskModel:
    def test_create_task_defaults(self, user_factory, task_factory):
        t = task_factory(user_factory())
        assert t.status == Task.Status.TODO
        assert t.priority == Task.Priority.MEDIUM
        assert t.tags == []
        assert t.position == 0.0

    def test_str_includes_status(self, user_factory, task_factory):
        t = task_factory(user_factory(), title="Write tests")
        assert "Write tests" in str(t)

    def test_user_relationship(self, user_factory, task_factory):
        u = user_factory()
        task_factory(u, title="A")
        task_factory(u, title="B")
        assert u.tasks.count() == 2