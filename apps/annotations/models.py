"""Models for the annotations app."""

from django.conf import settings
from django.db import models


class AnnotatedImage(models.Model):
    """An uploaded image that can have multiple polygons drawn on it."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="annotations/")
    original_filename = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "annotated_images"

    def save(self, *args, **kwargs):
        if not self.original_filename and self.image:
            self.original_filename = self.image.name.rsplit("/", 1)[-1]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.original_filename or f"Image {self.id}"


class Polygon(models.Model):
    """A polygon annotation on an image.

    ``points`` is a JSON list of ``[x, y]`` pixel coordinate pairs.
    """

    image = models.ForeignKey(
        AnnotatedImage,
        on_delete=models.CASCADE,
        related_name="polygons",
    )
    label = models.CharField(max_length=80, blank=True)
    points = models.JSONField()
    color = models.CharField(max_length=9, default="#ff0000")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        db_table = "polygons"

    def __str__(self) -> str:
        return f"Polygon {self.id} on {self.image_id}"