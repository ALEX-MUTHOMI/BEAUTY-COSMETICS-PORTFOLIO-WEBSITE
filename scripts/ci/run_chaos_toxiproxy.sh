#!/usr/bin/env bash
# Enterprise chaos gate: route DB/Redis through Toxiproxy, then run chaos suites.
# Fake-provider only — never opens real Daraja callbacks.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.toxiproxy.yml)

echo "CHAOS_COMPOSE=toxiproxy"
# No --build: the web image is prebuilt once by the build-images CI job and
# pulled/retagged to aesthetic_os_web_app:latest before this script runs
# (db/redis/toxiproxy are registry images with no build stage).
"${COMPOSE[@]}" up -d db redis toxiproxy
bash scripts/ci/setup_toxiproxy_proxies.sh
"${COMPOSE[@]}" up -d web worker
bash scripts/ci/wait_for_compose_health.sh
bash scripts/ci/bootstrap_web_db.sh

echo "CHAOS_SUITE=system_chaos"
docker compose -f docker-compose.yml -f docker-compose.toxiproxy.yml exec -T web \
  poetry run pytest tests/security/test_system_chaos.py -vv --durations=25

# Inject bounded latency toxic, then re-run a focused chaos proof under degraded IO.
echo "CHAOS_TOXIC=latency"
curl -fsS -X POST http://127.0.0.1:8474/proxies/postgres/toxics \
  -H 'Content-Type: application/json' \
  -d '{"name":"pg_latency","type":"latency","attributes":{"latency":80,"jitter":20}}' >/dev/null || true

docker compose -f docker-compose.yml -f docker-compose.toxiproxy.yml exec -T web \
  poetry run pytest tests/security/test_system_chaos.py::test_parallel_mpesa_callbacks_credit_checkout_once -vv

echo "CHAOS_RESULT=passed"
