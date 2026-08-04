# CI Test Matrix

The canonical verification strategy is a partitioned matrix. The monolithic
`pytest -q` command is useful for local debugging but is not the primary CI gate
because it can exceed Docker Desktop runtime limits and leave stale test DB
connections when interrupted.

## Lane Overview

| Lane | Purpose | Command |
| --- | --- | --- |
| Turbo Pass | Fast local/CI preflight for common regressions | `.\scripts\ci\turbo_pass.ps1` |
| Standard Backend | Full domain partitions without load/ZAP | `.\scripts\ci\run_ci_matrix.ps1` |
| Performance | Load and latency with explicit budgets | `.\scripts\ci\run_performance_gate.ps1 -Mode standard` |
| Passive Security | Bounded ZAP health/root/OpenAPI/Newman passive scans | `.\scripts\ci\run_security_passive_gate.ps1 -Mode all-passive` |
| CASS certification | Calendar-as-a-service sign-off bundle | GitHub jobs `cass-calendar-service`, `bookings-unit`, `newman-acceptance`, `zap-passive-newman`, `cass-certification` |
| Deep/Nightly | Future slow dependency/deep load/security expansion | scheduled CI only |

## GitHub Actions — CASS / Bookings gates (production pipeline)

| Job | Partition | Reports artifact |
| --- | --- | --- |
| `bookings-unit` | `bookings/tests` (~290 domain tests) | `reports/ci/junit/bookings.xml` |
| `cass-calendar-service` | Marketing contract, Option A policy, calendar API/policy/latency/security | `reports/ci/junit/cass-calendar.xml` |
| `tests-api-unit` | `tests/api` + `tests/unit` | `reports/ci/junit/api-unit.xml` |
| `newman-acceptance` | Full acceptance incl. folder `06 Calendar and Handoff` | `reports/ci/newman/newman-local.json` |
| `zap-passive-newman` | ZAP passive scan through Newman traffic | `reports/security/zap/` |
| `cass-certification` | Aggregated markdown sign-off when all CASS jobs green | `reports/ci/cass-certification.md` |

## Canonical Gates

Run these as independent CI jobs or clearly separated local gates:

1. `docker compose config -q`
2. `docker compose -f docker-compose.yml -f docker-compose.security-scan.yml config -q`
3. `docker compose exec web poetry run python manage.py check`
4. `docker compose exec web poetry run python manage.py makemigrations --check --dry-run`
5. `docker compose exec web poetry run pytest --collect-only -q`
6. `docker compose exec web poetry run pytest tests/unit -q`
7. `docker compose exec web poetry run pytest tests/api -q`
8. `docker compose exec web poetry run pytest tests/security -q`
9. `docker compose exec web poetry run pytest tests/integration -q`
10. `docker compose exec web poetry run pytest bookings/tests -q`
11. `docker compose exec web poetry run pytest checkout/tests billing/tests -q`
12. `docker compose exec web poetry run pytest tests/load -q --durations=25`
13. `docker compose exec web poetry run pytest tests/latency -q --durations=25`
14. Docker Newman acceptance via `scripts/ci/run_newman_docker.ps1`.
15. ZAP passive health/root/OpenAPI/Newman scans through `scripts/ci/run_security_passive_gate.ps1 -Mode all-passive`.
16. `black --check .`
17. `isort --check-only .`
18. `ruff check .`
19. fatal-syntax `flake8`
20. `bandit`
21. `scripts/ci/secret_hygiene.py`

## Runtime Policy

Load and latency tests are intentionally separate from fast unit/API/security
gates. They are part of release confidence but should not starve faster jobs.
The standard performance lane runs them sequentially. Combined load+latency is
not canonical because it can exceed local command budgets and obscure which
partition caused a timeout.

## Monolithic Pytest Policy

`pytest -q` remains best-effort/debug. If it times out, do not weaken tests or
increase timeouts indefinitely. Use the partitioned matrix and inspect slow
partitions.

## Booking Partition Runtime

`bookings/tests` is currently a canonical full domain partition, not a skipped
or reduced lane. Phase 3B-F re-ran it with durations and maxfail diagnostics:

```powershell
docker compose exec -T web poetry run pytest bookings/tests -q --durations=50 --maxfail=1
```

