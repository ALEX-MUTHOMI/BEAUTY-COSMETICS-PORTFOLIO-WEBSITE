#!/usr/bin/env bash
# Run a pytest partition inside the web container and emit a host-side JUnit report.
# The web image runs as non-root django-user (uid 10001). Host-created report dirs
# are not writable by that user, so JUnit is written under /app/var (owned by
# django-user) and copied out for GitHub Actions artifacts.
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <junit-basename.xml> <pytest-args...>" >&2
  exit 2
fi

JUNIT_NAME="$1"
shift

HOST_JUNIT_DIR="reports/ci/junit"
CONTAINER_JUNIT_DIR="/app/var/pytest-cache/junit"
CONTAINER_JUNIT_PATH="${CONTAINER_JUNIT_DIR}/${JUNIT_NAME}"
HOST_JUNIT_PATH="${HOST_JUNIT_DIR}/${JUNIT_NAME}"

mkdir -p "${HOST_JUNIT_DIR}"

docker compose exec -T web sh -c \
  "mkdir -p '${CONTAINER_JUNIT_DIR}' && poetry run pytest $* --junitxml='${CONTAINER_JUNIT_PATH}' -q --durations=25"

docker compose cp "web:${CONTAINER_JUNIT_PATH}" "${HOST_JUNIT_PATH}"
