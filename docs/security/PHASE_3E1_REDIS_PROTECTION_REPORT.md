# Phase 3E1 Redis Protection and Resilience Report

## Executive verdict

**PHASE 3E1 ACCEPTED — REDIS PROTECTION AND RESILIENCE BOUNDARY VERIFIED**

Production readiness remains **REJECTED / NOT CLAIMED**. This is local Docker
evidence only; it does not certify production network, WAF/CDN, provider, or
staging-resilience readiness.

## Previous blocker resolution

Phase 3E1 was previously blocked because the local Celery worker was unhealthy
and Docker verification could not complete. The current Docker stack is healthy
and the worker responded to a real `celery -A core inspect ping` with one pong.
The initial Turbo pass completed successfully. A later narrow billing-task
logging fix was directly tested and its full API/checkout/billing partition
passed. The required final Turbo rerun completed successfully on
2026-06-24 with all 21 gates passing in 964 seconds. The Phase 3E1
blocker is resolved.

## High-risk fix verification

| Fix | Verified | Evidence | Status |
| --- | --- | --- | --- |
| HMAC-derived OTP Redis key | yes | focused auth tests and count-only live probe | pass |
| HMAC OTP verifier/no reusable raw code | yes | focused auth tests and live verifier assertions | pass |
| No raw recipient in Redis OTP state | yes | focused auth tests and live key/value assertions | pass |
| Encrypted Celery delivery envelope | yes | focused auth and cross-suite selection | pass |
| Tampered envelope rejected | yes | focused auth test without mail invocation | pass |
| Fake mode has no network delivery | yes | focused auth test asserts mail sender is not called | pass |
| Lua fake-Redis contract current | yes | focused auth contract regression plus throttle/security suites | pass |

The OTP delivery task accepts framework correlation context only for base-task
compatibility. It does not place that context in delivery content or task logs.
The broker-facing delivery payload contains the encrypted envelope rather than
a raw recipient or reusable OTP.

## Redis boundary result

Redis remains a protected temporary control plane for admission, temporary OTP
verifiers, abuse score/action state, and Celery coordination. It does not own
booking, checkout, payment, ledger, capacity, staff-authorization, or media
visibility truth; PostgreSQL and Django transactions, constraints, state
machines, and authorization own those responsibilities.

Protected routes remain generic fail-closed when Redis admission is unavailable.
Normal public admission returned 200 and did not create abuse score/action
state. Redis pressure reduction remains an edge WAF/CDN and cache requirement,
not a claim that an edge deployment is complete.

## Verification results

| Gate | Current result |
| --- | --- |
| Docker services | web, Redis, database, and worker healthy |
| Django checks | normal and deploy checks passed |
| Celery | one worker pong received |
| Focused auth/OTP/envelope suite | 10 passed |
| Cross-suite OTP/Redis/envelope/fake selection | 50 passed, 621 deselected |
| Target throttle/abuse/diagnostic suite | 17 passed |
| Full security partition | 167 passed in 194.34 seconds |
| API/checkout/billing partition | 94 passed in 277.99 seconds |
| Load partition | 26 passed in 620.51 seconds |
| Latency partition | 27 passed in 60.69 seconds |
| Frontend type-check and build | passed |
| Newman collection | 30 requests and 91 assertions passed |
| Turbo serial gate | passed on final tree — 21 gates, 964s, result=passed (2026-06-24) |
| Black, isort, Ruff, flake8 | passed |
| Bandit configured medium/high gate | passed with no medium/high issues |
| Full Bandit raw-low baseline | existing low findings, including installed/test code; not a clean raw-low claim |
| Host Git and artifact hygiene | passed; no tracked secret markers |
| OpenAPI live path | generic 404 |
| Final Redis control-state counts | throttle 0, OTP 0, abuse score 0, abuse action 0 |
| Stale pytest processes | 0 |
| Stale test database sessions | 0 terminated |
| Recent log marker scan | 0 for traceback, internal error, Redis-unavailable, and invalid-envelope markers |

## Findings

### ID: 3E1-F-001

**Title:** Express-auth OTP Redis state used raw recipient and OTP values.

**Surface:** `users.services.OTPService`.

