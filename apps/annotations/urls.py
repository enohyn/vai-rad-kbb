"""URL routes for the annotations app."""

from rest_framework.routers import DefaultRouter

from .views import AnnotatedImageViewSet, PolygonViewSet

router = DefaultRouter()
router.register(r"images", AnnotatedImageViewSet, basename="image")
router.register(r"polygons", PolygonViewSet, basename="polygon")

urlpatterns = router.urls
