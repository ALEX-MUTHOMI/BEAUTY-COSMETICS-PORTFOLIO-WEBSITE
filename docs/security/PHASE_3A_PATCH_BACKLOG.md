# Phase 3A-P Patch Backlog

This backlog is evidence-based from Phase 3A mapping, route audit, tests, logs,
and safe baseline execution. No patches were applied in Phase 3A.

| ID | Source | Affected area | Severity | Recommended phase | Recommended test | Patch risk | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3A-P-001 | Docker health / Celery ping | Worker health and responsiveness after long verification runs | Partially resolved / monitor | 3A-P SRE hardening | Undirected Celery ping should be used when container hostname does not match the expected worker destination | Medium | SRE |
| 3A-P-002 | ZAP timeout | Passive ZAP baseline execution | Resolved tooling / open findings | 3A-P security tooling | `scripts/security/zap_baseline_local.ps1` now completes and archives HTML/MD/JSON reports | Low/Medium | DevSecOps |
| 3A-P-003 | OWASP API1 mapping | Object-level authorization for every object-id route | High | 3B BOLA test expansion | Parameterized cross-user tests for booking, checkout, receipt/status, staff booking routes | Medium | Backend/Security |
| 3A-P-004 | OWASP API3 mapping | Mass assignment of ownership/role fields | High | 3B API negative tests | Submit `user_id`, `customer_id`, `staff_id`, `role`, `business_id`, `tenant_id`, `org_id` to public/customer/staff write routes | Low | Backend |
| 3A-P-005 | OWASP API5 mapping | Staff-only route coverage in Newman | Medium | 3A-P API contract | Newman unauthenticated/customer-session negative requests for staff routes | Low | API QA |
| 3A-P-006 | OWASP A02/API3 mapping | Response field allowlists | Partially resolved / expand | 3A-P response privacy | OpenAPI banned-marker scan now includes tokens, provider payloads, storage keys, callback payload, and token hashes; Newman JSON scanner remains a Phase 3B expansion | Low | DevSecOps |
| 3A-P-007 | OWASP A05/API8 mapping | Admin exposure in staging | High | Staging hardening | Staging curl/Newman route-block tests for `/admin/`, `/api/billing/`, and unfinished APIs | Low | Platform |
| 3A-P-008 | OWASP A09 mapping | Security log and audit classification | Medium | Observability phase | Log scanner after integration/load/security gates, plus audit event coverage report | Medium | SRE/Security |
| 3A-P-009 | OWASP API9 mapping | Legacy billing disabled routes | Medium | 3A-P regression | Explicit tests that legacy billing STK/webhook routes return 410 and do not call providers | Low | Billing |
| 3A-P-010 | OWASP API7/A10 mapping | Outbound HTTP and provider consumption inventory | Medium | 3A-P architecture docs | Static inventory for Daraja, email, storage, PDF/image renderer outbound behavior | Low | Security Architecture |
| 3A-P-011 | OWASP API4/API6 mapping | Per-endpoint rate-limit inventory | Partially resolved / expand | 3B abuse controls | OTP and STK throttle malformed-body semantics now have regression tests; full endpoint inventory remains required | Medium | Backend/SRE |
| 3A-P-012 | Dependency review | Vulnerable/outdated components | Medium | Dependency audit phase | Poetry/npm audit or equivalent SBOM check in CI | Medium | DevSecOps |
| 3A-P-013 | ZAP passive findings | Missing CSP, Permissions-Policy, CORP, and cache headers on health/error responses | Resolved in 3A-P2/P3 | Security headers hardening | Middleware/header tests and ZAP reruns verify the current policy; frontend CSP remains tracked separately | Low/Medium | Backend/Security |
| 3A-P-014 | ZAP coverage | OpenAPI schema unavailable for schema-driven passive API scan | Resolved with gated exposure | API documentation/security tooling | OpenAPI schema exists only when explicitly enabled for security scan profile; default runtime returns 404 | Medium | API/Security |
| 3A-P-015 | ZAP Newman proxy | CSRF cookie reported without HttpOnly in passive workflow scan | Documented policy | CSRF policy review | CSRF cookie remains script-readable where required for SPA header submission; policy documented and should be revisited if bootstrap changes | Low/Medium | Backend/Frontend Security |
| 3A-P-016 | ZAP Newman proxy | API responses missing CSP/security headers in workflow-observed route | Resolved in 3A-P2/P3 | Security headers hardening | Header middleware tests cover normal, API, 404, and error responses | Low/Medium | Backend/Security |

## Phase 3A-P3 Closeout Notes

- Throttle hardening: OTP and STK throttles now preserve valid `ip:email` semantics while falling back to IP-only keys for hostile or malformed parsed request bodies.
- OpenAPI hardening: the schema remains disabled in the default runtime and is exposed only in the explicit security-scan profile. Sensitive marker checks include provider payloads, token hashes, raw callback language, storage keys, provider IDs, and secret-bearing field names.
- Test database lifecycle: stale PostgreSQL test database sessions are handled through an explicit dry-run-first cleanup script that refuses non-test database names and requires a confirmation flag for destructive actions.
- Monolithic pytest runtime: the canonical CI gate is the partitioned matrix in `docs/testing/CI_TEST_MATRIX.md`. A monolithic full-suite run remains a best-effort diagnostic path because long-running load/latency/security combinations can exceed local Docker runtime budgets and can leave stale test DB sessions after interrupted runs.
- Frontend CSP: backend API headers are enforced centrally. Nuxt/browser CSP tightening remains a separate frontend deployment hardening item because inline/runtime assets must be inventoried before enabling a stricter browser policy.

## Phase 3A-P4 Closeout Notes

- Turbo Pass: fast verification is now a first-class lane through `scripts/ci/turbo_pass.ps1`. It runs config, Django, migration, collect-only, targeted security, API/security, unit/integration, Docker Newman, lint/security, secret hygiene, Docker health, and worker ping.
- Docker Newman: Docker Newman is canonical through `scripts/ci/run_newman_docker.ps1`; host `newman.cmd` is optional and no longer blocks backend verification.
- Git hygiene parity: git/index-aware checks are owned by `scripts/ci/git_hygiene_host.ps1`; runtime containers remain git-free and continue to run filesystem secret hygiene.
- Performance budgeting: load and latency are preserved and budgeted through `scripts/ci/run_performance_gate.ps1`. They are not weakened or moved out of the standard performance lane.
- Passive security: ZAP/OpenAPI/Newman passive scans remain separate through `scripts/ci/run_security_passive_gate.ps1`; active/full scans remain out of default CI.
- Frontend CSP: policy is documented in `docs/security/FRONTEND_CSP_POLICY.md`. Backend CSP is not represented as complete browser CSP.

## Deferred But Required Before Production Readiness

- Production-like staging rehearsal.
- Real Daraja sandbox callback proof on stable HTTPS.
- Monitoring and alerting.
- Credential rotation documentation.
- Refund/reversal runbooks.
- Incident response runbook.
- Controlled low-value live/canary payment reconciliation.
