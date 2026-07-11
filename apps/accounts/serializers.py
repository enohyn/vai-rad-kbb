"""Serializers for the accounts app."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer; password is write-only."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)