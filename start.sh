#!/usr/bin/env bash
set -o errexit

python manage.py migrate --noinput

if [ "$CREATE_SUPERUSER" = "true" ]; then
  python manage.py