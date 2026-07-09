#!/usr/bin/env bash
# Create Toxiproxy listen→upstream proxies for Postgres and Redis chaos tests.
set -euo pipefail

ADMIN_URL="${TOXIPROXY_ADMIN_URL:-http://127.0.0.1:8474}"
max_attempts="${1:-30}"

for _ in $(seq 1 "$max_attempts"); do
  if curl -fsS "${ADMIN_URL}/version" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

curl -fsS "${ADMIN_URL}/version" >/dev/null

# Idempotent: delete then recreate so CI re-runs are clean.
curl -fsS -X DELETE "${ADMIN_URL}/proxies/postgres" >/dev/null 2>&1 || true
curl -fsS -X DELETE "${ADMIN_URL}/proxies/redis" >/dev/null 2>&1 || true

curl -fsS -X POST "${ADMIN_URL}/proxies" \
  -H 'Content-Type: application/json' \
  -d '{"name":"postgres","listen":"0.0.0.0:54320","upstream":"db:5432","enabled":true}' >/dev/null

curl -fsS -X POST "${ADMIN_URL}/proxies" \
  -H 'Content-Type: application/json' \
  -d '{"name":"redis","listen":"0.0.0.0:63790","upstream":"redis:6379","enabled":true}' >/dev/null

echo "TOXIPROXY_PROXIES=passed"
