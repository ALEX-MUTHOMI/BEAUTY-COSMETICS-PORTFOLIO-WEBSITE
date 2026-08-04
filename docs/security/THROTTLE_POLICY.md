# Throttle Policy

Phase 3D uses Redis-backed token buckets. Redis failure is fail-closed with a
generic `503`; a throttle refusal is a generic `429` with `Retry-After` when a
wait can be calculated. Raw IPs, users, tokens, and handles are never stored in
the throttle-key suffix.

Phase 3D-PLUS adds a route-scoped, TTL-bound abuse score and temporary action
key. A normal request remains one atomic Redis admission decision; only denied
or suspicious requests affect the abuse score. See
`ABUSE_ESCALATION_POLICY.md`, `IP_BAN_POLICY.md`, and `BOT_RETRY_POLICY.md`.

DRF class-based throttles use `core.exceptions.api_exception_handler` so their
response body follows the same generic contract as function-view throttles:
the numeric retry window is carried only in `Retry-After`, never reflected in
the JSON detail.

- Global DRF: anonymous `100/day`, authenticated `1000/day`.
- OTP: IP plus normalized email, `otp_request` (`5/min`).
- Staff login: IP plus email cooldown after five failures in ten minutes.
- STK: authenticated user plus IP, `checkout_stk_push` (`3/min`); legacy fake
  STK uses the existing `stk_push` scope.
- Booking hold/checkout, status polling, availability, catalog resolve, CSRF,
  gallery/media, and contact reveal use explicit route scopes rather than global limits.
- Webhooks intentionally use provider-IP admission plus inbox/event
  idempotency, not a client rate limit that could drop valid payment callbacks.

Local tests override only the affected scope with low deterministic rates and
clear Redis throttle keys between cases. Production tuning remains a later
operational decision; limits must not be increased merely to satisfy tests.

## Phase 3X-RL-CI Runtime And Test Audit

| File | Change type | Scope/rate | Runtime or test-only | Route affected | Risk | Status |
| --- | --- | --- | --- | --- | --- |
| `core/settings.py` | default policy | `catalog_resolve=60/min` | Runtime | handoff/catalog resolve | slug enumeration | active |
| `core/settings.py` | default policy | `booking_status=30/min` | Runtime | public booking status | polling/enumeration | unchanged |
| `core/settings.py` | default policy | `booking_hold=5/min`, `booking_checkout=8/min` | Runtime | public writes | capacity/checkout pressure | active |
| `core/settings.py` | default policy | checkout create `10/min`, detail `60/min`, STK `3/min` | Runtime | customer checkout | payment pressure | active |
| `core/settings.py` | default policy | contact reveal `6/min` | Runtime | staff PII reveal | repeated contact access | active |
| `core/throttling.py` | token bucket | hashed scope and actor key; TTL `period*2` | Runtime | custom scopes | raw-key exposure/collision | active |
| `core/throttling.py` | failure response | generic fail-closed `503` | Runtime | custom scopes | Redis outage | active |
| status endpoint security tests | durability override | `booking_status=200/min` | Test-only context | two 100-read polling tests | global policy mutation | isolated |
| load gallery pressure test | durability override | `public_gallery=200/min` | Test-only context | 100 capped gallery reads | production scrape limit mutation | isolated |
| load status pressure test | durability override | `booking_status=1200/min` | Test-only context | 1,000 read-only status polls | production polling limit mutation | isolated |
| latency checkout-detail pressure test | durability override | `checkout_detail=1200/min` | Test-only context | 1,000 owner-scoped checkout reads | production polling limit mutation | isolated |
| status endpoint security test | enforcement | `booking_status=1/min` | Test-only context | threshold-plus-one poll | missing throttle evidence | covered |
| checkout-detail route-control test | enforcement | `checkout_detail=1/min` | Test-only context | threshold-plus-one owner poll | missing customer-scope evidence | covered |
| `conftest.py` | cleanup | `throttle:*`, `abuse:*`, `otp:*` | Test runtime | direct Redis test state | cross-test pollution | fail-loud in Docker/CI |

The `200/min` value is not a production setting. Each test deep-copies
`REST_FRAMEWORK`, applies it through `override_settings`, and asserts the normal
`30/min` rate is restored. The separate `1/min` test proves generic `429`,
`Retry-After`, actor isolation, and no sensitive response fields.

The Redis-outage test now uses a scoped `monkeypatch.context()`. The broken
client is restored before the autouse Redis cleanup runs, so both setup and
teardown continue to clean real Redis state. There is no cleanup exemption.

## Booking SPA policy and load-test classification

| Route or test | Classification | Legitimate user behaviour | Abuse control | Current user-facing risk |
| --- | --- | --- | --- | --- |
| Booking status (`30/min` per anonymous actor/IP) | Type A, interactive read | A payment UI should poll at its existing five-second cadence and stop on a terminal result. | Bound polling and UUID-guessing attempts; generic `429` includes `Retry-After`. | Multiple booking tabs or customers behind one NAT can contend for the same IP budget; this needs production telemetry before changing the policy. |
| Public gallery (`60/min` per anonymous actor/IP) | Type A, interactive read | A page view normally makes one listing request; media delivery has a separate scope and caching. | Limits automated scrape loops without exposing storage paths. | Shared-IP traffic and aggressive refresh extensions can receive a retryable `429`. |
| `test_customer_status_polling_pressure` (1,000 reads) | Type B, synthetic durability | Not normal SPA behaviour; it proves the endpoint remains read-only under a controlled test-only `1200/min` allowance. | Production stays at `30/min`; the normal threshold-plus-one test proves enforcement. | None: the override cannot alter runtime settings. |
| `test_gallery_public_output_pressure` (100 reads) | Type B, synthetic durability | Not normal gallery use; it proves response caps and serialization stability under a controlled test-only `200/min` allowance. | Production stays at `60/min`; dedicated route-control tests prove enforcement. | None: the override cannot alter runtime settings. |
| `test_status_polling_pressure_is_customer_scoped_and_stable` (1,000 reads) | Type B, synthetic durability | Not normal checkout polling; it proves owner scoping and read stability under a controlled test-only `1200/min` allowance. | Production checkout detail stays at `60/min`; a separate threshold-plus-one test proves generic `429`, `Retry-After`, and actor isolation. | None: the override cannot alter runtime settings. |
| Throttle or Redis rejection | Type C, recovery contract | Clients must respect `Retry-After`; checkout/status UI must render a retry state, not spin or submit a duplicate action. | Generic `429` prevents budget bypass detail; generic `503` fails closed during Redis loss. | A user sees a retryable delay rather than an ambiguous failure or duplicate payment attempt. |

Do not raise production rates to satisfy a Type B test. Any production-rate
change requires a measured decision using redacted diagnostic aggregates:
route, scope, status family, latency, retry hint, and actor category only.

The shared checkout-resilience helper now consumes a numeric `Retry-After`
header and never converts malformed input into an immediate retry. The current
repository has no public booking-status page or API client that invokes this
helper; integrating it into that future UI is an explicit delivery requirement,
not a claim of completed customer-flow wiring.
