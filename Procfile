# Procfile for Heroku / Render manual deploys.
# Render's blueprint (render.yaml) overrides this, but keeping a Procfile
# means the app can be deployed to any Heroku-compatible host too.
web: gunicorn config.wsgi:application --bind=0.0.0.0:${PORT:-8000} --workers=3
release: python manage.py migrate --noinput && python manage.py seed_demo_user || true