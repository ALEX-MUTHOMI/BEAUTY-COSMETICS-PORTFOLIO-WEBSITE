#!/usr/bin/env bash
# Bounded retry for NON-DETERMINISTIC (network) steps only — dependency installs,
# image pulls, browser downloads. This is the durable-retry idea from Cloudflare
# Workflows applied to GitHub Actions shell steps.
#
# NEVER wrap test assertions with this: a test that only passes on retry is a
# hidden bug, not a flake to paper over.
#
# Usage: with_retry.sh <attempts> <sleep_seconds> -- <command...>
set -uo pipefail

attempts="${1:?attempts required}"; shift
sleep_s="${1:?sleep seconds required}"; shift
if [ "${1:-}" = "--" ]; then shift; fi

if [ "$#" -eq 0 ]; then
  echo "usage: with_retry.sh <attempts> <sleep_seconds> -- <command...>" >&2
  exit 2
fi

n=1
until "$@"; do
  rc=$?
  if [ "${n}" -ge "${attempts}" ]; then
    echo "::error::command failed after ${attempts} attempts (rc=${rc}): $*"
    exit "${rc}"
  fi
  echo "::warning::attempt ${n}/${attempts} failed (rc=${rc}); retrying in ${sleep_s}s: $*"
  n=$((n + 1))
  sleep "${sleep_s}"
done
