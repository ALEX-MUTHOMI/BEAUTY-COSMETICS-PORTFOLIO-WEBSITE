# Phase 3A OWASP Web/API Top 10 Report

## Executive Verdict

Status: **Phase 3A report complete; Phase 3A-P security tooling and runtime
stabilization patches applied.**

Phase 3A started as a report-only security discovery phase. Follow-up
Phase 3A-P patches added bounded tooling/runtime hardening only: security header
middleware, gated OpenAPI schema exposure for security scans, throttle malformed
body regression tests, and test database lifecycle tooling. Booking rules,
checkout/billing truth rules, gallery security behavior, and staff
auth/session business rules were not intentionally changed.

Production readiness remains **rejected / not claimed**.

## Scope

Assessed local Docker environment for:

- API endpoint inventory.
- OWASP Web Top 10 mapping.
- OWASP API Security Top 10 mapping.
- Existing test coverage.
- Safe local ZAP baseline attempt.
- Log and response privacy review.
- Evidence-based Phase 3A-P patch backlog.

Out of scope:

- ZAP full scan or active scan.
- Destructive attack testing.
- Real Daraja calls.
- Real email provider calls.
- Real Cloudflare/R2 production calls.
- Production scanning.
- Code patching.

## Target Environment

- Branch: `development`.
- Local backend: `http://localhost:8000`.
- Local frontend: `http://localhost:3000`.
- Docker services before ZAP attempt: web, worker, db, redis, frontend were healthy.
- HTTP health checks returned `301` to HTTPS because local settings enforce SSL redirect.
- `curl -k https://localhost:8000/...` failed on Windows Schannel with `SEC_E_NO_CREDENTIALS`.
- Newman still exercised the local API successfully over `http://localhost:8000`.

## Precheck Evidence

- `git status --short --branch`: clean `development`.
- `.env`, `db.sqlite3`, and `tests/postman/reports/newman-local.json`: not tracked.
- `docker compose config -q`: passed.
- `python manage.py check`: passed.
- `python manage.py makemigrations --check --dry-run`: no changes detected.
- `pytest --collect-only -q`: 581 tests collected before Phase 3A-P3 additions.
- `python -m compileall bookings checkout billing tests/factories`: passed.

## Endpoint Inventory Summary

| Area | Routes | Sensitivity | Notes |
| --- | --- | --- | --- |
| Health/CSRF | `/health/`, `/api/health-check/`, `/api/csrf/` | Public / auth support | CSRF bootstrap sets no-store and nosniff. |
| Auth/OTP | `/api/auth/request-otp/`, `/api/auth/verify-otp/` | Auth/session-sensitive, customer PII | Turnstile/negative tests cover controlled denial. |
| Legal | `/api/legal/documents/...` | Public | Sanitization and generic 404 tests exist. |
| Public catalog | `/api/bookings/catalog/services/`, `/api/bookings/catalog/packages/` | Public | Newman verifies safe response contract. |
| Availability | `/api/bookings/availability/` | Low/customer operational | Bounded query/range/security tests exist. |
| Holds | `/api/bookings/holds/` | Customer PII, anti-bot | CSRF, idempotency, abuse, capacity, and race tests exist. |
| Booking checkout bridge | `/api/bookings/checkout/` | Customer/payment-sensitive | Server-derived amount and policy acceptance tests exist. |
| Booking status | `/api/bookings/status/<public_booking_id>/` | Customer status | Generic 404, no PII/provider leakage tests exist. |
| Customer remembered device | `/api/customers/remembered-device/...` | Auth/session-sensitive, customer PII | Token hashing, revocation, non-account behavior tests exist. |
| Checkout sessions | `/api/checkout/sessions/...` | Payment-sensitive | Auth-scoped detail/create/STK tests exist. |
| M-Pesa webhook | `/api/checkout/mpesa/webhook/` | Provider-sensitive/payment truth | Fails closed; duplicate/malformed/unknown tests exist. |
| Legacy billing payment routes | `/api/billing/mpesa-webhook/`, `/api/billing/stk-push/` | Payment-sensitive legacy surface | Present but disabled with `410 Gone`. |
| Staff auth | `/api/staff/auth/...` | Staff auth/session-sensitive | Generic errors, reset, OAuth-start, reauth tests exist. |
| Staff portal | `/api/staff/bookings/...` | Staff/customer PII | Staff-only, payment visibility, contact reveal audit tests exist. |
| Staff gallery | `/api/staff/gallery/...` | Storage-sensitive, staff-only | Upload intent, caps, malicious file tests exist. |
| Public gallery | `/api/gallery/public/...` | Public/storage-sensitive | Optimized-only output, no storage-key exposure, sensitive filtering tests exist. |
| Admin | `/admin/...` | Admin-sensitive | Enabled in local route surface when `DISABLE_DJANGO_ADMIN` is false; staging config can disable. |

