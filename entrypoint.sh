#!/bin/sh
# entrypoint.sh
set -e

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 core.wsgi:application