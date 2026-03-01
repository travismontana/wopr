#!/bin/sh
# app/back_of_house/entrypoint.sh

set -e

echo "Waiting for postgres..."
while ! nc -z ${DB_HOST:-localhost} ${DB_PORT:-5432}; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear  # ADD --clear to force refresh

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 4 back_of_house.wsgi:application