## High-Risk Routes

| Route/workflow | Severity | Reason | Current protection |
| --- | --- | --- | --- |
| `/api/checkout/mpesa/webhook/` | Critical | Payment truth is externally triggered. | Webhook inbox, idempotency, amount/state validation, fail-closed tests. |
| `/api/bookings/checkout/` | High | Booking can cross into payment flow. | Server-side amount, policy acceptance, idempotency tests. |
| `/api/bookings/holds/` | High | Can be abused for inventory denial. | CSRF, TTL, Redis abuse counters, race/load tests. |
| `/api/staff/bookings/<id>/contact-access/` | High | Explicit PII reveal surface. | Staff permission, recent reauth, audit tests. |
| `/api/staff/gallery/images/` | High | Malicious upload and storage privacy risk. | Validation, quarantine, caps, processing tests. |
| `/api/billing/* legacy payment routes` | Medium | Inventory management risk if forgotten. | Routes return `410 Gone`; document and keep tests. |
| `/admin/` | Medium local / High staging if exposed | Admin route is present locally. | Staging hardening can disable/block. |

## OWASP Web Top 10 Mapping

| Category | App-specific risk | Current evidence | Gap / follow-up |
| --- | --- | --- | --- |
| A01 Broken Access Control | Public/customer/staff boundaries, contact reveal, checkout ownership. | Security tests, staff permission tests, Newman negative checks. | Add route-level BOLA matrix for every object-id route in Phase 3A-P. |
| A02 Cryptographic Failures | Tokens, provider refs, receipt tokens, cookies, logs. | Secret hygiene passed; log scan found no targeted secret/PII markers; cookie tests exist. | Add automated response scanner for token-like fields across Newman JSON. |
| A03 Injection | Booking inputs, webhook payloads, legal slugs, gallery metadata. | XSS/legal/generic error tests; webhook malformed tests; upload validation tests. | Add API fuzz smoke for query params without destructive payloads. |
| A04 Insecure Design | Payment confirmation, late payment, duplicate callbacks, booking capacity. | Load/security/integration tests cover duplicate, expiry, amount mismatch, capacity. | Keep late-payment/manual-review path in staging rehearsal checklist. |
| A05 Security Misconfiguration | SSL redirect, CORS/CSRF/cookies/admin exposure. | `manage.py check`; Newman CSRF; cookie tests; local route inventory; security header middleware tests; ZAP passive scan scripts. | Keep staging route-block checks and frontend CSP hardening in the deployment checklist. |
| A06 Vulnerable Components | Python/Django/DRF/Celery/Node/Docker images. | Lockfiles and Bandit present; no package audit executed in 3A. | Add dependency audit phase for Poetry and npm. |
| A07 Identification/Auth Failures | OTP, staff login, reset, session rotation, remembered device. | Staff/auth/OTP/security tests exist. | Add API contract checks for lockout response shape. |
| A08 Software/Data Integrity Failures | Provider callbacks, fake-vs-real provider boundary, CI gates. | Fake provider default, webhook tests, lint/security gates. | Add CI job that runs report-only route inventory diff. |
| A09 Logging/Monitoring Failures | Missing or leaking audit/security logs. | Log scan no sensitive markers; audit tests exist. | Worker health became unhealthy after long scan/test sequence; add SRE health alert/runbook. |
| A10 SSRF | Remote media, callback URLs, storage providers. | PDF/image URL rejection tests exist; Daraja callback URL tests exist. | Add outbound-request inventory and explicit allowlist documentation. |

## OWASP API Security Top 10 Mapping

