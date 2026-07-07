# Kanban + Annotation — Backend (Django)

The backend API for a 2-in-1 web app: a **date-based Kanban board** and an
**image polygon-annotation tool**. Built with **Django + Django REST Framework**,
**SimpleJWT** auth, and **SQLite** (Postgres-compatible) via the Django ORM.

> This README follows the task's storytelling theme: the *"villains"* are the
> hard problems we hit and how we defeated them.

---

## 🥷 The Villains We Faced (and How We Won)

### 🦹 Villain #1 — "Auth-token amnesia" (JWT logout that actually logs out)
**The problem:** With pure JWT, a refresh token stays valid until it expires. A
"logout" button that doesn't invalidate the token is theatre.

**The fix:** We enabled `rest_framework_simplejwt.token_blacklist`. On logout we
add the refresh token to a server-side blacklist (`OutstandingToken` /
`BlacklistedToken` tables). Rotated refresh tokens are blacklisted automatically.
*Power of friendship:* the [SimpleJWT docs](https://django-rest-framework-simplejwt.readthedocs.io/).

### 🦹‍♂️ Villain #2 — "The sneaky serializer" (data leakage)
**The problem:** A naive `User` serializer could echo `password` back in JSON.

**The fix:** `RegisterSerializer` uses `write_only=True` on the password field
and `validate_password` to run Django's password validators. There is a dedicated
unit test asserting `"password" not in response.data`.

### 🧟 Villain #3 — "Cross-tenant contamination"
**The problem:** User A must never see User B's tasks/images.

**The fix:** Every viewset overrides `get_queryset()` to filter by
`request.user`. Tests prove isolation (`test_isolation_between_users`).

### 👹 Villain #4 — "Pagination vs the Kanban"
**The problem:** DRF's default `PageNumberPagination` wraps lists in
`{count, next, results}`. A Kanban board for a *single date* wants a flat array.

**The fix:** Removed global pagination; each list endpoint returns the full,
already-scoped set. Tests assert `len(r.data) == N` (a list, not a dict).

### 🐉 Villain #5 — "The disappearing filename"
**The problem:** `ImageField` renames files to `annotations/xyz.png`; the
frontend wanted the *original* filename.

**The fix:** `AnnotatedImage.save()` auto-populates `original_filename` from the
uploaded file's basename if not set explicitly.

---

## 🧰 Tech Stack & Versions

| Tool | Version |
|------|---------|
| Python | **3.12** (see `runtime.txt`) |
| Django | **5.0.x** |
| Django REST Framework | **3.15.x** |
| djangorestframework-simplejwt | **5.3.x** |
| django-cors-headers | **4.4.x** |
| django-filter | **24.x** |
| django-environ | **0.11.x** |
| Pillow | **10.x** (image handling) |
| whitenoise | **6.7.x** (static files in prod) |
| pytest / pytest-django | **8.x / 4.x** |

Node version is only relevant for the **frontend** repo — this backend is pure
Python.

---

## 🚀 Run Locally (Detailed Steps)

### Prerequisites
- Python **3.12** installed (`python --version`)
- `pip` and `venv`

### 1. Clone & enter
```bash
git clone <your-backend-repo-url> backend
cd backend
```

### 2. Create & activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Copy the example and (optionally) edit values:
```bash
cp .env.example .env
```
`.env` contents (all have safe dev defaults):
```env
DEBUG=True
SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=http://localhost:3000
ACCESS_TOKEN_MINUTES=15
REFRESH_TOKEN_DAYS=7
```

### 5. Apply migrations & create the demo user
```bash
python manage.py migrate
python manage.py seed_demo_user
```
This creates the login user recruiters will use:
- **Email:** `demo@kanban.test`
- **Password:** `demoPass123!`

### 6. Run the tests (TDD ✅)
```bash
pytest -q
```
Expected: **30 passed**.

### 7. Start the dev server
```bash
python manage.py runserver
```
API base URL: `http://127.0.0.1:8000/api/`

---

## 📡 API Reference

All endpoints (except login/register) require:
```
Authorization: Bearer <access-token>
```

### Auth — `/api/auth/`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/register/` | Create account `{email, password, first_name, last_name}` |
| POST | `/login/` | `{email, password}` → `{access, refresh}` |
| GET | `/me/` | Current user's profile |
| POST | `/logout/` | `{refresh}` → blacklists the token (205) |

### Tasks — `/api/tasks/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/?date=YYYY-MM-DD` | List tasks for a date |
| POST | `/` | Create `{title, due_date, priority?, status?, tags?, position?}` |
| PATCH | `/:id/` | Update (used by drag-and-drop: `{status, position}`) |
| DELETE | `/:id/` | Remove a task |

Fields: `title`, `description`, `priority` (low/medium/high/urgent),
`status` (todo/in_progress/done), `due_date`, `tags` (JSON array),
`position` (float, for DnD ordering).

### Annotations — `/api/annotate/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/images/` | List uploaded images (includes polygons) |
| POST | `/images/` | Upload `multipart/form-data` field `image` |
| DELETE | `/images/:id/` | Remove an image |
| POST | `/polygons/` | `{image, points, label?, color?}` |
| DELETE | `/polygons/:id/` | Remove a single polygon |

`points` is a JSON array of `[x, y]` pixel coordinates, e.g.
`[[10, 20], [30, 40], [50, 60]]`.

---

## 🗂️ Project Structure

```
backend/
├── config/                 # Django project package (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # Feature-based Django apps
│   ├── accounts/           # User model + JWT auth endpoints
│   ├── tasks/              # Kanban task CRUD + date filtering
│   └── annotations/        # Image upload + polygon CRUD
├── manage.py
├── pytest.ini              # Points at ../kbb-tests/ (see Testing section)
├── requirements.txt
├── runtime.txt             # Python version for hosting
└── .env.example

# Tests live in a sibling folder, not inside the app packages:
../kbb-tests/
├── conftest.py             # Shared pytest fixtures
├── accounts/               # test_api.py, test_models.py
├── tasks/                  # test_api.py, test_models.py
└── annotations/            # test_api.py, test_models.py
```

---

## ☁️ Deployment (PythonAnywhere)

1. Push this repo to GitHub.
2. On PythonAnywhere: **Add a new web app** → **Manual config** → **Python 3.12**.
3. In a Bash console:
   ```bash
   git clone <repo> ~/backend && cd ~/backend
   python3.12 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_demo_user
   python manage.py collectstatic --noinput
   ```
4. Set the WSGI file to point at `config.wsgi`.
5. Add your PythonAnywhere domain to `ALLOWED_HOSTS` and the frontend URL to
   `CORS_ALLOWED_ORIGINS` via environment variables.

---

## 🧪 Testing Strategy (TDD)

Tests were written **first** (or alongside) implementation.

> **Note:** Tests live in a **sibling folder** (`../kbb-tests/`), not inside the
> Django app packages. `pytest.ini` points at that folder, so you still run pytest
> from the backend project root:

```bash
pytest -q          # run from vai-rad-kbb/
```

Coverage by app (30 tests total):
- `accounts`: register/login/me/logout + model behavior (16 tests)
- `tasks`: create/list/filter-by-date/isolation/drag-drop/delete + model (9 tests)
- `annotations`: upload/list/polygon create/delete + model (5 tests)

Shared fixtures (`api_client`, `user_factory`, `task_factory`, `image_factory`,
`png_upload`) live in `kbb-tests/conftest.py`.

---

## 📝 License & Credits

Built as a recruitment test task. The "power of friendship" came from the
official Django, DRF, and SimpleJWT documentation, plus Pillow for image
validation.