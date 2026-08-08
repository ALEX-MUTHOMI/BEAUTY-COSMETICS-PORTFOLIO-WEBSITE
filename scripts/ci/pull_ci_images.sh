#!/usr/bin/env bash
# Pull the run-scoped CI images built by build_ci_images.sh and retag them to
# the local ':latest' tags docker-compose.yml expects. After this, running
# `docker compose up -d` WITHOUT --build reuses the prebuilt image instead of
# rebuilding it (Compose only builds when the image is absent locally).
#
# Args: one or more of  web | frontend | frontend-test
set -euo pipefail

OWNER="$(echo "${GITHUB_REPOSITORY_OWNER:?}" | tr '[:upper:]' '[:lower:]')"
REPO="$(echo "${GITHUB_REPOSITORY##*/}" | tr '[:upper:]' '[:lower:]')"
SHA="${GITHUB_SHA:?}"
REG="ghcr.io/${OWNER}/${REPO}"

if [ "$#" -eq 0 ]; then
  echo "usage: pull_ci_images.sh <web|frontend|frontend-test> [more...]" >&2
  exit 2
fi

pull_tag() {
  local remote="$1" local_tag="$2"
  echo "== pull ${remote} -> ${local_tag} =="
  docker pull "${remote}"
  docker tag "${remote}" "${local_tag}"
}

for key in "$@"; do
  case "${key}" in
    web)
      pull_tag "${REG}/aesthetic_os_web_app:ci-${SHA}" "aesthetic_os_web_app:latest" ;;
    frontend)
      pull_tag "${REG}/aesthetic_os_nuxt_frontend:ci-${SHA}" "aesthetic_os_nuxt_frontend:latest" ;;
    frontend-test)
      pull_tag "${REG}/aesthetic_os_nuxt_frontend_test:ci-${SHA}" "aesthetic_os_nuxt_frontend_test:latest" ;;
    *)
      echo "::error::unknown image key '${key}' (want web|frontend|frontend-test)"; exit 1 ;;
  esac
done
