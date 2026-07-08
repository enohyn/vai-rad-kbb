"""
Django settings for the Kanban + Annotation backend.

WHY THIS FILE EXISTS
--------------------
In Django, ``settings.py`` is the single configuration hub — like a combined
``.env`` loader + ``app.js`` + middleware pipeline in an Express app. Every
constant here is read by Django at startup to wire the database, auth, apps,
CORS, file storage, etc.

We read sensitive values from a ``.env`` file via ``django-environ`` so that
no secrets live in source control (the "12-factor app" methodology).
"""

# ---------------------------------------------------------------------------
# 0. Imports & path setup
# ---------------------------------------------------------------------------
from datetime import timedelta  # built-in: used to express JWT token lifetimes
from pathlib import Path  # built-in: object-oriented filesystem paths

import environ  # third-party: django-environ, reads .env into a dict-like API

# BASE_DIR = the project root (the folder containing manage.py).
# Path(__file__) = this settings.py file; .resolve().parent.parent walks up twice:
# settings.py -> config/ -> project root.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# 1. Environment variables (.env)
# ---------------------------------------------------------------------------
# env.read_env() loads the .env file at the project root into os.environ.
# If .env is missing (e.g. on a fresh clone), environ falls back to real env
# vars, so we also provide safe DEBUG-based defaults below.
env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
# In JS land this is like process.env.SECRET_KEY; we default to an insecure
# dev key only when DEBUG is True so production never accidentally starts
# without a real key.
DEBUG = env.bool("DEBUG", default=False)
SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-dev-only-key-do-not-use-in-production" if DEBUG else None,
)

# Hosts/domains Django will respond to. "*" only when debugging locally.
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"] if DEBUG else [])

# ---------------------------------------------------------------------------
# 2. Applications (Django "apps" are like Node modules / feature folders)
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django built-ins (like node_modules shipped with the framework)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",  # DRF: serializers, viewsets, browsable API
    "rest_framework_simplejwt.token_blacklist",  # lets us invalidate refresh tokens on logout
    "corsheaders",  # Cross-Origin Resource Sharing for the Next.js frontend
    "django_filters",  # declarative filtering (?date=...)
    # Our local apps (created under apps/)
    "apps.accounts",
    "apps.tasks",
    "apps.annotations",
]

# Tell Django to use OUR custom User model (email-based) instead of the
# default username-based one. MUST be set BEFORE the first migrate.
AUTH_USER_MODEL = "accounts.User"

# ---------------------------------------------------------------------------
# 3. Middleware (request/response pipeline; like Express middleware chain)
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serve static files in production without a reverse proxy.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # must sit above CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"  # which urls.py is the root router

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"  # entry point for servers (gunicorn, PythonAnywhere)

# ---------------------------------------------------------------------------
# 4. Database (default SQLite for dev; DATABASE_URL can point to Postgres)
# ---------------------------------------------------------------------------
# environ's db() helper parses a URL like "sqlite:///db.sqlite3" or
# "postgres://user:pass@host:5432/db" into the dict Django expects.
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3"),
}

# ---------------------------------------------------------------------------
# 5. Password validation (run on signup + password change)
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# 6. Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# 7. Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # `collectstatic` outputs here for prod

MEDIA_URL = "media/"  # URL prefix for uploaded images
MEDIA_ROOT = BASE_DIR / "media"  # filesystem folder where uploads are stored

# WhiteNoise: serve compressed static files in production (no nginx needed).
# In dev Django's default staticfiles storage is used (DEBUG=True serves them).
if not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# 8. Django REST Framework global config
# ---------------------------------------------------------------------------
# These defaults are applied to EVERY DRF view unless overridden.
# - Authentication: JSON Web Tokens (Bearer token in the Authorization header).
# - Permissions: a user must be authenticated by default.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    # No global pagination: a Kanban board needs all tasks/images for the
    # selected scope (a single date) in one response. Per-view pagination can
    # still be added later if lists grow large.
}

# ---------------------------------------------------------------------------
# 9. SimpleJWT settings (token lifetimes + claim customization)
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    # Access tokens are short-lived (minutes) — limits damage if leaked.
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("ACCESS_TOKEN_MINUTES", default=15)
    ),
    # Refresh tokens are long-lived (days) — used to get a new access token.
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int("REFRESH_TOKEN_DAYS", default=7)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    # The login field on our custom User model is "email", not "username".
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------------------------------------------------------------------------
# 10. CORS — which origins may call this API from a browser
# ---------------------------------------------------------------------------
# In dev the Next.js app runs on http://localhost:3000.
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000"],
)
# Allow cookies / Authorization headers through CORS.
CORS_ALLOW_CREDENTIALS = True