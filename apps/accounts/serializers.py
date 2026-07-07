"""
Serializers for the accounts app.

A *serializer* converts a model instance <-> Python dict <-> JSON, and applies
validation rules. Think of it as a Zod / Joi schema that also knows how to read
and write the database.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Reads/writes a User. Password is write-only (never sent back in JSON)."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {
            # write_only => accepted on create/update but excluded from responses.
            "password": {"write_only": True, "min_length": 8},
        }

    def create(self, validated_data):
        """Use the manager's create_user so the password gets hashed."""
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)
