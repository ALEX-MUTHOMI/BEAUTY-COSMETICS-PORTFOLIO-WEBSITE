# ZAP Baseline Triage

## Scope

All scans in this file are local passive ZAP scans against the owned Docker
backend. No active scan, full scan, Burp, real provider traffic, production data,
or production target was used.

## Health Baseline

Command:

```powershell
.\scripts\security\zap_baseline_local.ps1 -Mode health -SpiderMinutes 1 -MaxMinutes 6
```

Target: `http://host.docker.internal:8000/health/`

Result:

- ZAP exit code: 2.
- Artifacts:
  - `reports/security/zap/health/zap-health-baseline.html`
  - `reports/security/zap/health/zap-health-baseline.md`
  - `reports/security/zap/health/zap-health-baseline.json`
- Observed URL count: 5.
- Alerts: 4.

Findings:

| Rule ID | Alert | Risk | Instances | Triage |
| --- | --- | --- | ---: | --- |
| 10038 | Content Security Policy Header Not Set | Medium | 3 | True positive/header gap on local root/error routes reached by health scan. Patch in security-header phase. |
| 90004 | Cross-Origin-Resource-Policy Header Missing or Invalid | Low | 1 | True positive/header policy gap on `/health/`. Patch in security-header phase. |
| 10063 | Permissions Policy Header Not Set | Low | 3 | True positive/header gap on root/error routes. Patch in security-header phase. |
| 10049 | Storable and Cacheable Content | Informational | 5 | Needs review. Health and error responses should have explicit cache policy. |

## Root Baseline

Command:

```powershell
.\scripts\security\zap_baseline_local.ps1 -Mode root -SpiderMinutes 2 -MaxMinutes 8
```

Target: `http://host.docker.internal:8000/`

Result:

- ZAP exit code: 2.
- Artifacts:
  - `reports/security/zap/root/zap-root-baseline.html`
  - `reports/security/zap/root/zap-root-baseline.md`
  - `reports/security/zap/root/zap-root-baseline.json`
- Observed URL count: 3.
- Alerts: 3.

Findings:

| Rule ID | Alert | Risk | Instances | Triage |
| --- | --- | --- | ---: | --- |
| 10038 | Content Security Policy Header Not Set | Medium | 2 | True positive on 404/root behavior. Add global CSP on normal and error responses. |
| 10063 | Permissions Policy Header Not Set | Low | 3 | True positive on 404/root behavior. Add global Permissions-Policy. |
| 10049 | Storable and Cacheable Content | Informational | 3 | Needs review. Add explicit cache policy for error responses. |

## API Schema Baseline

Command:

```powershell
.\scripts\security\zap_baseline_local.ps1 -Mode api -MaxMinutes 10
```

Result:

- Deferred.
- Reason: no reachable local OpenAPI schema endpoint.
- Checked candidates:
  - `/api/schema/`
  - `/api/schema/?format=json`
  - `/api/docs/`
  - `/schema/`
  - `/openapi.json`
- Static search found no `drf-spectacular`, `SpectacularAPIView`, Swagger,
  Redoc, or OpenAPI wiring.

No API schema ZAP coverage is claimed.

## Newman Through ZAP Passive Proxy

Command:

```powershell
.\scripts\security\zap_baseline_local.ps1 -Mode newman -MaxMinutes 15
```

Result:

- Newman exit code: 0.
- Artifacts:
  - `reports/security/zap/newman/zap-newman-passive.html`
  - `reports/security/zap/newman/zap-newman-passive.md`
  - `reports/security/zap/newman/zap-newman-passive.json`
  - `reports/security/zap/newman/zap-newman-passive.urls.json`
- Observed URL count: 61.
- Alerts: 4.

Observed workflow areas:

- CSRF bootstrap.
- Legal documents.
- Public service/package catalog.
- Availability.
- Booking hold and idempotent hold replay.
- Booking checkout.
- Fake M-Pesa webhook success/duplicate/unknown cases.
- Booking status.
- Staff login/session routes.
- Staff booking schedule/week routes.
- Staff gallery category route.
- Public gallery homepage.
- Negative security cases from the Newman collection.

Findings:

| Rule ID | Alert | Risk | Instances | Triage |
| --- | --- | --- | ---: | --- |
| 10038 | Content Security Policy Header Not Set | Medium | 1 | True positive on booking hold response. Add CSP/security headers for API responses. |
| 10010 | Cookie No HttpOnly Flag | Low | 2 | Needs review. Instances are `csrftoken` on CSRF/login flow; Django commonly leaves CSRF cookie script-readable for header submission, but policy must be explicit. Session cookie was not reported under this rule. |
| 10111 | Authentication Request Identified | Informational | 1 | Expected. Staff login route observed by passive proxy. |
| 10112 | Session Management Response Identified | Informational | 7 | Expected. CSRF/session workflow observed by passive proxy. Values were not included in this triage. |

## Open Findings

- Add global CSP for normal and error responses.
- Add Permissions-Policy for normal and error responses.
- Decide and enforce CORP/COOP policy for health/API responses.
- Add explicit cache headers for health/error/security-sensitive API responses.
- Decide whether CSRF cookie non-HttpOnly is accepted by policy or whether the
  frontend can use a different CSRF bootstrap design.
- Add OpenAPI schema tooling in a future API documentation phase if desired.

## Non-Findings / Boundaries

- ZAP did not report debug tracebacks.
- ZAP did not report sensitive information in URLs.
- ZAP did not report X-Content-Type-Options missing.
- ZAP did not run active checks.
- ZAP does not prove BOLA/IDOR or mass-assignment protection; those remain Phase
  3B work.
