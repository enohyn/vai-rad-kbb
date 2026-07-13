"""Root URL routing for the Kanban + Annotation API."""

from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    # Health-check endpoint for load balancers.
    path(
        "api/health/",
        lambda request: JsonResponse({"status": "ok"}),
        name="health",
    ),

    path("admin/", admin.site.urls),

    # Auth: token obtain (login), refresh, blacklist (logout).
    path("api/auth/", include(("apps.accounts.urls", "accounts"), namespace="auth")),

    # Kanban tasks.
    path("api/tasks/", include(("apps.tasks.urls", "tasks"), namespace="tasks")),

    # Image annotation.
    path(
        "api/annotate/",
        include(("apps.annotations.urls", "annotations"), namespace="annotations"),
    ),
]

# Serve uploaded media files via Django itself, regardless of DEBUG.
#
# In a "pure" production setup, media is served by the host (e.g. a
# PythonAnywhere /media/ static-files mapping) and Django does NOT serve them.
# In practice on PythonAnywhere's free tier that static mapping is fragile
# (it requires a manual Reload after every change and sometimes silently fails
# to intercept requests, causing 404s for uploaded annotation images). For this
# low-traffic demo we deliberately serve media through Django so the frontend
# works reliably regardless of host configuration.
#
# NOTE: ``django.conf.urls.static.static()`` is a no-op when DEBUG=False, so we
# wire ``serve`` explicitly here to make it work in production too. Remove this
# block if you move to a host that serves MEDIA_ROOT directly (nginx, S3, etc.).
_media_prefix = settings.MEDIA_URL.lstrip("/")
urlpatterns += [
    re_path(
        rf"^{_media_prefix}(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
] 
