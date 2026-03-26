#!/usr/bin/env bash
set -o errexit

# Installer les dépendances
pip install -r requirements.txt

# Static files
python manage.py collectstatic --no-input

# Migrations
python manage.py migrate
python manage.py shell < scripts/create_superuser.py

# Création automatique du superuser (si activée)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creating Django superuser..."

    python manage.py createsuperuser --no-input || \
    echo "Superuser already exists, skipping."
fi
``