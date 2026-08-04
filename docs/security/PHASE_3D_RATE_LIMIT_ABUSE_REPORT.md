# Phase 3D Rate-Limit / Abuse Report

> **Current Phase 3X-OBS-RL local status:** Phase 3D is closed with a
> low/medium frontend follow-up. This supersedes the historical blocked status
> below. GitHub CI is unverified until an approved push; production readiness
> remains rejected / not claimed.

Status: **PHASE 3D BLOCKED — TEST MATRIX INCOMPLETE**.

Phase 3X status: **OPEN — SECURITY MATRIX ROOT-CAUSE STABILIZATION REQUIRED**.
Phase 3E must not start.

The pre-patch inventory identified existing Redis STK/OTP throttles, staff-login
cooldown, booking/checkout idempotency, transaction locks, generic denials,
published-only media resolution, and webhook inbox replay protection. It also
identified missing function-view admission controls for high-risk booking,
contact-reveal, polling, and public-read routes. No Phase 3B authorization or
Phase 3C response-privacy regression was established during discovery.

## Closeout

The patch added hashed Redis token-bucket scopes for CSRF bootstrap,
availability, booking hold/checkout, public status, public gallery/media, and
staff contact reveal. Checkout create/detail now use explicit authenticated
user-plus-IP scopes. STK, OTP, staff-login cooldown, capacity locks,
idempotency, and webhook inbox replay controls remain in force.

Verification: 5 new Phase 3D tests passed in 17.99 seconds; 26 directly
affected existing throttle, idempotency, booking-status, checkout, and privacy
tests passed in 38.27 seconds. Tests were bounded and local-only with fake
providers. No active scan, external provider, or production data was used.

Targeted evidence is green, but Phase 3D is not closed: the full
`tests/security` partition exceeded its approved 600-second command budget and
had to be stopped by restarting the local web service. The result is a
test-runner lifecycle/verification timeout, not an observed abuse-control or
privacy failure. Do not proceed to Phase 3E until the remaining required
partitions, hygiene, and operational checks complete.

## Phase 3X-OBS-RL Final Local Evidence

- Fake Redis is scoped to its outage request and restored before mandatory
  direct-Redis cleanup; Docker/CI cleanup fails loudly when Redis is expected.
- High-volume booking-status, checkout-detail, and gallery tests use copied,
  test-only settings and assert production values restore. Runtime values remain
  `booking_status=30/min`, `checkout_detail=60/min`, and `public_gallery=60/min`.
- DRF class-based throttle bodies are now generic. `Retry-After` carries the
  retry delay rather than disclosing the exact token-bucket wait in JSON.
- Final local evidence passed: security 161 tests, load 26 tests, latency 27
  tests, Newman 30 requests/91 assertions, Turbo Pass, static checks, Bandit,
  host Git hygiene, service health, and worker ping.

The remaining product follow-up is a public booking-status SPA caller that
uses the existing frontend `Retry-After` helper. It is not a reason to weaken
backend admission control or to claim production readiness.
