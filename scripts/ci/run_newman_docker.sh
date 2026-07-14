#!/usr/bin/env bash
# Run Newman against the live Compose stack.
#
# Do NOT bind-mount checkout paths into the Newman container when CI runs on a
# socket-mounted self-hosted runner: the host Docker daemon cannot see those
# paths and creates empty directories (Newman then fails with EISDIR).
# docker cp works from the runner filesystem into the ephemeral container.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COLLECTION="${ROOT}/tests/postman/aesthetic_os_backend_acceptance.postman_collection.json"
ENVIRONMENT="${ROOT}/tests/postman/local-docker.postman_environment.json"
REPORT_DIR="${ROOT}/reports/ci/newman"
REPORT_FILE="${REPORT_DIR}/newman-local.json"
IMAGE="${NEWMAN_IMAGE:-postman/newman:6.1.3}"

mkdir -p "$REPORT_DIR"

echo "NEWMAN_RUNNER=docker"
echo "NEWMAN_IMAGE=${IMAGE}"
echo "NEWMAN_COLLECTION=${COLLECTION}"
echo "NEWMAN_ENVIRONMENT=${ENVIRONMENT}"
echo "NEWMAN_REPORT=${REPORT_FILE}"

# Live gunicorn DB is empty until migrate — seeds fail hard without this.
bash "${ROOT}/scripts/ci/bootstrap_web_db.sh"
docker compose exec -T web poetry run python manage.py seed_api_acceptance_data
docker compose exec -T web poetry run python manage.py seed_marketing_catalog

cid="$(
  docker create --network host --entrypoint sh "${IMAGE}" -c \
    'mkdir -p /etc/newman/reports && \
     newman run /etc/newman/collection.json \
       -e /etc/newman/environment.json \
       --bail \
       --reporters cli,json \
       --reporter-json-export /etc/newman/reports/newman-local.json'
)"

cleanup() { docker rm -f "${cid}" >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker cp "${COLLECTION}" "${cid}:/etc/newman/collection.json"
docker cp "${ENVIRONMENT}" "${cid}:/etc/newman/environment.json"

docker start -a "${cid}"
docker cp "${cid}:/etc/newman/reports/newman-local.json" "${REPORT_FILE}"

echo "NEWMAN_RESULT=passed"
