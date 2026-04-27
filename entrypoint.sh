#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "Database not ready yet, retrying in 2s..."
  sleep 2
done

echo "Running migrations..."
python -m alembic upgrade head

echo "Starting server..."
exec "$@"
