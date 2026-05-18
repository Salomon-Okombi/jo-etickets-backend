#!/usr/bin/env bash
set -o errexit

export PYTHONPATH=$PYTHONPATH:$(pwd)

echo " Running migrations..."
python manage.py migrate --noinput

echo " Starting server..."
gunicorn core.wsgi:application --bind 0.0.0.0:${PORT}
