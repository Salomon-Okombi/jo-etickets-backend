#!/usr/bin/env bash
set -o errexit

echo " Migration DB..."
python manage.py migrate --noinput

echo " Création admin..."
python manage.py createadmin || true

echo " Collect static..."
python manage.py collectstatic --noinput

echo " Démarrage serveur..."
gunicorn core.wsgi:application --bind 0.0.0.0:${PORT}