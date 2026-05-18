#!/usr/bin/env bash
set -o errexit

# Installer les dépendances
pip install -r requirements.txt

# Static files
python manage.py collectstatic --noinput
``