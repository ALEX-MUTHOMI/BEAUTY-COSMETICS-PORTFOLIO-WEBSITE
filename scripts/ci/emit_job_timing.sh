#!/usr/bin/env bash
# Emit a per-job wall-time line into the GitHub Actions run summary — the
# lightweight analog of Cloudflare Workflows' per-step timing. Pair it with an
# early `echo "JOB_START=$(date +%s)" >> "$GITHUB_ENV"` step in the same job.
#
# Usage: emit_job_timing.sh <job-label>
set -uo pipefail

label="${1:-job}"
start="${JOB_START:-}"
now="$(date +%s)"
out="${GITHUB_STEP_SUMMARY:-/dev/stdout}"

if [ -n "${start}" ]; then
  elapsed=$(( now - start ))
  printf '### %s wall-time: %dm %02ds\n' "${label}" "$(( elapsed / 60 ))" "$(( elapsed % 60 ))" >> "${out}"
else
  printf '### %s wall-time: (no JOB_START recorded)\n' "${label}" >> "${out}"
fi