Result: 290 tests passed in 612.30s. If a future local machine times this lane
out, split by the existing file groups for diagnosis only, then preserve the
full Booking partition in CI unless a documented CI budget decision replaces it
with a no-omission subpartition matrix.

## Failure Handling

If a partition fails, fix that partition and rerun dependent gates. If an
interrupted run leaves `test_aesthetic_os_db` stale, use
`docs/testing/TEST_DB_LIFECYCLE.md`.

Generated reports are ignored by Git and may be uploaded as CI artifacts when
safe. Default CI must not call real Daraja, real email providers, production R2,
active ZAP, Burp, or real DDoS tooling.

## Authorization Security Gate

Phase 3B/3B-C authorization tests live in `tests/security` and are part of both
Turbo Pass and the standard `tests/api tests/security` matrix. The gate covers:

- customer-to-customer BOLA/IDOR;
- anonymous protected-object access;
- staff/non-staff/inactive-staff boundaries;
- mass assignment of owner/role/status/payment fields;
- role/header/query tampering;
- disabled legacy billing route behavior;
- public/private gallery query widening;
- deny-by-default for unknown sensitive routes.

No route that accepts object IDs, tokens, owner-like fields, role-like fields,
status-like fields, or payment-like fields may be added without updating the
authorization matrix and tests.

## Response Privacy Security Gate

Phase 3C response privacy tests also live in `tests/security` and are covered by
Turbo Pass plus the standard `tests/api tests/security` matrix. The gate covers:

- booking hold, checkout bridge, and status token response minimization;
- checkout, billing, webhook, and disabled legacy billing non-reflection;
- staff booking, staff payment, and audited contact reveal response contracts;
- public/staff gallery response privacy and opaque public media URLs;
- malformed, denied, disabled, and unknown-route error response non-leakage;
- route-aware sensitive field allowlist/denylist helpers.

No public/customer/staff/provider route should be added without updating:

- `docs/security/RESPONSE_PRIVACY_MATRIX.md`
- `docs/security/API_FIELD_ALLOWLIST_MATRIX.md`
- `docs/security/SENSITIVE_FIELD_DENYLIST.md`
- relevant response privacy tests in `tests/security/`

## Phase 3C-Final-E Closeout Snapshot

Current-session local evidence (2026-06-20): the standalone `all-passive` gate
completed in 502 seconds with `FAIL-NEW=0`, zero sensitive marker hits,
non-empty health/root/API/Newman reports, scanner cleanup, and a
Newman-through-ZAP result of 30 requests, 91 assertions, and 0 failures.

Immediately preceding closeout-sequence evidence: Turbo Pass completed in 699
seconds; frontend strict type-check and production build passed; partitioned
security/API, booking, checkout/billing, and unit/integration checks passed;
payment-load and latency passed in their bounded lanes. These are separate lane
results, not a monolithic `pytest -q` claim.

## Phase 3D Abuse Controls

`tests/security/test_rate_limit_route_controls.py` is a deterministic Redis
admission-control lane. It uses test-only one-per-minute scope overrides,
bounded requests, and clears only the tested throttle scope. It covers generic
throttle privacy, actor isolation, malformed booking pressure, public
gallery/media enumeration pressure, staff contact reveal pressure, and explicit
checkout route scopes.

Checkout detail additionally verifies a generic DRF `429` body with
`Retry-After`, actor isolation, and restoration of the production `60/min`
setting after its test-only override. Synthetic 100/1,000-read durability tests
must never raise runtime rates; their copied test-local settings are documented
in `docs/security/THROTTLE_POLICY.md`.

## Phase 3D-PLUS Abuse Escalation Controls

`tests/security/test_abuse_escalation.py` verifies invalid booking and checkout
enumeration scoring, generic `429`/`Retry-After`, ignored-retry escalation,
expiry, redacted hashed keys/events, and authenticated actor isolation on a
shared source IP. `tests/security/test_abuse_signal_routes.py` verifies staff
contact probing, raw non-public media-path classification, rejected webhook
source classification, and generic fail-closed booking-hold behavior when the
throttle Redis client is unavailable.

These are bounded Docker tests. They do not call providers, exercise a real
WAF/CDN, generate uncontrolled load, or prove a production Redis/Celery drill.
