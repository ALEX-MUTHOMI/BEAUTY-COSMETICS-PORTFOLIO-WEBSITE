# Phase 3A-P Patch Backlog

This backlog is evidence-based from Phase 3A mapping, route audit, tests, logs,
and safe baseline execution. No patches were applied in Phase 3A.

| ID | Source | Affected area | Severity | Recommended phase | Recommended test | Patch risk | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3A-P-001 | Docker health / Celery ping | Worker health and responsiveness after long verification runs | High | 3A-P SRE hardening | Healthcheck test or management command that asserts worker ping under bounded timeout | Medium | SRE |
| 3A-P-002 | ZAP timeout | Passive ZAP baseline execution | Resolved tooling / open findings | 3A-P security tooling | `scripts/security/zap_baseline_local.ps1` now completes and archives HTML/MD/JSON reports | Low/Medium | DevSecOps |
| 3A-P-003 | OWASP API1 mapping | Object-level authorization for every object-id route | High | 3B BOLA test expansion | Parameterized cross-user tests for booking, checkout, receipt/status, staff booking routes | Medium | Backend/Security |
| 3A-P-004 | OWASP API3 mapping | Mass assignment of ownership/role fields | High | 3B API negative tests | Submit `user_id`, `customer_id`, `staff_id`, `role`, `business_id`, `tenant_id`, `org_id` to public/customer/staff write routes | Low | Backend |
| 3A-P-005 | OWASP API5 mapping | Staff-only route coverage in Newman | Medium | 3A-P API contract | Newman unauthenticated/customer-session negative requests for staff routes | Low | API QA |
| 3A-P-006 | OWASP A02/API3 mapping | Response field allowlists | Medium | 3A-P response privacy | Automated scanner over Newman JSON for internal fields, tokens, storage keys, ledger/checkout/provider IDs | Low | DevSecOps |
| 3A-P-007 | OWASP A05/API8 mapping | Admin exposure in staging | High | Staging hardening | Staging curl/Newman route-block tests for `/admin/`, `/api/billing/`, and unfinished APIs | Low | Platform |
| 3A-P-008 | OWASP A09 mapping | Security log and audit classification | Medium | Observability phase | Log scanner after integration/load/security gates, plus audit event coverage report | Medium | SRE/Security |
| 3A-P-009 | OWASP API9 mapping | Legacy billing disabled routes | Medium | 3A-P regression | Explicit tests that legacy billing STK/webhook routes return 410 and do not call providers | Low | Billing |
| 3A-P-010 | OWASP API7/A10 mapping | Outbound HTTP and provider consumption inventory | Medium | 3A-P architecture docs | Static inventory for Daraja, email, storage, PDF/image renderer outbound behavior | Low | Security Architecture |
| 3A-P-011 | OWASP API4/API6 mapping | Per-endpoint rate-limit inventory | Medium | 3B abuse controls | Document/test rate limits for OTP, holds, checkout, STK, webhook, gallery upload, status polling | Medium | Backend/SRE |
| 3A-P-012 | Dependency review | Vulnerable/outdated components | Medium | Dependency audit phase | Poetry/npm audit or equivalent SBOM check in CI | Medium | DevSecOps |
| 3A-P-013 | ZAP passive findings | Missing CSP, Permissions-Policy, CORP, and cache headers on health/error responses | Medium | Security headers hardening | Middleware/header tests plus rerun ZAP baseline | Low/Medium | Backend/Security |
| 3A-P-014 | ZAP coverage | OpenAPI schema unavailable for schema-driven passive API scan | Medium | API documentation/security tooling | Add OpenAPI schema and safe ZAP API baseline if product decision approves public/internal schema | Medium | API/Security |
| 3A-P-015 | ZAP Newman proxy | CSRF cookie reported without HttpOnly in passive workflow scan | Low/Needs review | CSRF policy review | Explicit CSRF cookie policy test/doc; confirm frontend CSRF header mechanism requires script-readable CSRF token or redesign bootstrap | Low/Medium | Backend/Frontend Security |
| 3A-P-016 | ZAP Newman proxy | API responses missing CSP/security headers in workflow-observed route | Medium | Security headers hardening | Header middleware tests covering normal, API, 404, and error responses | Low/Medium | Backend/Security |

## Deferred But Required Before Production Readiness

- Production-like staging rehearsal.
- Real Daraja sandbox callback proof on stable HTTPS.
- Monitoring and alerting.
- Credential rotation documentation.
- Refund/reversal runbooks.
- Incident response runbook.
- Controlled low-value live/canary payment reconciliation.
