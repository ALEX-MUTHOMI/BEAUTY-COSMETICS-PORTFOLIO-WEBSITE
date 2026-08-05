#!/usr/bin/env bash
# Fail closed if the last successful full-fortress Secure Enterprise run is older
# than MAX_AGE_DAYS (default 7). Used before staging/production promote.
#
# A green push/PR (or workflow_dispatch without fortress) must NOT satisfy this
# gate — we require schedule, or a dispatch whose jobs include fortress-gate.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-${1:-}}"
MAX_AGE_DAYS="${FORTRESS_MAX_AGE_DAYS:-7}"
WORKFLOW_NAME="${FORTRESS_WORKFLOW_NAME:-Secure Enterprise CI Pipeline}"
FORTRESS_JOB_MARKER="${FORTRESS_JOB_MARKER:-fortress-gate}"

if [[ -z "${REPO}" ]]; then
  echo "GITHUB_REPOSITORY or repo arg required (owner/name)"
  exit 2
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required"
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
  echo "python is required"
  exit 2
fi

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

echo "[*] Looking for successful fortress runs on ${REPO} (max age ${MAX_AGE_DAYS}d)"

TMP="$(mktemp)"
trap 'rm -f "${TMP}"' EXIT

gh run list \
  --repo "${REPO}" \
  --workflow "${WORKFLOW_NAME}" \
  --status completed \
  --limit 50 \
  --json databaseId,conclusion,event,createdAt,displayTitle,url \
  >"${TMP}"

FORTRESS_MAX_AGE_DAYS="${MAX_AGE_DAYS}" \
FORTRESS_JOB_MARKER="${FORTRESS_JOB_MARKER}" \
REPO="${REPO}" \
"${PY}" - "${TMP}" <<'PY'
import json, os, subprocess, sys
from datetime import datetime, timezone, timedelta

path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
max_age = timedelta(days=int(os.environ.get("FORTRESS_MAX_AGE_DAYS", "7")))
marker = os.environ.get("FORTRESS_JOB_MARKER", "fortress-gate")
repo = os.environ["REPO"]
now = datetime.now(timezone.utc)
# Accept legacy cass-certification until schedules emit fortress-gate.
markers = [marker]
if marker == "fortress-gate" and "cass-certification" not in markers:
    markers.append("cass-certification")

def has_fortress_job(run_id: int) -> bool:
    raw = subprocess.check_output(
        [
            "gh",
            "run",
            "view",
            str(run_id),
            "--repo",
            repo,
            "--json",
            "jobs",
        ],
        text=True,
    )
    jobs = json.loads(raw).get("jobs") or []
    for job in jobs:
        name = (job.get("name") or "").lower()
        if job.get("conclusion") != "success":
            continue
        for m in markers:
            if m.lower() in name:
                return True
    return False

candidates = []
for run in data:
    if run.get("conclusion") != "success":
        continue
    event = run.get("event") or ""
    if event not in {"schedule", "workflow_dispatch"}:
        continue
    created = datetime.fromisoformat(run["createdAt"].replace("Z", "+00:00"))
    candidates.append((created, run))

candidates.sort(key=lambda row: row[0], reverse=True)

chosen = None
for created, run in candidates:
    run_id = run["databaseId"]
    event = run.get("event") or ""
    # Schedule always runs fortress. Dispatch must prove the marker job succeeded
    # (promo-only dispatch must not clear this gate).
    if event == "schedule" or (event == "workflow_dispatch" and has_fortress_job(run_id)):
        chosen = (created, run)
        break
    print(f"skip run {run_id} ({event}): no successful {'/'.join(markers)} job")

if chosen is None:
    print(
        "No successful fortress run found (schedule or dispatch with "
        f"{'/'.join(markers)}). Re-run Secure Enterprise with run_full_fortress=true.",
        file=sys.stderr,
    )
    sys.exit(1)

created, run = chosen
age = now - created
print(f"Latest fortress success: {run.get('url')} age={age}")
if age > max_age:
    print(
        f"Fortress freshness gate failed: last success is {age.days}d old "
        f"(limit {max_age.days}d). Re-run Secure Enterprise with run_full_fortress=true.",
        file=sys.stderr,
    )
    sys.exit(1)
print("fortress freshness OK")
PY
