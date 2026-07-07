"""
Models for the tasks app (the Kanban board).

A Task belongs to one User. Each task carries the fields required by the
task spec: title, priority, due date, tags, and a board column status.
"""

from django.conf import settings
from django.db import models


class Task(models.Model):
    """A single Kanban card.

    Field-by-field rationale
    ------------------------
    user        -> the owner. Tasks are private per user (multi-tenant by user).
    title       -> short headline shown on the card.
    description -> optional long text (the "body" of the card).
    priority    -> enum stored as text; choices enforced by Django at the form
                   layer and by the DB via a CHECK constraint (Django 5+).
    status      -> which column the card is in (TODO / IN_PROGRESS / DONE).
    due_date    -> the calendar day this card belongs to on the board. The
                   frontend DateSelector filters tasks by this field.
    tags        -> a JSON list of short labels (e.g. ["bug","urgent"]).
    position    -> float so drag-and-drop reordering can insert a card between
                   two others without rewriting every row (lexical ordering).
    created_at / updated_at -> audit timestamps.
    """

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
            # Speeds up the common "all tasks for user X on day Y" query.
            models.Index(fields=["user", "due_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"
