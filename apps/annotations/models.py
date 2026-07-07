"""
Models for the annotations app.

An AnnotatedImage is an uploaded picture belonging to a user.
A Polygon is one shape drawn on top of that image (a list of x/y points).
"""

from django.conf import settings
from django.db import models


class AnnotatedImage(models.Model):
    """An uploaded image that can have multiple polygons drawn on it."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="images",
    )
    # ImageField stores a path; the file itself lives in MEDIA_ROOT.
    image = models.ImageField(upload_to="annotations/")
    original_filename = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "annotated_images"

    def save(self, *args, **kwargs):
        # Auto-populate original_filename from the uploaded file's name if it
        # wasn't set explicitly (keeps ORM-level creates consistent with the API).
        if not self.original_filename and self.image:
            self.original_filename = self.image.name.rsplit("/", 1)[-1]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.original_filename or f"Image {self.id}"


class Polygon(models.Model):
    """A single polygon annotation on an image.

    points is a JSON list of [x, y] coordinate pairs in image-pixel space,
    e.g. [[10, 20], [30, 40], [50, 60]]. Stored as JSONField for portability
    across SQLite/Postgres and easy consumption by the canvas frontend.
    """

    image = models.ForeignKey(
        AnnotatedImage,
        on_delete=models.CASCADE,
        related_name="polygons",
    )
    label = models.CharField(max_length=80, blank=True)
    points = models.JSONField()
    color = models.CharField(max_length=9, default="#ff0000")  # #RRGGBB
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        db_table = "polygons"

    def __str__(self) -> str:
        return f"Polygon {self.id} on {self.image_id}"
