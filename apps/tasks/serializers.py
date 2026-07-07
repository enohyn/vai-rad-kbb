"""Serializers for the tasks app."""

from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Converts Task <-> JSON and enforces validation.

    The `user` field is read-only because it is inferred from the JWT of the
    request, never trusted from the payload (security: prevents IDOR).
    """

    class Meta:
        model = Task
        fields = [
            "id",
            "user",
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "tags",
            "position",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_tags(self, value):
        """Ensure tags is a list of strings."""
        if not isinstance(value, list):
            raise serializers.ValidationError("tags must be a list.")
        if not all(isinstance(t, str) for t in value):
            raise serializers.ValidationError("All tags must be strings.")
        return value
