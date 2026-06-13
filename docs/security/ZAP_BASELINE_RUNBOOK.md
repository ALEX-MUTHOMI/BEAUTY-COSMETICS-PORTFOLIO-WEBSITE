# ZAP Baseline Local Runbook

This runbook is for local passive ZAP coverage only. It must not be used for
active scanning, brute force, destructive payloads, real provider traffic, or
production scanning.

## Local Scan Profile

Use `docker-compose.security-scan.yml` for local scans:

```powershell
docker compose -f docker-compose.yml -f docker-compose.security-scan.yml up -d web worker
```

The override is local-only. It disables the local HTTP-to-HTTPS redirect so
Dockerized scanners can reach Django over HTTP and keeps payment/email providers
fake.

## Safety Rules

Allowed local targets:

```text
http://localhost:8000
http://127.0.0.1:8000
http://host.docker.internal:8000
```

Forbidden:

```text
zap-full-scan.py
active scan
Burp
production or third-party targets
real Daraja calls
real email provider calls
real R2/Cloudflare calls
production secrets or production data
```

## Scan Modes

### Health Baseline

Purpose: scanner and target health.

```powershell
.\scripts\security\zap_baseline_local.ps1 -Mode health -SpiderMinutes 1 -MaxMinutes 6
```

Artifacts:

```text
reports/security/zap/health/zap-health-baseline.html
reports/security/zap/health/zap-health-baseline.md
reports/security/zap/health/zap-health-baseline.json
```

### Root Baseline

Purpose: root/error/robots/sitemap/header behavior.

```powershell
.\scripts\security\zap_baseline_local.ps1 -Mode root -SpiderMinutes 2 -MaxMinutes 8
```

Artifacts:

```text
reports/security/zap/root/zap-root-baseline.html
reports/security/zap/root/zap-root-baseline.md
reports/security/zap/root/zap-root-baseline.json
```

### API Schema Baseline

Purpose: OpenAPI route coverage if a schema endpoint exists.

```powershell
.\scripts\security\zap_baseline_local.ps1 -Mode api -MaxMinutes 10
```

Current status: deferred because no local OpenAPI schema endpoint is configured.
Do not invent schema coverage in reports until a schema exists.

### Newman Through ZAP Passive Proxy

Purpose: let ZAP passively observe API workflows that spidering cannot discover:
CSRF, public catalog, booking hold, booking checkout, fake webhook, staff login,
staff session routes, public gallery, and negative security cases.

```powershell
.\scripts\security\zap_baseline_local.ps1 -Mode newman -MaxMinutes 15
```

Artifacts:

```text
reports/security/zap/newman/zap-newman-passive.html
reports/security/zap/newman/zap-newman-passive.md
reports/security/zap/newman/zap-newman-passive.json
reports/security/zap/newman/zap-newman-passive.urls.json
```

The script runs a temporary local ZAP daemon and Docker Newman through the ZAP
proxy using fake providers only. It must not be pointed at production.

## Exit Code Handling

The script prints the underlying ZAP exit code.

```text
0 = completed with no warnings
1 = completed with FAIL findings
2 = completed with warnings
3 = scanner/system failure
```

By default, exit code `2` is treated as completed-with-warnings so artifact
triage can continue. Use `-StrictExitCodes` if a CI job should fail on warnings.

## Report Hygiene

Generated ZAP reports are ignored by Git. Commit `.gitkeep` files, scripts, and
sanitized triage documents only.

Run this after generating artifacts:

```powershell
python .\scripts\security\zap_summarize_reports.py --file .\reports\security\zap\newman\zap-newman-passive.json --urls-file .\reports\security\zap\newman\zap-newman-passive.urls.json
```

Do not paste cookies, tokens, provider payloads, receipt IDs, checkout IDs,
ledger IDs, or storage keys into reports.

## Post-Scan Checks

After passive scans:

```powershell
docker compose ps
docker compose exec worker sh -lc "celery -A core inspect ping -d celery@`$HOSTNAME --timeout=10 | grep -q OK; echo exit=`$?"
docker compose exec web poetry run python manage.py check
docker compose exec web poetry run python manage.py makemigrations --check --dry-run
docker compose exec web poetry run pytest --collect-only -q
docker compose exec web poetry run pytest tests/api tests/security -q
newman.cmd run tests\postman\beauty_backend_acceptance.postman_collection.json -e tests\postman\local-docker.postman_environment.json --bail
```

If host Newman is unavailable, use Docker Newman and document the fallback.

Restore the default profile when finished:

```powershell
docker compose up -d web worker
```
