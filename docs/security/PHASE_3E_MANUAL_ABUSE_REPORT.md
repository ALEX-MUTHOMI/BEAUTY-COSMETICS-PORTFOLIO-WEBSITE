# Phase 3E Manual Abuse Testing Report

## Scope and safety boundary

This report records bounded manual abuse testing against the local Docker stack.
No production endpoint, production data, real payment provider, real OTP/email/SMS
provider, external object store, active scanner, or uncontrolled load test was
used. Identifiers, account details, request payloads, and correlation values are
intentionally omitted.

## Manual probe results

| Area | Controlled probe | Result | Evidence |
| --- | --- | --- | --- |
| Request correlation | Sent a client-controlled correlation header to the local health endpoint. | Passed: the response was successful and did not reflect the supplied value. | Server-generated correlation handling was observed. |
| Public gallery | Requested the local public homepage gallery endpoint. | Passed: normal public admission returned 200. | Public read path remained available. |
| Booking status | Requested a malformed public booking-status reference. | Passed: generic 404 response. | No object-existence disclosure through the response. |
| Media resolver | Requested a raw media-like path. | Passed: generic 404 response. | Raw storage-shaped path was not served. |
| Abuse state hygiene | Removed state created by the two malformed probes. | Passed: four local Redis throttle/abuse records were removed. | The manual probes did not contaminate later test evidence. |
| OTP fake-provider path | Exercised the fake-provider task path and its Redis throttle test double. | Passed after remediation. | Six focused authentication tests passed. |

The direct probes above complement the automated authorization, throttling,
checkout, staff, and privacy suites listed in the verification matrix. They are
not a production penetration test and do not assert an external WAF/CDN
deployment.

## Findings and remediation

### 3E-F-001 — stale OTP Redis test double caused a false fail-closed result

**Severity:** Medium (test and local operational reliability)

The OTP unit-test Redis double implemented an earlier script contract. The
current token-bucket script uses the three-key abuse-aware contract, so a normal
fake OTP request was interpreted as an infrastructure failure and returned a
generic 503. This hid valid behavior behind a test-environment error.

**Remediation:** updated the double to model the current token-bucket interface
and added regression coverage for the normal fake-provider flow.

**Verification:** focused authentication suite passed: 6 tests. The broader
OTP, booking, staff, authorization, and security partitions passed after the
fix.

### 3E-F-002 — fake OTP dispatch could attempt SMTP delivery

**Severity:** Medium (local performance and isolation)

When the configured email provider was `fake`, the OTP task still reached the
SMTP send path. In a local or CI environment this could wait on unavailable
network infrastructure, consume worker capacity, and violate the intended
no-external-provider test boundary.

**Remediation:** the task now accepts fake-provider dispatch locally after
redacted logging and returns before composing or sending email. A regression
test asserts that the mail sender is never called in fake mode.

**Verification:** the focused authentication suite and all listed regression
partitions passed. The production provider path was not changed by this branch.

## Regression and operational verification

| Verification | Result |
| --- | --- |
| Focused authentication tests | 6 passed |
| OTP, booking, staff, authorization, and related security checks | 28 passed |
| Full security partitions | 167 passed |
| API, checkout, and billing suite | 94 passed |
| Load suite | 26 passed |
| Latency suite | 27 passed |
| Newman local collection | 30 requests, 91 assertions passed |
| Frontend type-check and build | Passed |
| Turbo pass | Passed |
| Full formatting/static gate (Black, isort, Ruff, fatal flake8) | Passed |
| Configured Bandit medium/high gate | Passed |
| Host Git and filesystem secret hygiene | Passed; no secret markers detected |
| Docker health and Celery ping | Passed |
| Runtime diagnostics | Disabled; no throttle, OTP, or abuse keys remained after cleanup |
| Recent runtime logs | No traceback, internal-server-error, or Redis-unavailable entries in the checked window |

## Residual risk and follow-up

- This is local Docker evidence only. GitHub Actions and production runtime
  behavior remain unverified in this phase.
- The configured Bandit gate is clean at medium/high severity. Existing
  repository-wide low-severity baseline items remain a separately tracked
  cleanup concern and are not represented as a clean raw-low baseline.
- The WAF/CDN policy is an operator handoff, not a claim that an edge deployment
  has been completed.
- No real payment, email, SMS, storage, or production data was contacted.

## Phase decision

**PHASE 3E ACCEPTED — MANUAL ABUSE TESTING PASSED WITH FOLLOW-UP.**

The two confirmed local OTP reliability/isolation defects were fixed and
regression-tested. Normal booking-facing public admission remained available
while malformed booking and raw-media probes failed generically. This decision
does not certify production readiness.
