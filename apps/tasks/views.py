"""Views for the tasks app."""

from rest_framework import viewsets

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for tasks, scoped to the authenticated user."""

    serializer_class = TaskSerializer
    filterset_fields = ["due_date", "status", "priority"]

    def get_queryset(self):
        qs = Task.objects.filter(user=self.request.user)
        date_param = self.request.query_params.get("date")
        if date_param:
            qs = qs.filter(due_date=date_param)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)