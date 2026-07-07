# From JavaScript to Django — A Cheat Sheet for This Project

> You come from a JS/TS background and need to *explain* this Django backend in
> an interview. This doc maps every concept here to something you already know.

---

## 1. The mental model

| JavaScript world | Django world |
|---|---|
| `package.json` | `requirements.txt` (+ `pip`) |
| `node_modules/` | `.venv/` (virtual environment — per-project packages) |
| `npm install` | `pip install -r requirements.txt` |
| `npm run dev` | `python manage.py runserver` |
| Express `app.js` | `config/settings.py` + `config/urls.py` |
| `app.get('/x', handler)` | `urls.py` route → `views.py` function/class |
| Mongoose / Prisma model | `models.py` (Django ORM) |
| `fetch('/api/x')` | same on the frontend; backend exposes REST endpoints |
| JWT in Express | `djangorestframework-simplejwt` |
| Jest / Vitest | `pytest` |
| `npm test` | `pytest` |

---

## 2. Project layout (why it looks the way it does)

```
config/   ← the "project" (like the Express app bootstrap)
apps/     ← feature folders (like /routes, /controllers, /models combined)
  accounts/   ← login/register
  tasks/      ← Kanban
  annotations/← image drawing
```

A **Django app** is a self-contained module: it brings its own `models.py`,
`views.py`, `urls.py`, `serializers.py`, and `tests/`. This is Django's
"batteries-included" convention — you don't choose the structure, you follow it.

---

## 3. Models (the ORM) — `models.py`

A model is a class that becomes a database table.

```python
class Task(models.Model):          # → table "tasks"
    title = models.CharField(...)  # → VARCHAR column
    due_date = models.DateField()  # → DATE column
    tags = models.JSONField()      # → JSON column
```

**Equivalent in Prisma:**
```prisma
model Task {
  id       Int      @id @default(autoincrement())
  title    String
  dueDate  DateTime @db.Date
  tags     Json
}
```

**Migrations** (`python manage.py makemigrations` → `migrate`) are like
`prisma migrate`. They generate versioned SQL files in `migrations/`.

### Querying
```python
Task.objects.filter(user=request.user, due_date=the_date)
```
is the same idea as:
```js
await prisma.task.findMany({ where: { userId, dueDate } })
```

---

## 4. Views & ViewSets — `views.py`

A **ViewSet** is DRF's way of saying "one class handles list/create/retrieve/
update/destroy for a resource" — like a REST resource controller.

```python
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_fields = ["due_date"]   # allows ?date=... (mapped below)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
```

`get_queryset()` scoped to `request.user` is the **auth-based data isolation** —
the single most important security line in the file.

---

## 5. Serializers — `serializers.py`

A serializer does two jobs:
1. **Validation** on input (like a Zod schema).
2. **Rendering** on output (Model → JSON).

```python
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["user"]   # server sets it, never the client
```

---

## 6. URLs — `urls.py`

```python
router = routers.DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")
```
This auto-generates:
- `GET    /api/tasks/`        → list
- `POST   /api/tasks/`        → create
- `GET    /api/tasks/:id/`    → retrieve
- `PATCH  /api/tasks/:id/`    → partial update
- `DELETE /api/tasks/:id/`    → destroy

Just like `express.Router()` + resource routes.

---

## 7. Authentication — SimpleJWT

Flow (identical to an Express JWT app):

1. `POST /api/auth/login/` with `{email, password}` → returns
   `{access, refresh}`.
2. Frontend stores `access` (short-lived, 15 min) and `refresh` (7 days).
3. Every request sends `Authorization: Bearer <access>`.
4. When `access` expires, `POST /api/auth/refresh/` with `{refresh}` to get a
   new one.
5. `POST /api/auth/logout/` with `{refresh}` → server blacklists it.

`config/settings.py` → `REST_FRAMEWORK` sets `JWTAuthentication` globally so you
never annotate individual views.

---

## 8. Custom User model — `accounts/models.py`

Django ships a username-based `User`. We replaced it with an **email-based**
model:

```python
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    # ...
    USERNAME_FIELD = "email"
```

**Why?** Modern apps log in with email, not username. Setting
`AUTH_USER_MODEL = "accounts.User"` **before the first migration** is the
supported way to customize it.

---

## 9. Testing — pytest

```python
@pytest.mark.django_db
def test_create_task(api_client, user_factory):
    user = user_factory()
    api_client.force_authenticate(user=user)
    r = api_client.post(reverse("tasks:task-list"), {...})
    assert r.status_code == 201
```

- `@pytest.mark.django_db` → "this test can touch the database" (uses a
  transaction that rolls back after — like a test DB in Jest).
- `api_client` is DRF's `APIClient` (like `supertest`).
- `user_factory` is a pytest fixture (like a beforeEach helper) defined in
  `conftest.py`.

Run: `pytest -q` → 30 passed.

---

## 10. Configuration & environment

`django-environ` reads `.env`:
```python
DEBUG = env.bool("DEBUG", default=False)
DATABASES = {"default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3")}
```
Identical pattern to `dotenv` + `process.env` in Node.

---

## 11. Interview one-liners you can say

- *"I scoped every queryset to `request.user`, so users can't read each other's
  data — there's a test proving it."*
- *"Auth uses JWT with a refresh-token blacklist, so logout actually revokes
  access."*
- *"The API is fully tested with pytest — 30 tests across three apps."*
- *"I disabled global pagination because a Kanban board needs the whole day's
  tasks in one response."*
- *"Image polygons are stored as a JSONField of `[x, y]` pairs — portable across
  SQLite and Postgres, and trivial for the canvas to consume."*
- *"The custom `User` model is email-based and set via `AUTH_USER_MODEL` before
  the first migration, which is Django's recommended pattern."*