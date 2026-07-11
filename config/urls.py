"""Root URL routing for the Kanban + Annotation API."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

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