| Category | App-specific risk | Current evidence | Gap / follow-up |
| --- | --- | --- | --- |
| API1 BOLA | Booking/status/checkout/staff object IDs. | Status/staff/checkout ownership tests exist. | Generate a complete object-route authorization matrix. |
| API2 Broken Authentication | OTP/staff login/reset/session/logout. | Auth tests, throttling, generic errors. | Add Newman auth-abuse cases for reset and reauth. |
| API3 BOPLA | Client-supplied IDs/roles/amounts. | Server-side amount tests; serializers/service ownership. | Add mass-assignment negative tests for `user_id`, `staff_id`, `role`, `business_id`. |
| API4 Resource Consumption | Holds, OTP, STK, webhook, gallery uploads, status polling. | Load/latency tests passed; OTP/STK malformed-body throttle regressions added. | Add full per-endpoint rate-limit inventory doc. |
| API5 Function Authorization | Staff-only actions, contact reveal, disabled billing routes. | Staff/security tests; billing routes disabled. | Add Newman negative checks for each staff route. |
| API6 Sensitive Business Flows | Booking hold bombing, OTP/email cost, contact reveal, uploads. | Load/security tests passed. | Add abuse-budget monitoring metrics. |
| API7 SSRF | User-controlled remote URLs or provider callback URLs. | PDF/image renderer tests; Daraja callback URL tests. | Add static outbound HTTP call inventory. |
| API8 Misconfiguration | Headers, CORS, CSRF, DEBUG, admin. | Settings checks, security header middleware tests, OpenAPI scan gating tests, ZAP baseline scripts. | Keep production/staging proxy policy and frontend CSP in follow-up hardening. |
| API9 Inventory Management | Legacy billing routes, wrappers, undocumented endpoints. | Route inventory created; legacy billing routes return 410. | Track disabled-route tests and deprecation owner. |
| API10 Unsafe API Consumption | Daraja, email provider, storage provider. | Fake provider default; adapter tests; error redaction tests. | Staging sandbox callback remains outside this phase. |

## Existing Test Coverage

| Risk | Existing tests | Strength | Missing follow-up |
| --- | --- | --- | --- |
| Booking hold abuse/race/capacity | `bookings/tests`, `tests/load`, `tests/security` | Strong | Add API inventory-driven ownership matrix. |
| Checkout webhook replay/mismatch/expired/cancelled | `checkout/tests`, `tests/integration`, `tests/security`, `tests/load` | Strong | Add Newman replay negative cases if safe. |
| Billing immutability/redaction | `billing/tests`, integration/security tests | Strong | Add dependency on audit export/reconciliation checks. |
| Gallery public/privacy/upload | `bookings/tests/test_gallery_*`, `tests/security/test_gallery_*` | Strong | Add public route response scanner for storage-key patterns. |
| Staff auth/contact reveal | `bookings/tests/test_staff_*`, `tests/security/test_staff_*` | Strong | Add Newman negative staff authorization routes. |
| Logs/secrets | security tests, secret hygiene, log scan | Partial/Strong | Add CI log scanner after integration/load jobs. |
| ZAP passive headers/config | ZAP health/root/API/Newman workflows | Stronger after 3A-P | Keep passive scans bounded; do not run active scans by default. |

## AestheticOS-Specific Security Questions

### A. Can a public user access private booking/customer data?

Evidence: booking status endpoint generic 404 tests, customer status red-team tests,
staff-only route tests, Newman negative checks. Current protection appears strong
for tested routes. Follow-up: complete BOLA matrix for every object-id route.

### B. Can customer A access customer B's booking, checkout, receipt, or status?

Evidence: checkout detail selector is customer-scoped; status tests assert generic
response and no provider leakage. Follow-up: add explicit cross-customer API
negative tests for every current and future receipt/status route.

### C. Can request body change ownership or role fields?

Evidence: checkout/booking services derive customer/session context server-side;
amount tampering tests exist. Follow-up: add mass-assignment tests for `user_id`,
`customer_id`, `staff_id`, `role`, `business_id`, `tenant_id`, and `org_id`.

### D. Can role/session claims be modified to access staff/admin endpoints?

