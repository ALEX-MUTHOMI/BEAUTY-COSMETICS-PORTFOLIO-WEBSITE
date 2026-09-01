#!/usr/bin/env bash
# Build the three CI images ONCE per commit and push run-scoped tags to GHCR.
#
# Cloudflare's CI post calls this "install once, cache, reuse": the expensive,
# deterministic build is paid for a single time, then every downstream job pulls
# it (see pull_ci_images.sh) instead of running `docker compose up --build`. That
# turns ~13 cold image builds per pipeline into one.
#
# Only a run-scoped ':ci-<sha>' tag is pushed (one tag == one version), so the
# end-of-run cleanup can delete it safely without touching any shared cache tag.
# Cross-run BuildKit layer caching is a deliberate future optimization (would
# need a registry/gha cache backend); the build-once-per-run win needs none.
set -euo pipefail

OWNER="$(echo "${GITHUB_REPOSITORY_OWNER:?}" | tr '[:upper:]' '[:lower:]')"
REPO="$(echo "${GITHUB_REPOSITORY##*/}" | tr '[:upper:]' '[:lower:]')"
SHA="${GITHUB_SHA:?}"
REG="ghcr.io/${OWNER}/${REPO}"

export DOCKER_BUILDKIT=1

build_push() {
  local name="$1" ctx="$2" target="${3:-}" install_dev="${4:-}"
  local img="${REG}/${name}"

  local args=(build -t "${img}:ci-${SHA}")
  [ -n "${target}" ] && args+=(--target "${target}")
  [ -n "${install_dev}" ] && args+=(--build-arg "INSTALL_DEV=${install_dev}")
  args+=(-f "${ctx}/Dockerfile" "${ctx}")

  echo "== build ${img}:ci-${SHA} (target='${target:-default}' install_dev='${install_dev:-default}') =="
  docker "${args[@]}"
  docker push "${img}:ci-${SHA}"
}

# Backend CI image (dev deps for pytest). One build serves web/worker/beat/*-worker.
build_push "aesthetic_os_web_app" "." "" "true"
# Nuxt SSR production image (default 'runner' stage) — used by frontend/edge/e2e.
build_push "aesthetic_os_nuxt_frontend" "./frontend" "" ""
# Nuxt 'builder' stage (node_modules + source) — used by frontend-test lint/unit/type/build.
build_push "aesthetic_os_nuxt_frontend_test" "./frontend" "builder" ""

echo "build-images: pushed ci-${SHA} tags for web, frontend, frontend-test"
