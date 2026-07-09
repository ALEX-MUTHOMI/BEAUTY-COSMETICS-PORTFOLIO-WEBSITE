#!/usr/bin/env bash
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

docker run --rm --network host \
  -v "${COLLECTION}:/etc/newman/collection.json:ro" \
  -v "${ENVIRONMENT}:/etc/newman/environment.json:ro" \
  -v "${REPORT_DIR}:/etc/newman/reports:rw" \
  "${IMAGE}" run /etc/newman/collection.json \
  -e /etc/newman/environment.json \
  --bail \
  --reporters cli,json \
  --reporter-json-export /etc/newman/reports/newman-local.json

echo "NEWMAN_RESULT=passed"
