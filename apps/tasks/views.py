"""Views (viewsets) for the tasks app.

A ModelViewSet bundles list/retrieve/create/update/destroy into one class -
like a resource controller in Express with auto-generated CRUD handlers.
"""

from rest_framework import viewsets

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for tasks, scoped to the authenticated user.

    Filtering: ?date=YYYY-MM-DD returns only tasks for that calendar day.
    """

    serializer_class = TaskSerializer
    filterset_fields = ["due_date", "status", "priority"]

    def get_queryset(self):
        """Only ever return the requesting user's tasks (row-level security)."""
        qs = Task.objects.filter(user=self.request.user)
        # Allow an optional ?date=YYYY-MM-DD query param as a convenience alias
        # for the django-filter ?due_date=... param.
        date_param = self.request.query_params.get("date")
        if date_param:
            qs = qs.filter(due_date=date_param)
        return qs

    def perform_create(self, serializer):
        """Attach the logged-in user before saving."""
        serializer.save(user=self.request.user)
