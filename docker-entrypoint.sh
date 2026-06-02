#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py ensure_bootstrap_superuser
python manage.py collectstatic --noinput
exec "$@"
