# Kanban + Annotation — Backend (Django)

The backend API for a 2-in-1 web app: a **date-based Kanban board** and an
**image polygon-annotation tool**. Built with **Django + Django REST Framework**,
**SimpleJWT** auth, and **SQLite** (Postgres-compatible) via the Django ORM.

---

## 🧰 Tech Stack

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

---

## 🚀 Run Locally

### Prerequisites
- Python **3.12** (`python --version`)
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
This creates a demo login:
- **Email:** `demo@kanban.test`
- **Password:** `demoPass123!`

### 6. Run the tests
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

Fields: `title`, `description`, `priority` (low/medium/high),
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

## 🔒 Security Notes

- **JWT logout:** Refresh tokens are added to a server-side blacklist
  (`rest_framework_simplejwt.token_blacklist`) on logout, so tokens are
  actually invalidated rather than just discarded client-side.
- **Password handling:** The `User` serializer marks `password` as
  `write_only`, so it is never included in API responses.
- **Row-level isolation:** Every viewset filters by `request.user`, so
  users can only access their own tasks and images.

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
├── pytest.ini              # Points at tests/ folder
├── requirements.txt
├── runtime.txt             # Python version for hosting
└── .env.example

tests/
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

## 🧪 Testing

```bash
pytest -q
```

Tests live in a `tests/` folder inside the repo. `pytest.ini` points at that
folder, so you run pytest from the project root.

Coverage by app (30 tests total):
- `accounts`: register/login/me/logout + model behavior (16 tests)
- `tasks`: create/list/filter-by-date/isolation/drag-drop/delete + model (9 tests)
- `annotations`: upload/list/polygon create/delete + model (5 tests)

Shared fixtures (`api_client`, `user_factory`, `task_factory`, `image_factory`,
`png_upload`) live in `tests/conftest.py`.