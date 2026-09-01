#!/usr/bin/env bash
# Best-effort deletion of the run-scoped ':ci-<sha>' GHCR images pushed by
# build_ci_images.sh, so per-commit CI tags don't accumulate in the registry.
#
# Non-fatal by design: GHCR version deletion for user-owned packages can be
# denied to GITHUB_TOKEN. Failures are warnings; a scheduled retention policy is
# the reliable backstop (see docs/ops/CI_WORKFLOW_DESIGN.md).
set -uo pipefail

OWNER="$(echo "${GITHUB_REPOSITORY_OWNER:?}" | tr '[:upper:]' '[:lower:]')"
REPO="${GITHUB_REPOSITORY##*/}"
SHA="${GITHUB_SHA:?}"
TAG="ci-${SHA}"

images=(aesthetic_os_web_app aesthetic_os_nuxt_frontend aesthetic_os_nuxt_frontend_test)

for image in "${images[@]}"; do
  pkg="${REPO}/${image}"
  enc="${pkg//\//%2F}"
  echo "== cleanup ${pkg}:${TAG} =="

  vid="$(gh api "/users/${OWNER}/packages/container/${enc}/versions" \
      --jq ".[] | select(.metadata.container.tags[]? == \"${TAG}\") | .id" 2>/dev/null | head -n1 || true)"

  if [ -z "${vid}" ]; then
    echo "::warning::no version found for ${pkg}:${TAG} (already gone or API denied)"
    continue
  fi

  if gh api -X DELETE "/users/${OWNER}/packages/container/${enc}/versions/${vid}" >/dev/null 2>&1; then
    echo "deleted ${pkg} version ${vid} (${TAG})"
  else
    echo "::warning::could not delete ${pkg} version ${vid} (${TAG}) — non-fatal"
  fi
done
exit 0
