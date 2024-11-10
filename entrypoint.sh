#!/bin/sh
# ./backend/entrypoint.sh

echo "Waiting for postgres..."
while ! nc -z db 5432; do
    sleep 0.1
done
echo "PostgreSQL started"

# Collect static files
python manage.py collectstatic --noinput

# Apply migrations
python manage.py migrate

# Start Gunicorn
exec gunicorn django_nt_solutions.wsgi:application --bind 0.0.0.0:8000 --workers 3