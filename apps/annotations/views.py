"""Views for the annotations app."""

from rest_framework import viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from .models import AnnotatedImage, Polygon
from .serializers import AnnotatedImageSerializer, PolygonSerializer


class AnnotatedImageViewSet(viewsets.ModelViewSet):
    """Upload, list, retrieve, delete images.

    Multi-part form uploads are supported via MultiPartParser.
    """

    serializer_class = AnnotatedImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return AnnotatedImage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Stash the original filename for friendly display in the UI.
        upload = self.request.FILES.get("image")
        original = upload.name if upload else ""
        serializer.save(user=self.request.user, original_filename=original)


class PolygonViewSet(viewsets.ModelViewSet):
    """CRUD for polygons belonging to the requesting user's images."""

    serializer_class = PolygonSerializer

    def get_queryset(self):
        # Only polygons whose image belongs to the current user (row-level).
        return Polygon.objects.filter(image__user=self.request.user)
