#!/bin/sh
set -e

echo "Iniciando worker Celery..."
exec celery -A core worker -l info