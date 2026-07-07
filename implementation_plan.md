# Implementation Plan

[Overview]
A Django + Django REST Framework backend providing JWT-authenticated REST APIs for a Kanban task board (per-date, drag-and-drop) and an image-annotation tool (image upload + polygon persistence).

This backend is the persistence and business-logic layer for a decoupled React/Next.js + TypeScript frontend. It is a **greenfield project** built inside the existing (currently empty) directory `i:\kanban\vai-rad-kbb`. The machine already has **Python 3.14.6**, but 3.14 is too new for reliable binary wheels of several dependencies (Pillow, etc.), so the project must be built and run on **Python 3.12** (installed alongside 3.14 and invoked via `py -3.12`). Node 24 / npm 11 are present for the (separate, later) frontend task.

The backend implements three functional areas that mirror the frontend pages:

1. **Authentication** — email/password login issuing JWT access + refresh tokens, a registration endpoint (so a demo user can be created), and a "current user" profile endpoint. A custom `User` model uses `email` as the unique identifier (best practice for a new Django project and required for email login).
2. **Tasks (Kanban)** — tasks owned by a user, each with `title`, `priority`, `due_date`, `status` (To Do / In Progress / Done), `order` (for drag-and-drop positioning), and `tags`. The board is filtered by the selected date, implemented by filtering tasks on `due_date`. A bulk `reorder` action persists the new column ordering when a card is dragged.
3. **Annotations** — `Image` records (file upload) and `Annotation` polygon records (JSON coordinate arrays) belonging to a user. Polygons are created, updated, and deleted individually so the frontend can remove a specific drawn shape.

All endpoints are user-scoped (each user only sees and mutates their own tasks, tags, images, and annotations), protected by JWT authentication and object-level `IsOwner` permissions. The database is SQLite for development (as permitted by the task), with settings driven by environment variables so Postgres/MySQL can be used in production. CORS is configured for the Next.js dev server (`http://localhost:3000`). Deployment target is **PythonAnywhere** (Render documented as fallback).

The build follows **test-driven development**: for each app we write models + serializers first, then failing pytest tests defining the contract, then implement views/permissions until tests pass. This satisfies the "make test driven" requirement and gives strong ownership/isolation guarantees recruiters look for.

[Types]
No Python "types" module is required beyond Django ORM model fields; the data contracts are defined by DRF serializers. The following enumerations and JSON shapes define the type system for the API.

**Enum: Task.status** (`tasks.Task`)
- `todo` → "To Do"
- `in_progress` → "In Progress"
- `done` → "Done"

**Enum: Task.priority** (`tasks.Task`)
- `low` → "Low"
- `medium` → "Medium" (default)
- `high` → "High"

**JSON type: Annotation.points** (`annotations.Annotation.points`, stored in `JSONField`)
- A JSON array of normalized coordinate pairs, each pair an array of two floats in the range `0.0`–`1.0`, e.g. `[[0.12, 0.34], [0.45, 0.67], [0.78, 0.90]]`.
- Normalized (0–1) coordinates are resolution-independent: the frontend multiplies each value by the rendered image width/height to reconstruct the polygon. This keeps stored shapes valid if image display size changes.
- Validation rule: at least 3 coordinate pairs (minimum for a polygon). Enforced in `AnnotationSerializer.validate_points`.

**API request/response shapes (canonical contracts the frontend will consume):**

- `RegisterSerializer` (write): `{ email: string, name: string, password: string, password2: string }`
- `LoginRequest` (write, SimpleJWT): `{ email: string, password: string }`
- `TokenResponse` (read): `{ access: string, refresh: string }`
- `UserSerializer` (read): `{ id: int, email: string, name: string }`
- `TagSerializer` (read/write): `{ id: int, name: string, color: string }`
- `TaskReadSerializer` (read): `{ id: int, title: string, description: string, status: "todo"|"in_progress"|"done", priority: "low"|"medium"|"high", due_date: "YYYY-MM-DD", order: int, tags: TagSerializer[] }`
- `TaskWriteSerializer` (write): `{ title: string, description?: string, status?: string, priority?: string, due_date: "YYYY-MM-DD", order?: int, tag_ids?: int[] }`
- `ReorderItem` / `ReorderSerializer` (write): `{ items: [{ id: int, status: string, order: int }] }`
- `ImageSerializer` (read): `{ id: int, file: string(url), original_filename: string, uploaded_at: ISO8601, annotations: AnnotationSerializer[] }`
- `ImageUpload` (write, multipart): form-data field `file` (image)
- `AnnotationSerializer` (read/write): `{ id: int, image: int, label: string, points: number[][], color: string }`

