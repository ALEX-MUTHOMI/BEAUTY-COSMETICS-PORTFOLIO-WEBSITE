#!/usr/bin/env bash
set -euo pipefail

max_attempts="${1:-30}"
sleep_seconds="${2:-5}"

for _ in $(seq 1 "$max_attempts"); do
  web_status="$(docker inspect --format='{{.State.Health.Status}}' aesthetic_os_web_app 2>/dev/null || echo starting)"
  db_status="$(docker inspect --format='{{.State.Health.Status}}' aesthetic_os_postgres_db 2>/dev/null || echo starting)"
  redis_status="$(docker inspect --format='{{.State.Health.Status}}' aesthetic_os_redis 2>/dev/null || echo starting)"
  if [[ "$web_status" == "healthy" && "$db_status" == "healthy" && "$redis_status" == "healthy" ]]; then
    echo "COMPOSE_HEALTH=passed"
    exit 0
  fi
  sleep "$sleep_seconds"
done

docker compose ps || true
echo "COMPOSE_HEALTH=failed"
exit 1
