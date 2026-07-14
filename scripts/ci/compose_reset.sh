#!/usr/bin/env bash
# Tear down Compose project state and reclaim fixed container_name values from
# docker-compose.yml. Required on self-hosted runners that share Docker Desktop
# with a local desk stack (same host socket).
set -uo pipefail

docker compose down --volumes --remove-orphans || true

names=(
  aesthetic_os_postgres_db
  aesthetic_os_redis
  aesthetic_os_web_app
  aesthetic_os_nuxt_frontend
  aesthetic_os_nuxt_frontend_test
  aesthetic_os_celery_worker
  aesthetic_os_celery_beat
  aesthetic_os_receipt_notification_worker
  aesthetic_os_gallery_worker
)
for c in "${names[@]}"; do
  docker rm -f "$c" >/dev/null 2>&1 || true
done

docker network rm aesthetic_os_isolated_network >/dev/null 2>&1 || true
exit 0
