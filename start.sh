#!/usr/bin/env bash
set -o errexit

# Migrations au runtime
python manage.py migrate --noinput

# Création superuser automatique (optionnel)
if [ "$CREATE_SUPERUSER" = "true" ]; then
  python manage.py shell < scripts/create_superuser.py
fi

# Lancer serveur Django
gunicorn core.wsgi:application --bind 0.0.0.0:${PORT}
