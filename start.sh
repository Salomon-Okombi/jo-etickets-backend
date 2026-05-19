#!/usr/bin/env bash
set -o errexit

echo "  Démarrage backend..."

echo "  Migration DB..."
python manage.py migrate --noinput

echo "  Collect static..."
python manage.py collectstatic --noinput

echo "  Lancement Gunicorn..."
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers=2 --timeout 60