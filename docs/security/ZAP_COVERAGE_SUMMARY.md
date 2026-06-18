# ZAP Coverage Summary

This summary measures what ZAP passively observed. It does not claim app-wide
security completeness.

## Mode Summary

| Mode | Target | Scan type | Exit/result | Artifacts | Observed URLs | Alerts |
| --- | --- | --- | --- | --- | ---: | ---: |
| Health | `http://host.docker.internal:8000/health/` | Passive baseline | Exit 2, completed with warnings | `reports/security/zap/health/` | 4 | 2 |
| Root | `http://host.docker.internal:8000/` | Passive baseline | Exit 2, completed with warnings | `reports/security/zap/root/` | 3 | 1 |
| API schema | `http://host.docker.internal:8000/api/schema/` | Safe OpenAPI passive scan | Exit 2, completed with warnings | `reports/security/zap/api/` | 15 | 5 |
| Newman proxy | Newman workflows through ZAP proxy | Passive observation | Newman exit 0, ZAP report generated | `reports/security/zap/newman/` | 61 | 3 |

## Coverage Matrix

| Category | Coverage classification | Notes |
| --- | --- | --- |
| Health | Observed by ZAP | Health baseline and Newman flow hit health. |
| Root/error/static behavior | Observed by ZAP | Root baseline observed 404/root/robots/sitemap behavior. |
| CSRF | Observed through Newman proxy | CSRF bootstrap observed; CSRF cookie warning is triaged. |
| Legal | Observed through Newman proxy | Legal list/detail workflows observed. |
| Public catalog | Observed through Newman proxy | Services/packages observed. |
| Availability | Observed through Newman proxy | Normal and full-package availability observed. |
| Booking hold | Observed through Newman proxy | Create, duplicate/idempotent retry, and price tampering observed. |
| Booking checkout | Observed through Newman proxy | Held booking checkout observed with fake provider mode. |
| Booking status | Observed through Newman proxy | Confirmed and held status routes observed. |
| Checkout sessions | Only covered by pytest/Newman, not directly spidered | The Newman acceptance flow covers booking-to-checkout bridge, not every checkout session route. |
| Fake webhook | Observed through Newman proxy | Success, duplicate, unknown, and malformed fake callbacks observed. |
| Legacy disabled billing routes | Only covered by pytest/Newman, not ZAP | Keep explicit regression tests. |
| Staff auth | Observed through Newman proxy | Staff login and staff me observed. |
| Staff portal | Observed through Newman proxy | Staff schedule/week routes observed. |
| Staff contact reveal | Only covered by pytest/Newman, not ZAP | Keep Phase 3B negative matrix work. |
| Staff gallery | Observed through Newman proxy | Staff gallery categories observed with staff session. |
| Public gallery | Observed through Newman proxy | Homepage route observed. |
| Admin route | Not observed in P1 ZAP | Staging must block/disable admin; local passive scan did not exercise it. |

## Gaps

- OpenAPI schema is available only in the explicit security-scan profile.
  Default runtime keeps `/api/schema/` disabled and returning `404`.
- ZAP spidering does not discover authenticated/API workflows without Newman.
- Newman-through-ZAP observes API workflows, but it does not prove object-level
  authorization correctness.
- ZAP does not replace BOLA/IDOR, mass-assignment, role tampering, rate-limit,
  or business-logic abuse tests.

## Security Interpretation

P4A proves the scanner is configured for broader passive coverage and that it can
observe meaningful application workflows through Newman without leaving stale
scanner containers. It does not prove the Beauty app is production-ready or
vulnerability-free.
