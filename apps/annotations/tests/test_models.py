"""Tests for the annotations models."""

import pytest

from apps.annotations.models import Polygon


@pytest.mark.django_db
class TestAnnotationModels:
    def test_image_has_filename(self, user_factory, image_factory):
        img = image_factory(user_factory())
        # image_factory names files img1.png, img2.png, ...
        assert img.original_filename.startswith("img")

    def test_polygon_relation(self, user_factory, image_factory):
        u = user_factory()
        img = image_factory(u)
        Polygon.objects.create(image=img, points=[[0, 0], [1, 0], [1, 1]], label="roof")
        assert img.polygons.count() == 1
        assert img.polygons.first().label == "roof"