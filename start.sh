#!/usr/bin/env bash
set -o errexit

cd backend

# Migrations au démarrage (runtime)
python manage.py migrate --noinput

# Création superuser uniquement si activée
if [ "$CREATE_SUPERUSER" = "true" ]; then
  python manage.py shell < scripts/create_superuser.py
fi

# Lancer le serveur (WSGI)
gunicorn core.wsgi:application --bind 0.0.0.0:${PORT}