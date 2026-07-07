"""Admin registration for tasks."""

from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "status", "priority", "due_date"]
    list_filter = ["status", "priority", "due_date"]
    search_fields = ["title", "description"]
    date_hierarchy = "due_date"
