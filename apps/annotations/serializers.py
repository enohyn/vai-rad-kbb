"""Serializers for the annotations app."""

from rest_framework import serializers

from .models import AnnotatedImage, Polygon


class PolygonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Polygon
        fields = ["id", "image", "label", "points", "color", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AnnotatedImageSerializer(serializers.ModelSerializer):
    # Nested read: include this image's polygons when serializing.
    polygons = PolygonSerializer(many=True, read_only=True)

    class Meta:
        model = AnnotatedImage
        fields = [
            "id",
            "user",
            "image",
            "original_filename",
            "polygons",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "original_filename", "created_at", "updated_at"]
