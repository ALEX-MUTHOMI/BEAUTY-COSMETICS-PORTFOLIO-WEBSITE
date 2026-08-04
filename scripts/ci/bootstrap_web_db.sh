#!/usr/bin/env bash
# Apply Django migrations against the live compose web DB before seeds / Newman.
# Pytest partitions use pytest-django's test DB; management commands do not.
set -euo pipefail

echo "BOOTSTRAP_WEB_DB=migrate"
docker compose exec -T web poetry run python manage.py migrate --noinput
echo "BOOTSTRAP_WEB_DB=passed"
