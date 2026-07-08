#!/usr/bin/env bash
# Render.com build script — runs during the "build" phase.
# Exit on any error.
set -euo pipefail

echo "=== Installing dependencies ==="
pip install -r requirements/prod.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Seeding demo user ==="
python manage.py seed_demo_user || echo "Demo user already exists, skipping."

echo "=== Build complete ==="