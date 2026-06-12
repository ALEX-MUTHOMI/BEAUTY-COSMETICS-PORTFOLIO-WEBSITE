# ZAP Baseline Local Runbook

This runbook is for passive local ZAP baseline scanning only. It must not be
used for active scanning, brute force, destructive payloads, or real provider
traffic.

## Scope

Allowed target:

```text
http://host.docker.internal:8000
```

Allowed scan type:

```text
zap-baseline.py passive baseline
```

Disallowed:

```text
zap-full-scan.py
active scan
real Daraja calls
real email provider calls
real R2/Cloudflare calls
production data
```

## Local Scan Profile

Use `docker-compose.security-scan.yml` for local scanner runs. It disables the
local HTTP-to-HTTPS redirect and allows `host.docker.internal` so Dockerized
ZAP can reach Django. This override is not a production or staging profile.

The application still uses fake payment and notification providers in this
profile.

## Commands

Start the local scan profile:

```powershell
docker compose -f docker-compose.yml -f docker-compose.security-scan.yml up -d web worker
```

Verify the safe target:

```powershell
curl.exe -i http://localhost:8000/health/
curl.exe -i http://localhost:8000/api/health-check/
docker compose exec worker sh -lc "celery -A core inspect ping -d celery@`$HOSTNAME --timeout=10 | grep -q OK; echo exit=`$?"
```

Run ZAP baseline:

```powershell
.\scripts\security\zap_baseline_local.ps1
```

Expected artifact paths:

```text
reports/security/zap/zap-baseline.html
reports/security/zap/zap-baseline.md
reports/security/zap/zap-baseline.json
```

Generated ZAP reports are ignored by Git. Commit only the runbook, config, and
triage notes.

## Exit Codes

ZAP can return a non-zero exit when it finds warnings. Treat non-zero as a
triage signal, not as proof that artifacts are missing. Verify the report files
before declaring the scan blocked.

## Post-Scan Checks

After ZAP completes, run the normal regression gates:

```powershell
docker compose exec web poetry run python manage.py check
docker compose exec web poetry run python manage.py makemigrations --check --dry-run
docker compose exec web poetry run pytest --collect-only -q
docker compose exec web poetry run pytest tests/api tests/security -q
newman.cmd run tests\postman\beauty_backend_acceptance.postman_collection.json -e tests\postman\local-docker.postman_environment.json --bail --reporters cli,json --reporter-json-export tests\postman\reports\newman-local.json
```

Do not claim Phase 3A readiness unless the scan artifacts exist and the
post-scan checks pass or any blocker is explicitly reported.
