"""API tests for the annotations endpoints."""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestImageEndpoints:
    def test_upload_requires_auth(self, api_client):
        r = api_client.post(reverse("annotations:image-list"), {})
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_then_list(self, api_client, user_factory, png_upload):
        user = user_factory()
        api_client.force_authenticate(user=user)
        r = api_client.post(
            reverse("annotations:image-list"),
            {"image": png_upload("avatar.png")},
            format="multipart",
        )
        assert r.status_code == status.HTTP_201_CREATED, r.content
        image_id = r.data["id"]
        # original_filename should reflect the uploaded file's name
        assert r.data["original_filename"] == "avatar.png"
        r = api_client.get(reverse("annotations:image-list"))
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data) == 1
        assert r.data[0]["id"] == image_id


@pytest.mark.django_db
class TestPolygonEndpoints:
    def test_create_and_delete_polygon(self, api_client, user_factory, png_upload):
        user = user_factory()
        api_client.force_authenticate(user=user)
        # upload image first
        r = api_client.post(
            reverse("annotations:image-list"),
            {"image": png_upload()},
            format="multipart",
        )
        image_id = r.data["id"]
        # create polygon
        r = api_client.post(
            reverse("annotations:polygon-list"),
            {"image": image_id, "points": [[0, 0], [2, 0], [2, 2]], "label": "x"},
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED, r.content
        poly_id = r.data["id"]
        # delete polygon
        r = api_client.delete(reverse("annotations:polygon-detail", args=[poly_id]))
        assert r.status_code == status.HTTP_204_NO_CONTENT