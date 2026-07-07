"""
Root URL routing for the Kanban + Annotation API.

URL hierarchy
-------------
``/api/auth/``      -> JWT login, refresh, logout (SimpleJWT)
``/api/tasks/``     -> CRUD for the Kanban board
``/api/annotate/``  -> image upload + polygon persistence

Admin lives at ``/admin/`` for debugging data.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin (built-in dashboard). Useful for quick data inspection.
    path("admin/", admin.site.urls),

    # Auth: token obtain (login), refresh, blacklist (logout).
    path("api/auth/", include(("apps.accounts.urls", "accounts"), namespace="auth")),

    # Feature: Kanban tasks.
    path("api/tasks/", include(("apps.tasks.urls", "tasks"), namespace="tasks")),

    # Feature: image annotation.
    path(
        "api/annotate/",
        include(("apps.annotations.urls", "annotations"), namespace="annotations"),
    ),
]
