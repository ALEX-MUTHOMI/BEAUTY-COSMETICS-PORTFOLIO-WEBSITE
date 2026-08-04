# Security Test Matrix

| Endpoint / workflow | OWASP Web | OWASP API | Attack / risk scenario | Existing tests | Missing tests | Expected safe response | Severity | Phase owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/health/`, `/api/health-check/` | A05 | API8/API9 | Health route exposes debug/internal data. | Newman health checks, API tests. | Add header assertions via ZAP/Newman. | 200 with safe body only. | Low | Platform |
| `/api/csrf/` | A05/A07 | API2/API8 | CSRF bootstrap leaks secrets or lacks safe cache headers. | Newman CSRF bootstrap. | Add explicit header regression tests. | 200 JSON, CSRF cookie, no-store. | Medium | Backend |
| `/api/auth/request-otp/` | A07/A09 | API2/API4/API6 | OTP enumeration/cost abuse. | OTP/security tests, Newman missing-Turnstile denial. | Add response timing/enumeration test. | Generic denial / throttle. | High | Auth |
| `/api/auth/verify-otp/` | A07 | API2/API4 | OTP brute force/replay. | Unit/security tests. | Add Newman negative replay case. | Generic failure / throttle. | High | Auth |
| `/api/legal/documents/...` | A03/A05 | API8/API9 | XSS in slug/content or debug 404. | Legal sanitization tests, Newman XSS slug. | Add passive ZAP once stable. | Sanitized HTML or generic 404. | Medium | Legal/API |
| `/api/bookings/catalog/*` | A05 | API9 | Overexposes internal IDs or inactive catalog data. | Catalog tests, Newman. | Add schema allowlist. | Public-safe catalog. | Medium | Booking |
| `/api/bookings/availability/` | A01/A04/A03 | API1/API4/API6 | Range abuse, inactive service probing, PII reflection. | Availability security/load tests. | Add Newman negative malformed-date cases. | Generic unavailable / bounded response. | High | Booking |
| `/api/bookings/holds/` | A01/A04/A07 | API3/API4/API6 | Bot holds, price tampering, duplicate inventory locks. | Hold idempotency/security/load tests, Newman CSRF/tampering. | Add broad mass-assignment body test. | 201 idempotent, 400/403 generic. | High | Booking |
| `/api/bookings/checkout/` | A04/A08 | API3/API6/API10 | Client changes amount/linkage or bypasses policy. | Checkout contract/policy tests, Newman. | Add wrong currency/linkage API-level cases. | 201 only with server-derived amount. | High | Booking/Checkout |
| `/api/bookings/status/<id>/` | A01/A02 | API1/API3/API9 | Booking enumeration or provider/PII leak. | Status endpoint/red-team tests, Newman status checks. | Add cross-customer status access matrix. | 200 minimal safe status or generic 404. | High | Booking |
| `/api/customers/remembered-device/*` | A02/A07 | API2/API3 | Opaque token replay or account bypass. | Remember-device tests. | Add Newman cookie lifecycle cases. | Redacted summary / safe revoke. | High | Customer |
| `/api/checkout/sessions/` | A01/A04/A08 | API1/API3/API4/API6 | Cross-user checkout/session creation abuse. | Checkout API permission/idempotency tests. | Add Newman unauthenticated and cross-user cases. | 401/403 or scoped session. | High | Checkout |
| `/api/checkout/sessions/<uuid>/` | A01/A02 | API1/API3 | Customer A reads customer B checkout. | Checkout permission tests. | Add response-field allowlist. | 404/403 generic. | High | Checkout |
| `/api/checkout/sessions/<uuid>/mpesa/stk/` | A04/A08/A09 | API4/API6/API10 | STK storms, spoofed phone, provider outage. | Throttle/provider error/load/latency tests. | Add Newman throttling smoke if deterministic. | 202 or controlled 429/503. | High | Checkout |
| `/api/checkout/mpesa/webhook/` | A04/A08/A10 | API4/API6/API10 | Fake success, replay, mismatch, malformed payload. | Webhook, integration, security, load tests. | Add passive ZAP once stable. | 202/400 controlled, no ledger on invalid. | Critical | Checkout/Billing |
| `/api/billing/mpesa-webhook/`, `/api/billing/stk-push/` | A05/A09 | API5/API9 | Legacy payment path accidentally active. | Route source shows 410 Gone. | Add explicit tests for 410 if absent. | 410 Gone. | Medium | Billing |
| `/api/staff/auth/login/` | A07/A09 | API2/API4/API6 | Enumeration/bruteforce/CSRF. | Staff login/rate-limit tests, Newman login. | Add Newman bad-credential generic error check. | Generic 401/429 or session. | High | Staff |
| `/api/staff/auth/password-reset/*` | A07/A02 | API2/API6 | Reset enumeration/token reuse. | Password reset tests. | Add Newman safe generic flow. | Generic success/failure. | High | Staff |
| `/api/staff/auth/reauth/` | A07 | API2/API5 | Bypass recent reauth for sensitive action. | Recent reauth/contact tests. | Add Newman contact reveal without reauth. | 401/403 generic. | High | Staff |
| `/api/staff/bookings/*` | A01/A02 | API1/API5 | Public/customer reads staff booking data. | Staff portal/privacy/security tests, Newman staff flow. | Add per-route unauthenticated Newman checks. | 401/403 generic. | High | Staff |
| `/api/staff/bookings/<id>/contact-access/` | A01/A09 | API1/API5/API6 | PII reveal without permission/reauth/audit. | Contact reveal audit/red-team tests. | Add response cache/header test. | No-store redacted audit or deny. | High | Staff |
| `/api/staff/gallery/images/` | A03/A04/A10 | API4/API5/API7 | Malicious upload, decompression/SSRF/storage leak. | Gallery validation/upload/storage tests. | Add upload quota response contract test. | Reject/quarantine/fail closed. | High | Gallery |
| `/api/gallery/public/*` | A01/A02 | API1/API3/API9 | Private storage key or sensitive content leak. | Public gallery/security/load tests, Newman homepage. | Add schema allowlist for all public gallery routes. | Optimized public variants only. | High | Gallery |
| `/admin/` | A01/A05 | API5/API8/API9 | Admin exposed outside trusted environment. | Settings support disabling. | Add staging route-block verification. | Disabled or protected. | High in staging | Platform |

## Cross-Cutting Missing Tests

- Full object-level authorization matrix for every route containing an object id.
- Mass-assignment negative tests for ownership/role/tenant-like fields.
- Newman negative cases for all staff-only routes.
- Response field allowlist scanning for public booking, status, checkout, gallery, and staff payment routes.
- Stable passive ZAP baseline with triaged findings.
- CI log scanner after security/load/integration gates.

## Redis release gates

| Gate | Purpose |
| --- | --- |
| Lua contract test | Detects key, argument, and result-shape drift. |
| Fake Redis contract test | Keeps the OTP test double aligned with the current Lua boundary. |
| OTP encrypted-state test | Prevents raw recipient and OTP values in Redis keys/values. |
| OTP encrypted-delivery test | Prevents raw recipient and OTP values in Celery task arguments. |
| Fake-provider task test | Prevents SMTP/network activity in fake mode. |
| Redis-unavailable route test | Confirms protected routes fail closed with generic 503. |
| Abuse TTL and normal-admission tests | Prevent permanent actions and unnecessary normal-traffic abuse writes. |
| Bounded cleanup test | Prevents unsafe `KEYS` or database-wide Redis cleanup. |
