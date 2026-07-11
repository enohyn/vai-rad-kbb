"""Task model for the Kanban board."""

from django.conf import settings
from django.db import models


class Task(models.Model):
    """A single Kanban card."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.TODO
    )
    due_date = models.DateField()
    tags = models.JSONField(default=list, blank=True)
    position = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "position", "-created_at"]
        db_table = "tasks"
        indexes = [
            models.Index(fields=["user", "due_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"