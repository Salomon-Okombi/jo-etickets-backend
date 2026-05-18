#!/usr/bin/env bash
set -o errexit

# Aller dans le dossier Django (si ton manage.py est dans backend/)
cd backend

# Installer les dépendances
pip install -r requirements.txt

# Static files
python manage.py collectstatic --noinput