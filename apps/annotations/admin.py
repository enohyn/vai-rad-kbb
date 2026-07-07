"""Admin registration for annotations."""

from django.contrib import admin

from .models import AnnotatedImage, Polygon


@admin.register(AnnotatedImage)
class AnnotatedImageAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "original_filename", "created_at"]
    readonly_fields = ["image"]


@admin.register(Polygon)
class PolygonAdmin(admin.ModelAdmin):
    list_display = ["id", "image", "label", "created_at"]
