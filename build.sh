#!/usr/bin/env bash
set -o errexit

export PYTHONPATH=$PYTHONPATH:$(pwd)

pip install -r requirements.txt

# ✅ créer dossier logs
mkdir -p logs

# ✅ static
python manage.py collectstatic --noinput