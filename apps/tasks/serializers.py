"""Serializers for the tasks app."""

from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer; `user` is read-only (set from the JWT)."""

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
        if not isinstance(value, list):
            raise serializers.ValidationError("tags must be a list.")
        if not all(isinstance(t, str) for t in value):
            raise serializers.ValidationError("All tags must be strings.")
        return value