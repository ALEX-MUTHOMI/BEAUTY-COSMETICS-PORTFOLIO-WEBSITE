# ZAP Baseline Triage

## Command

```powershell
.\scripts\security\zap_baseline_local.ps1 -Target http://host.docker.internal:8000/health/ -SpiderMinutes 1 -MaxMinutes 6
```

## Target

`http://host.docker.internal:8000/health/`

This target maps to the owned local Docker backend exposed on localhost through
the local-only `docker-compose.security-scan.yml` override. The override keeps
providers fake and disables only the local HTTP-to-HTTPS redirect so ZAP can
scan the Django development deployment over HTTP.

## Result

- Scan date: 2026-06-12.
- ZAP exit code: 2.
- Result: completed with warning findings.
- Report artifacts:
  - `reports/security/zap/zap-baseline.html`
  - `reports/security/zap/zap-baseline.md`
  - `reports/security/zap/zap-baseline.json`
- Generated reports are ignored by Git; commit only triage and runbook files.

## Findings Table

| Rule ID | Alert | Risk | Instances | Triage |
| --- | --- | --- | ---: | --- |
| 10038 | Content Security Policy (CSP) Header Not Set | Medium | 3 | Open. Findings are on 404 responses for `/`, `/robots.txt`, and `/sitemap.xml`. Add global CSP middleware/headers for error responses before production exposure. |
| 90004 | Cross-Origin-Resource-Policy Header Missing or Invalid | Low | 1 | Open. `/health/` should include an explicit safe CORP header or be covered by global security headers. |
| 10063 | Permissions Policy Header Not Set | Low | 3 | Open. Findings are on 404 responses for `/`, `/robots.txt`, and `/sitemap.xml`. Add global Permissions-Policy for normal and error responses. |
| 10049 | Storable and Cacheable Content | Informational | 5 | Open. Health/error responses should be explicitly non-cacheable where appropriate. |

## Execution Notes

- Docker health was green before the scan.
- `/health/` and `/api/health-check/` returned HTTP 200 under the scan profile.
- Worker ping returned `exit=0` before the scan.
- No active scan was run.
- No real Daraja, email provider, or storage provider traffic was used.

## Follow-Up Recommendation

The ZAP tooling blocker is resolved. The remaining items are application header
hardening findings:

- Add global CSP and Permissions-Policy headers for normal and error responses.
- Add explicit no-store/no-cache behavior for health and security-sensitive API
  responses.
- Add CORP/COOP policy decisions to the security-header inventory.

Do not run ZAP full scan or active scan until explicitly approved in a later
phase.