**Validation rules (serializer-level):**
- `email`: valid email format, unique (case-insensitive) among users.
- `password`: minimum 8 characters (Django's `AUTH_PASSWORD_VALIDATORS` enabled).
- `Task.title`: required, 1–200 chars.
- `Task.due_date`: required, ISO date `YYYY-MM-DD`.
- `Annotation.points`: required, JSON array, length ≥ 3, each element a `[float, float]` pair with values in [0,1].

[Files]
All paths are relative to the project root `i:\kanban\vai-rad-kbb`. New files are created from scratch (greenfield).

**Project-scaffolding / config files (new):**
- `manage.py` — standard Django management entrypoint pointing to `config.settings`.
- `requirements/base.txt` — runtime deps: Django, DRF, simplejwt, cors-headers, django-filter, Pillow, django-environ, whitenoise.
- `requirements/dev.txt` — `-r base.txt` + pytest-django, pytest, factory-boy, black, ruff, isort.
- `requirements/prod.txt` — `-r base.txt` + gunicorn.
- `requirements.txt` — convenience pointer (`-r requirements/prod.txt`) for hosts that expect a single file.
- `.env.example` — template: `SECRET_KEY=`, `DEBUG=True`, `ALLOWED_HOSTS=*`, `CORS_ALLOWED_ORIGINS=http://localhost:3000`, `DATABASE_URL=sqlite:///db.sqlite3`.
- `.gitignore` — Python, venv, `db.sqlite3`, `media/`, `.env`, `__pycache__/`, IDE folders.
- `runtime.txt` — `python-3.12.x` (PythonAnywhere / Render Python version pin).
- `README.md` — difficulties/"villains" faced, Python 3.12 & Node versions, run steps, demo credentials, deployment notes (PythonAnywhere).
- `pytest.ini` / `setup.cfg` — pytest-django config (`DJANGO_SETTINGS_MODULE=config.settings`).
- `frontend_spec.md` — API contract handoff for the (later) frontend task.

**Project package `config/` (new):**
- `config/__init__.py`
- `config/settings.py` — settings using `django-environ`; installs apps; sets `AUTH_USER_MODEL`, DRF + SimpleJWT config, CORS, MEDIA, SQLite default DB.
- `config/urls.py` — root router: `admin/`, `api/auth/`, `api/tasks/`, `api/tags/`, `api/images/`, `api/annotations/`, plus `media/` serving in debug.
- `config/wsgi.py` — WSGI entrypoint (PythonAnywhere/Render).
- `config/asgi.py` — ASGI entrypoint.

**App: `apps/accounts/` (new) — authentication & user:**
- `apps/__init__.py`
- `apps/accounts/__init__.py`
- `apps/accounts/apps.py` — `AccountsConfig`, `default_auto_field = "django.db.models.BigAutoField"`.
- `apps/accounts/managers.py` — `UserManager` (email-based `create_user` / `create_superuser`).
- `apps/accounts/models.py` — `User` model (email as `USERNAME_FIELD`).
- `apps/accounts/admin.py` — register `User` with email-based admin.
- `apps/accounts/serializers.py` — `UserSerializer`, `RegisterSerializer`.
- `apps/accounts/views.py` — `RegisterView`, `MeView`, `LogoutView` (blacklist refresh).
- `apps/accounts/urls.py` — register, login, refresh, logout, me.
- `apps/accounts/tokens.py` — `EmailTokenObtainPairSerializer` (subclass SimpleJWT to authenticate by email).
- `apps/accounts/management/commands/seed_demo_user.py` — creates the demo recruiter login.
- `apps/accounts/migrations/__init__.py`

**App: `apps/tasks/` (new) — Kanban tasks + tags:**
- `apps/tasks/__init__.py`
- `apps/tasks/apps.py` — `TasksConfig`.
- `apps/tasks/models.py` — `Tag`, `Task`.
- `apps/tasks/admin.py` — register `Tag`, `Task`.
- `apps/tasks/serializers.py` — `TagSerializer`, `TaskReadSerializer`, `TaskWriteSerializer`, `ReorderSerializer`.
- `apps/tasks/views.py` — `TaskViewSet`, `TagViewSet` (ModelViewSets, `IsOwner`, date filter, `reorder` action).
- `apps/tasks/permissions.py` — `IsOwner` (handles `obj.user`).
- `apps/tasks/filters.py` — `TaskFilter` (filter by `due_date` query param).
- `apps/tasks/urls.py` — router registration.
- `apps/tasks/migrations/__init__.py`

**App: `apps/annotations/` (new) — images + polygons:**
- `apps/annotations/__init__.py`
- `apps/annotations/apps.py` — `AnnotationsConfig`.
- `apps/annotations/models.py` — `Image`, `Annotation`.
- `apps/annotations/admin.py` — register `Image`, `Annotation`.
- `apps/annotations/serializers.py` — `AnnotationSerializer`, `ImageSerializer` (nested annotations on read).
- `apps/annotations/views.py` — `ImageViewSet`, `AnnotationViewSet`.
- `apps/annotations/permissions.py` — `IsOwner` / `IsImageOwner`.
- `apps/annotations/urls.py` — routers (images + nested annotations).
- `apps/annotations/migrations/__init__.py`

**Tests (new, written TDD-style before/with each feature):**
- `apps/accounts/tests/__init__.py`
- `apps/accounts/tests/test_auth.py`
- `apps/tasks/tests/__init__.py`
- `apps/tasks/tests/test_tasks.py`
- `apps/tasks/tests/test_reorder.py`
- `apps/annotations/tests/__init__.py`
- `apps/annotations/tests/test_annotations.py`
- `tests/conftest.py` — pytest-django fixtures (api client, auth user, factories).

**Files to be deleted/moved:** None — greenfield project.

**Configuration updates:** `config/settings.py` is the single source of truth; environment-specific overrides are read from `.env` via `django-environ`.

[Functions]
Key functions and callables introduced (signatures in Python type style).

**Managers (`apps/accounts/managers.py`):**
- `UserManager.create_user(email: str, name: str, password: str | None = None, **extra_fields) -> User` — normalizes email, sets a usable password.
- `UserManager.create_superuser(email: str, name: str, password: str | None = None, **extra_fields) -> User` — enforces `is_staff=True`, `is_superuser=True`.

**Token serializer (`apps/accounts/tokens.py`):**
- `EmailTokenObtainPairSerializer.get_token(cls, user) -> Token` — adds `name`/`email` to the JWT claim.
- Override `username_field` handling so authentication accepts the `email` field instead of `username`.

**Views — accounts (`apps/accounts/views.py`):**
- `RegisterView.post(request) -> Response` — validates `RegisterSerializer`, creates user, issues access+refresh tokens, returns `201` with tokens and user.
- `MeView.get(request) -> Response` — returns the authenticated user serialized (`IsAuthenticated`).
- `LogoutView.post(request) -> Response` — blacklists the provided refresh token via `OutstandingToken`/`BlacklistedToken`.

**Serializers — accounts (`apps/accounts/serializers.py`):**
- `RegisterSerializer.validate_email(value) -> str` — case-insensitive uniqueness check.
- `RegisterSerializer.validate(attrs) -> dict` — confirms `password == password2`.
- `RegisterSerializer.create(validated_data) -> User` — delegates to `UserManager.create_user`.

**Serializers — tasks (`apps/tasks/serializers.py`):**
- `TaskReadSerializer` — nested `TagSerializer(many=True)` for output.
- `TaskWriteSerializer.create(validated_data) -> Task` — pops `tag_ids`, associates tags, sets `user=request.user`.
- `TaskWriteSerializer.update(instance, validated_data) -> Task` — updates `tag_ids` if present.
- `ReorderSerializer.validate_items(items) -> list` — ensures all task ids belong to `request.user`.

**Views — tasks (`apps/tasks/views.py`):**
- `TaskViewSet.get_queryset() -> QuerySet[Task]` — returns `request.user.tasks` ordered by `('due_date', 'status', 'order')`, filtered by `?date=` via `TaskFilter`.
- `TaskViewSet.perform_create(serializer)` — sets `user=self.request.user`.
- `TaskViewSet.reorder(request) -> Response` — `@action(detail=False, methods=['patch'])`; accepts `ReorderSerializer`, updates `status` + `order` for each task id atomically (`transaction.atomic`).
- `TagViewSet.get_queryset() -> QuerySet[Tag]` — returns `request.user.tags`.
- `TagViewSet.perform_create(serializer)` — sets `user`.

**Serializers — annotations (`apps/annotations/serializers.py`):**
- `AnnotationSerializer.validate_points(value) -> list` — enforces ≥ 3 pairs and each coord in [0,1].
- `ImageSerializer` — on retrieve, includes nested `AnnotationSerializer(many=True)`; `file` is the URL field.

**Views — annotations (`apps/annotations/views.py`):**
- `ImageViewSet.get_queryset() -> QuerySet[Image]` — returns `request.user.images`.
- `ImageViewSet.perform_create(serializer)` — sets `user`, records `original_filename` from the uploaded file.
- `AnnotationViewSet.get_queryset() -> QuerySet[Annotation]` — filters by `image_id` from the URL kwarg and ensures the image is owned by `request.user`.
- `AnnotationViewSet.perform_create(serializer)` — sets `image` from the validated URL kwarg.

**Management command (`apps/accounts/management/commands/seed_demo_user.py`):**
- `Command.handle(*args, **options)` — creates (idempotently) the demo user with email/password from env or defaults, prints credentials.

**No existing functions are modified or removed** (greenfield).

[Classes]
Classes introduced (all new; no removals).

- **`accounts.User`** (`AbstractUser`) — fields: `email` (unique), `name` (CharField 150), plus inherited `is_active`, `is_staff`, `is_superuser`, `date_joined`. `USERNAME_FIELD = "email"`, `REQUIRED_FIELDS = ["name"]`. Removes the `username` field. Methods: `__str__`.
- **`accounts.UserManager`** (`BaseUserManager`) — see Functions; used as `User.objects`.
- **`accounts.RegisterView`** (`generics.CreateAPIView`) — serializer_class `RegisterSerializer`.
- **`accounts.MeView`** (`generics.RetrieveAPIView`) — serializer_class `UserSerializer`, permission `IsAuthenticated`, returns `request.user`.
- **`accounts.LogoutView`** (`APIView`) — blacklists refresh token.
- **`tasks.Tag`** (`models.Model`) — `user` (FK User), `name` (CharField 50), `color` (CharField 7, blank). Meta: `unique_together = ("user", "name")`.
- **`tasks.Task`** (`models.Model`) — `user` (FK User), `title` (CharField 200), `description` (TextField blank), `status` (CharField choices, default `todo`), `priority` (CharField choices, default `medium`), `due_date` (DateField), `order` (IntegerField default 0), `tags` (M2M Tag, blank), `created_at`, `updated_at`.
- **`tasks.TaskFilter`** (`django_filters.FilterSet`) — exposes `date` (exact match on `due_date`).
- **`tasks.TaskViewSet`** (`viewsets.ModelViewSet`) — permission `IsAuthenticated`, `IsOwner`; filterset `TaskFilter`; `reorder` action.
- **`tasks.TagViewSet`** (`viewsets.ModelViewSet`) — permission `IsOwner`.
- **`tasks.permissions.IsOwner`** (`permissions.BasePermission`) — `has_object_permission`: `obj.user == request.user`.
- **`annotations.Image`** (`models.Model`) — `user` (FK User), `file` (ImageField upload_to `images/`), `original_filename` (CharField 255 blank), `uploaded_at`.
- **`annotations.Annotation`** (`models.Model`) — `image` (FK Image, cascade), `label` (CharField 100 blank), `points` (JSONField), `color` (CharField 7 blank), `created_at`, `updated_at`.
- **`annotations.ImageViewSet`** (`viewsets.ModelViewSet`) — list/retrieve/create/destroy (no update needed); `IsOwner`.
- **`annotations.AnnotationViewSet`** (`viewsets.ModelViewSet`) — scoped to `image_id`; create/retrieve/update/destroy; `IsImageOwner`.

**Modified classes:** None (greenfield).

[Dependencies]
Python packages (pinned in `requirements/`), targeting **Python 3.12**.

Runtime (`base.txt`):
- `Django==5.0.6` — web framework (Django ORM required by the task).
- `djangorestframework==3.15.2` — serializers, viewsets, browsable API.
- `djangorestframework-simplejwt==5.3.1` — JWT auth (access + refresh).
- `django-cors-headers==4.4.0` — allow the Next.js origin.
- `django-filter==24.2` — `TaskFilter` for `?date=` filtering.
- `Pillow==10.4.0` — required by `ImageField` for image uploads.
- `django-environ==0.11.2` — 12-factor config from `.env`.
- `whitenoise==6.7.0` — static-file serving in production.

Dev (`dev.txt`, extends base):
- `pytest==8.3.1`, `pytest-django==4.8.0` — test runner.
- `factory-boy==3.3.0` — test data factories.
- `black==24.4.2`, `ruff==0.5.1`, `isort==5.13.2` — formatting/linting.

Prod (`prod.txt`, extends base):
- `gunicorn==22.0.0` — WSGI server (used on Render; PythonAnywhere uses its own WSGI).

System prerequisites: **Python 3.12 must be installed** (via `winget install Python.Python.3.12` or the python.org installer). The existing Python 3.14 is left in place but not used; the project venv is created with `py -3.12 -m venv .venv`. Node 24 / npm 11 are already installed for the (separate) frontend. No other system packages required; SQLite ships with Python.

[Testing]
Use `pytest-django` with the Django test client; `factory-boy` for fixtures. Tests are written **before** the view layer where practical (define the expected status codes / payload shapes, then implement until green).

**Test files:**
- `apps/accounts/tests/test_auth.py` — register (success, duplicate email 400, mismatched password 400), login (valid → tokens, invalid → 401), `/me` (authenticated 200, anonymous 401), logout blacklists refresh.
- `apps/tasks/tests/test_tasks.py` — create task, list filtered by `?date=`, update status, delete; cross-user access returns 404 (enforced via ownership, not leakage); tags association round-trips.
- `apps/tasks/tests/test_reorder.py` — `reorder` action reorders within and across columns; atomic on partial failure; rejects ids not owned by the user.
- `apps/annotations/tests/test_annotations.py` — image upload (multipart), list images with nested annotations, create polygon (valid + invalid <3 points 400), delete a specific annotation, delete image cascades annotations.

**Validation strategy:** every endpoint asserts (1) happy path status + payload shape, (2) authentication required, (3) object-level ownership isolation. The demo-user seed command is smoke-tested manually.

**Running tests:** `pytest` (configured via `pytest.ini` with `DJANGO_SETTINGS_MODULE=config.settings`). Coverage target ≥ 90% on the apps.

[Implementation Order]
1. Ensure **Python 3.12** is installed (`py -3.12 --version`); if missing, install via `winget install Python.Python.3.12`. Create the virtualenv inside `i:\kanban\vai-rad-kbb` with `py -3.12 -m venv .venv`, activate it (`.\.venv\Scripts\Activate.ps1`), upgrade pip, and verify `python --version` prints `3.12.x`.
2. Scaffold the project: create `requirements/` files (`base.txt`, `dev.txt`, `prod.txt`, `requirements.txt`), `pip install -r requirements/dev.txt`, then `django-admin startproject config .` and the three apps (`python manage.py startapp accounts`, `tasks`, `annotations`) relocated under `apps/`; create `apps/__init__.py`, `apps/<app>/migrations/__init__.py`.
3. Configure `config/settings.py`: `django-environ`-driven `SECRET_KEY`/`DEBUG`/`DATABASE_URL`, `INSTALLED_APPS` (DRF, simplejwt, corsheaders, django_filters, apps), `AUTH_USER_MODEL = "accounts.User"`, DRF default auth/permission classes (JWT + `IsAuthenticated`), SimpleJWT lifetimes, CORS allowed origins, MEDIA root/url, password validators; add `.env.example`, `.gitignore`, `runtime.txt`, `pytest.ini`.
4. Build the `accounts` app (TDD): write `test_auth.py` expectations first, then implement `UserManager` + `User` model, run `makemigrations accounts` then `migrate`, admin registration, `EmailTokenObtainPairSerializer`, register/login/refresh/logout/me endpoints, and the `seed_demo_user` management command; run `pytest apps/accounts` until green.
5. Build the `tasks` app (TDD): write `test_tasks.py` + `test_reorder.py` expectations first, then implement `Tag` + `Task` models (with `order` and M2M tags), migrations, `TagSerializer`/`TaskReadSerializer`/`TaskWriteSerializer`/`ReorderSerializer`, `IsOwner` permission, `TaskFilter` (date), `TaskViewSet` (+ `reorder` action), `TagViewSet`, and URL routing; run `pytest apps/tasks` until green.
6. Build the `annotations` app (TDD): write `test_annotations.py` expectations first, then implement `Image` (with `ImageField`) + `Annotation` (JSONField points) models, migrations, serializers with polygon validation, `ImageViewSet` (upload/list/delete) and `AnnotationViewSet` (nested CRUD + ownership), URL routing; run `pytest apps/annotations` until green.
7. Wire the root `config/urls.py` (admin + `/api/...` prefixes + media serving in debug); run full `pytest`; run the seed command to create the demo user, and smoke-test all endpoints with `curl` (register → login → create task → reorder → upload image → add polygon → delete polygon).
8. Write `README.md` (difficulties/villains section, Python 3.12 + Node versions, step-by-step run instructions, demo credentials, PythonAnywhere deployment notes) and `frontend_spec.md` (API contract handoff); finalize `requirements*.txt`, `.env.example`, `.gitignore`; commit to a fresh `git` repo.