# 🚀 Deployment Guide

This backend can be deployed to **Render.com** (recommended — auto-deploys from
GitHub) or **PythonAnywhere** (manual but the task's suggested host).

Both free tiers work for a recruitment demo.

---

## Option A: Render.com (Recommended — Easiest)

Render reads the `render.yaml` blueprint in this repo and auto-configures
everything: Postgres database, web service, environment variables, and
auto-deploys on every `git push`.

### Step 1 — Push to GitHub
Your repo is already at: https://github.com/enohyn/vai-rad-kbb

### Step 2 — Create a Render account
1. Go to **https://render.com** → Sign up (use GitHub login for speed)
2. Verify your email

### Step 3 — Create a Blueprint deployment
1. Dashboard → **New +** → **Blueprint**
2. Select the `vai-rad-kbb` repository
3. Render detects `render.yaml` and shows:
   - A **PostgreSQL** database (`kanban-db`, free tier)
   - A **Web Service** (`vai-rad-kbb`, free tier)
4. Click **Apply**

### Step 4 — Wait for the build
Render will:
1. Install Python 3.12
2. Run `./build.sh` → `pip install`, `collectstatic`, `migrate`, `seed_demo_user`
3. Start `gunicorn config.wsgi:application`

This takes ~3–5 minutes. Watch the logs for "Build complete".

### Step 5 — Get your URL
Once live, your API will be at:
```
https://vai-rad-kbb.onrender.com/api/
```

### Step 6 — Update CORS for the frontend
After deploying the frontend (Vercel), come back to Render:
1. Dashboard → `vai-rad-kbb` web service → **Environment**
2. Edit `CORS_ALLOWED_ORIGINS` → add your Vercel URL:
   ```
   https://your-frontend.vercel.app
   ```
3. Save → Render auto-redeploys

### Step 7 — Test the API
```bash
# Login
curl -X POST https://vai-rad-kbb.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@kanban.test","password":"demoPass123!"}'

# Should return: {"access":"...","refresh":"..."}
```

### Render Free Tier Limits
| Limit | Detail |
|-------|--------|
| Cold starts | Service sleeps after 15 min idle (~30s wake-up) |
| Postgres | Free DB expires after 90 days |
| Build minutes | 750 hours/month (plenty) |
| Bandwidth | 100 GB/month |

✅ Perfectly fine for a demo.

---

## Option B: PythonAnywhere (Manual)

PythonAnywhere is great for Django and has a permanently free tier
(no cold starts for web apps, but limited CPU).

### Step 1 — Sign up
1. Go to **https://www.pythonanywhere.com/registration/signup/beginner/**
2. Create a free "Beginner" account
3. Your domain will be: `<username>.pythonanywhere.com`

### Step 2 — Clone the repo
Dashboard → **Consoles** → **Bash**:
```bash
git clone https://github.com/enohyn/vai-rad-kbb.git ~/backend
cd ~/backend
```

### Step 3 — Virtual environment + install
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 4 — Configure `.env`
```bash
cp .env.example .env
nano .env
```
Set these values:
```env
DEBUG=False
SECRET_KEY=RUN_PYTHON_BELOW_TO_GENERATE
ALLOWED_HOSTS=<username>.pythonanywhere.com
CORS_ALLOWED_ORIGINS=http://localhost:3000
DATABASE_URL=sqlite:///db.sqlite3
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Paste the output as `SECRET_KEY`.

### Step 5 — Migrate + seed + collect static
```bash
python manage.py migrate
python manage.py seed_demo_user
python manage.py collectstatic --noinput
```

### Step 6 — Create the Web App
1. Dashboard → **Web** tab → **Add a new web app**
2. Choose **Manual configuration** → **Python 3.12**
3. Set **Working directory** to: `/home/<username>/backend`

### Step 7 — Configure WSGI
Web tab → click the **WSGI configuration file** link. Replace the entire
contents with:
```python
import os
import sys

# Add the project to Python's path
path = '/home/<username>/backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Environment variables (or set these in the PythonAnywhere Environment tab)
os.environ['DEBUG'] = 'False'
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['ALLOWED_HOSTS'] = '<username>.pythonanywhere.com'
os.environ['CORS_ALLOWED_ORIGINS'] = 'http://localhost:3000'
os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
Save the file.

### Step 8 — Set the Virtualenv
Web tab → **Virtualenv** → enter:
```
/home/<username>/backend/.venv
```

### Step 9 — Static + Media file mappings
Web tab → **Static files** → add two entries:
| URL | Directory |
|-----|-----------|
| `/static/` | `/home/<username>/backend/staticfiles` |
| `/media/` | `/home/<username>/backend/media` |

### Step 10 — Reload and test
Click the green **Reload** button. Then:
```bash
curl -X POST https://<username>.pythonanywhere.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@kanban.test","password":"demoPass123!"}'
```

### PythonAnywhere Free Tier Limits
| Limit | Detail |
|-------|--------|
| CPU seconds | 100/day (plenty for demo) |
| Web apps | 1 on free tier |
| No always-on | Web app sleeps after ~3 months; console sessions expire |
| Storage | 512 MB |

---

## 🔑 Demo Credentials (for both options)
| Field | Value |
|-------|-------|
| Email | `demo@kanban.test` |
| Password | `demoPass123!` |

These are created by `python manage.py seed_demo_user` (or automatically on
Render via `build.sh`).

---

## 🔄 Re-deploying Updates

**Render:** Just `git push` to `master` — Render auto-detects and redeploys.

**PythonAnywhere:**
```bash
cd ~/backend
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
Then click **Reload** in the Web tab.

---

## 🐛 Common Deployment Issues

| Problem | Fix |
|---------|-----|
| `DisallowedHost` error | Add your domain to `ALLOWED_HOSTS` in `.env` |
| `CORS error` in browser | Add frontend URL to `CORS_ALLOWED_ORIGINS` |
| `collectstatic` fails | Ensure `whitenoise` is in `INSTALLED_APPS` middleware (it is) |
| `psycopg2` build error | Only needed on Render/Postgres; SQLite doesn't need it |
| Login returns 401 | Check that `SEED_EMAIL` / `SEED_PASSWORD` match `.env` |
| Static files 404 | Run `collectstatic` + configure static file mapping |