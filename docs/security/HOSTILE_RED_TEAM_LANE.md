# Hostile Red Team lane (Staff Portal + Guest Money Path)

Artifacts live under `tests/security/`, `tests/postman/`, and `scripts/security/`.
Local active `zap-full-scan` against localhost remains **forbidden** (see `ZAP_BASELINE_RUNBOOK.md`).

## 1. pytest (turbo_pass / tests/security)

```powershell
docker compose exec -T web poetry run pytest tests/security/test_staff_portal_owasp_red_team.py -q
```

Included automatically when turbo_pass runs `pytest tests/security`.

## 2. Hostile Newman

```powershell
.\scripts\ci\run_newman_hostile_docker.ps1
```

Collection: `tests/postman/aesthetic_os_hostile_red_team.postman_collection.json`

## 3. ZAP authenticated passive (local)

```powershell
# After staff login, copy sessionid + csrftoken from browser DevTools
.\scripts\security\zap_staff_authenticated_passive.ps1 -SessionId '<sessionid>' -CsrfToken '<csrftoken>'
```

Context template: `scripts/security/zap_staff_authenticated_context.json`

## 4. ZAP staging active (gated)

```powershell
$env:CONFIRM_ACTIVE_ZAP='1'
.\scripts\security\zap_staging_active_scan.ps1 -Target 'https://YOUR-STAGING-HOST'
```

Refuses localhost and hostnames that look like production without `staging` in the name.
