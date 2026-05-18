#!/usr/bin/env bash
set -o errexit

# IMPORTANT : ajoute ça
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Installer les dépendances
pip install -r requirements.txt

# Static
python manage.py collectstatic --noinput