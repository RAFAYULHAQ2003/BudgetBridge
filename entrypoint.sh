#!/bin/sh
set -e

echo "Waiting for database to be ready..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  echo "Database not ready, sleeping 2s..."
  sleep 2
done

echo "Database ready. Running migrations..."
python manage.py migrate --noinput

exec "$@"