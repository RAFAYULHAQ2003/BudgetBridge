#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
/usr/local/bin/wait-for-it.sh db:5432 --timeout=30

# Run migrations only on the server container
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running migrations..."
    python manage.py migrate
fi

# Start server or Celery depending on arguments
if [ $# -gt 0 ]; then
    exec "$@"
fi