Evidence: staff session tests cover staff-only boundaries and customer-token
isolation. Admin is present locally when not disabled. Follow-up: staging must
set `DISABLE_DJANGO_ADMIN=True` or proxy-block `/admin/`.

### E. Can payment truth be faked?

Evidence: checkout/billing tests cover duplicate callbacks, amount mismatch,
expired/cancelled callbacks, failed callbacks, rollback safety, and immutable
ledger behavior. Current protection appears strong in fake-provider/local tests.

### F. Can gallery private data leak?

Evidence: public gallery output tests assert optimized public variants only and
no storage-key exposure; upload validation tests reject malicious/corrupt inputs.

### G. Can staff contact reveal leak PII?

Evidence: contact reveal requires permission/recent reauth and creates redacted
audit events. Follow-up: add Newman negative cases for contact reveal.

### H. Can the booking form expose existing user data?

Evidence: hold and status tests assert generic errors and no raw PII reflection.
Follow-up: add response-field allowlist scanner for public booking endpoints.

### I. Do logs expose secrets or PII?

Evidence: log scan found zero hits for targeted secret/PII markers. Worker logs
redacted Redis credentials as `redis://:**@...`. No raw provider payload markers
were found.

### J. Does row-level locking protect the right risk?

Row-level locking protects concurrency/race conditions. It does not replace
object authorization. Current concurrency tests are strong for booking holds,
capacity, webhook replay, and ledger idempotency. Phase 3A-P should add a
complete object-authorization matrix for all object-id routes.

## ZAP Baseline Summary

Phase 3A-P0 stabilized passive ZAP execution, Phase 3A-P1 broadened passive
coverage, and Phase 3A-P2/P3 added gated OpenAPI schema exposure plus security
header policy tests.

Completed local passive modes:

- Health baseline: `http://host.docker.internal:8000/health/`.
- Root baseline: `http://host.docker.internal:8000/`.
- Newman-through-ZAP passive proxy for API workflows.

OpenAPI safety:

- The schema endpoint is disabled in the default runtime.
- The schema endpoint is enabled only in the explicit security-scan profile.
- Sensitive marker tests reject provider payloads, callback payload language,
  storage keys, token hashes, provider IDs, and secret-bearing fields.

No ZAP full scan, active scan, Burp scan, production scan, real Daraja call, real
email provider call, or real storage provider call was run.

Findings are tracked in `docs/security/ZAP_BASELINE_TRIAGE.md` and coverage is
tracked in `docs/security/ZAP_COVERAGE_SUMMARY.md`.

Backend/API security headers are now enforced through middleware and covered by
tests. The CSRF cookie HttpOnly finding is documented as an intentional
SPA-compatible policy until the frontend CSRF bootstrap is redesigned. Frontend
Nuxt CSP tightening remains a separate deployment-hardening task.

## Log/Privacy Review

Scanned recent logs for:

- `Traceback`
- `DEBUG=True`
- passkeys
- consumer key/secret
- access/refresh token markers
- session/csrf markers
- receipt tokens
- checkout/ledger/provider IDs
- storage keys/private buckets
- `phone=`
- `email=`
- raw/provider payload markers

Result: zero hits across web, worker, db, redis, and frontend in the scripted scan.

Notable operational finding: a destination-specific Celery ping can fail when
the expected hostname does not match the actual worker node name. Use an
undirected bounded `celery inspect ping` for local health confirmation, and keep
worker health under observation after long ZAP/load runs.

## Patch Backlog Summary

Detailed backlog is in `docs/security/PHASE_3A_PATCH_BACKLOG.md`.

Highest remaining priority:

1. Add full object-level authorization matrix tests for every object-id route.
2. Add mass-assignment negative tests for ownership/role fields.
3. Add Newman negative cases for staff-only and contact-reveal endpoints.
4. Add dependency/SBOM audit coverage for Python and Node dependencies.
5. Keep frontend CSP, staging proxy route-blocking, and operational runbooks in
   the production-readiness backlog.

## Non-Production-Readiness Statement

This report does not claim production readiness. Production readiness remains
rejected pending staging rehearsal, live-provider sandbox callback proof,
monitoring/alerting, incident response, credential rotation, rollback runbooks,
and a controlled live/canary payment rehearsal.
