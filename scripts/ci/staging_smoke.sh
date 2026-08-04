#!/usr/bin/env bash
# Staging / promote smoke — fail-closed readiness + book deep-link reachability.
set -euo pipefail

BASE_URL="${STAGING_BASE_URL:-${1:-}}"
if [[ -z "${BASE_URL}" ]]; then
  echo "STAGING_BASE_URL is required (e.g. https://staging.example.com or http://127.0.0.1:8000)"
  exit 2
fi

BASE_URL="${BASE_URL%/}"
echo "[*] Smoke against ${BASE_URL}"

curl -fsS --max-time 20 "${BASE_URL}/api/health-check/" | tee /tmp/health-check.json

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

"${PY}" - <<'PY'
import json, sys

payload = json.load(open("/tmp/health-check.json", encoding="utf-8"))
text = json.dumps(payload).lower()
# Fail if response body looks like credential leakage.
if "consumer_secret" in text or "passkey" in text:
    print("health payload looks like it may contain secrets", file=sys.stderr)
    sys.exit(1)

status = str(payload.get("status") or "").lower()
if status != "ok":
    print(f"health-check status not ok: {payload!r}", file=sys.stderr)
    sys.exit(1)

checks = payload.get("checks")
if isinstance(checks, dict):
    bad = {k: v for k, v in checks.items() if str(v).lower() != "ok"}
    if bad:
        print(f"health-check dependency failures: {bad}", file=sys.stderr)
        sys.exit(1)

print("health-check OK")
PY

# Book deep-link surfaces (frontend or API edge). Accept 200/3xx.
for path in "/book" "/services" "/"; do
  code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 20 "${BASE_URL}${path}" || true)"
  echo "[*] GET ${path} -> ${code}"
  case "${code}" in
    200|301|302|303|304|307|308) ;;
    *)
      echo "book/deep-link smoke failed for ${path} (HTTP ${code})"
      exit 1
      ;;
  esac
done

echo "[+] staging smoke passed"