**Expected:** temporary OTP state is TTL-bound and exposes neither raw recipient
data nor a reusable OTP in Redis.

**Actual:** the prior implementation used a raw recipient key and raw OTP value.

**Impact:** authorized Redis inspection or accidental diagnostics could expose
authentication material and recipient PII.

**Severity:** High.

**Fix:** versioned HMAC-derived key and recipient-bound HMAC verifier; 300-second
TTL and successful-verification deletion are preserved.

**Regression:** focused auth suite, cross-suite OTP/Redis selection, and live
count-only assertions.

**Status:** fixed and verified.

### ID: 3E1-F-002

**Title:** Express-auth Celery task arguments carried raw recipient and OTP data.

**Surface:** request-OTP dispatch to the Redis-backed Celery broker.

**Expected:** broker task arguments and task logs do not carry raw recipient
data or reusable OTP values.

**Actual:** the prior invocation supplied raw delivery fields directly.

**Impact:** a broker inspection, event, or transport diagnostic could expose
authentication material.

**Severity:** High.

**Fix:** encrypted, authenticated minimal delivery envelope; worker-only
decryption; fake-mode early return; tampered-envelope rejection without retry
or mail delivery.

**Regression:** focused auth suite, cross-suite selection, and full security
partition.

**Status:** fixed and verified.

### ID: 3E1-F-003

**Title:** Local Celery worker health blocked prior verification.

**Surface:** Docker worker healthcheck and Phase 3E1 test execution.

**Expected:** healthy worker and real ping before the verification matrix.

**Actual:** the earlier worker state was unhealthy. At closeout, the worker was
healthy and responded to a real ping.

**Impact:** prior verification was incomplete.

**Severity:** Medium.

**Fix:** local runtime recovered; no source change was attributed without
evidence.

**Regression:** complete Docker matrix and Turbo worker ping.

**Status:** resolved in the current local runtime.

### ID: 3E1-F-004

**Title:** Legacy billing DLQ task could log its payload and correlation value.

**Surface:** `billing.tasks.dlq_billing`.

**Expected:** provider payload and correlation data are redacted at the task
boundary even if a legacy task is invoked outside current route paths.

**Actual:** the prior task logged its received payload and correlation argument
directly.

**Impact:** task-level diagnostics could disclose provider or customer-linked
data.

**Severity:** High.

**Fix:** task-boundary financial-payload redaction and hashed correlation logging.

**Regression:** dedicated billing task-redaction test and full API/checkout/
billing partition.

**Status:** fixed and verified locally.

## Changed files

| Area | Files | Change |
| --- | --- | --- |
| Runtime | `users/services.py`, `users/tasks.py`, `users/views.py`, `billing/tasks.py` | HMAC OTP Redis state, encrypted Celery delivery envelope, and task-boundary billing log redaction. |
| Tests | `tests/unit/test_auth.py`, `billing/tests/test_task_redaction.py` | Redis privacy, envelope, tamper, fake-provider, Lua fake-contract, and billing log-redaction coverage. |
| Docs | Redis policy, Phase 3E1 report, WAF policy, security matrix | Redis role, pressure boundary, monitoring, and release gates. |
| Frontend/scripts | none | no change. |

## Remaining follow-up
- GitHub Actions after an approved push.
- Real WAF/CDN deployment, monitoring, emergency rule, and rollback validation.
- Production private-network, TLS, authentication, ACL, and managed-Redis
  configuration.
- Separate Redis instances or enforced resource/ACL separation for Celery and
  admission-control traffic.
- Phase 3J staging restart, slow-response, unavailable, Celery-backlog,
  webhook-preservation, and rollback drills.
- Phase 3F booking/payment concurrency proof; Phase 3G media/CDN hardening;
  Phase 3H staff/session/PII review; and Phase 3I release enforcement.

## Explicit confirmations

No branch, commit, push, or pull request was created. No real provider,
production endpoint, production data, production secret, active scanner, Burp,
DDoS, uncontrolled load, public Redis exposure, permanent automatic IP ban, or
production throttle weakening was used. No raw sensitive data or Redis keys are
recorded in this report. Production readiness is not claimed.
