#!/usr/bin/env bash
set -o errexit

export PYTHONPATH=$PYTHONPATH:$(pwd)

pip install -r requirements.txt

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

#  créer dossier logs
mkdir -p logs

#  static
python manage.py collectstatic --noinput