# Enterprise-Grade Code Review — AestheticOS (2026-07-03)

**Method:** Manual, hacker's-mindset senior-engineer review performed in lieu of CodeRabbit
(CodeRabbit CLI/App setup was blocked by network/auth constraints in the review
environment). Three parallel deep-dive passes (backend, frontend, infrastructure/CI)
were cross-referenced against actual source, then Critical/High findings were verified
line-by-line and fixed where the fix was safely contained and test-verifiable.

**Scope:** Django/DRF backend, Nuxt 3/Vue 3 frontend, Docker/Compose/Caddy/GitHub Actions
infrastructure.

**Verification:** All applied fixes were run against the existing automated test suite
inside the project's own Docker stack. **384 tests passed, 0 failed** across the affected
apps (`users/`, `checkout/`, `bookings/tests/`) after the changes below.

---

## 1. Fixes Applied and Verified

| # | Issue | Severity | File(s) | Fix |
|---|---|---|---|---|
| 1 | `/api/auth/verify-otp/` had **no rate limit** and the OTP was only invalidated on a *correct* guess — an attacker could brute-force the 1,000,000-value 6-digit OTP space within the 5-minute TTL with unlimited attempts. | **Critical** | `users/views.py`, `users/throttles.py`, `core/settings.py`, `users/services.py` | Added `OTPVerifyRateThrottle` (10/min, IP+email scoped) and a server-side attempt counter in `OTPService` that destroys the OTP after 5 wrong guesses. |
| 2 | `verify_turnstile_token()` accepted the literal string `CF_CLEARANCE_TEST_TOKEN` as an **unconditional** bypass of Cloudflare Turnstile bot-mitigation — active in every environment, including a hypothetical production deploy. | **High** | `users/services.py` | Bypass now only works while `TURNSTILE_SECRET_KEY` is still Cloudflare's public test placeholder. Any real deployment configuring a live secret automatically closes the bypass — no extra env flag needed. |
| 3 | Checkout `idempotency_key` is globally unique in the DB but `create_checkout_session`/`initiate_mpesa_stk` used `get_or_create()`/lookup without checking the requesting customer — a colliding or front-run key from a different actor would silently hand back (or "claim") another customer's checkout/attempt instead of failing. | **High** | `checkout/services.py`, `checkout/views.py` | Added an ownership check that raises `CheckoutValidationError` → **409 Conflict** on cross-customer idempotency-key collision, for both session creation and STK initiation. |
| 4 | `BookingCircuitBreaker.mode_for_context()` read abuse counters via `getattr(self.redis, "values", {})` (only works on the test double) using **the wrong key names** (`holds_created` vs the real `holds:created`) — in production this always read 0 and the breaker never left `NORMAL` mode, and the real Redis client was never even passed into the HTTP hold-creation path in the first place. | **Medium** | `bookings/domain/circuit_breaker.py`, `bookings/api/public_views.py`, `bookings/tests/test_booking_hold_abuse_circuit_breaker.py` | Fixed key names to match the actual counters, switched to real `redis.get()`, and wired a real Redis client into `_request_context()` for the public hold-creation endpoint. Updated the test double accordingly. |
| 5 | `nuxt.config.ts` had `devtools: { enabled: true }` unconditionally, and loaded the Cloudflare Turnstile script **twice** (once via the module's `addScript: true`, once via a manual `<script>` tag). | Low / Nit | `frontend/nuxt.config.ts` | DevTools now gated on `NODE_ENV !== 'production'`; removed the duplicate script tag. |

All five fixes were verified against the existing test suite (see below) plus, where the
existing suite didn't already cover the exact regression, an updated/extended test.

### Verification runs
```
users/, checkout/, tests/security/test_rate_limit_route_controls.py, tests/unit/test_auth.py,
tests/security/test_red_team_auth.py                              → 25 passed
checkout/ + users/ + circuit-breaker test                          → 68 passed
bookings/tests/ (full suite)                                       → 291 passed
```

---

## 2. Findings Requiring an Explicit Decision (Not Auto-Fixed)

These are real, verified findings, but fixing them safely requires an operational/product
decision, coordination with the Daraja/M-Pesa configuration, or infrastructure changes I
can't fully validate without a live deploy — so they were **not** silently changed. Ranked
by priority:

1. **M-Pesa webhook trusts source IP only, no shared secret / signature** (`checkout/views.py`,
   `checkout/permissions.py`). Daraja doesn't sign callbacks; add a high-entropy shared
   secret header validated before processing, in addition to the IP allowlist.
2. **`SAFARICOM_ALLOWED_CIDRS` defaults are unsafe behind a reverse proxy** — `core/settings.py`
   defaults include `127.0.0.1/32`, and `docker-compose.yml`/`.env.example` include
   `172.16.0.0/12`. Combined with `TRUSTED_PROXY_CIDRS` being empty by default, this is a
   **paradox**: fixing "webhook returns 403 behind Caddy" by widening the CIDR list
   (as the current defaults do) defeats IP allowlisting entirely. Needs: explicit
   `TRUSTED_PROXY_CIDRS` set to the real proxy hop, `X-Forwarded-For` set correctly in
   `Caddyfile.staging`, and removal of private/loopback ranges from the CIDR allowlist —
   ideally enforced by a Django deploy-check that fails startup if `DEBUG=False` and the
   allowlist still contains a private range with no trusted proxy configured. This needs a
   coordinated change across `core/settings.py`, `Caddyfile.staging`, `docker-compose*.yml`,
   and CI env — flagging for your review rather than guessing at production topology.
3. **Sandbox tunnel callback bypass** (`checkout/permissions.py`) disables the IP allowlist
   entirely for `DARAJA_ENV=sandbox`, gated only by the tunnel hostname matching config —
   should be restricted to `DEBUG=True` or an explicit unsafe-tunnel flag, and must never be
   deployed with `DARAJA_ENV=sandbox` in production.
4. **Staff OAuth (Google/Apple) has start endpoints but no `/callback/` routes** — either
   finish the implementation (state validation, PKCE, nonce, staff allowlist) or remove the
   start endpoints until ready; the existing tests reference callback URIs that would 404.
5. **Remember-device issuance has no proof of ownership** — anyone holding a booking's
   public UUID (e.g. from a status-check link) can mint a long-lived `bc_remember_device`
   cookie bound to that customer's contact info. Should require a fresh OTP/action-session
   before issuance.
6. **Weak defaults for `SECRET_KEY`/`PII_ENCRYPTION_KEY`/`PII_HASH_PEPPER`/`TURNSTILE_SECRET_KEY`**
   are only validated lazily; a misconfigured deploy with `DEBUG=False` could boot silently.
   Recommend a `django.core.checks` deploy-only check, but this requires updating
   `scripts/ci/django_smoke.sh` and `.github/workflows/ci.yml` env in lockstep — flagging
   rather than risking breaking the green pipeline blind.
7. **Frontend: client-only staff route guard** (`middleware/staff-auth.client.ts`) — Nuxt SSR
   renders staff page HTML before the client-only middleware runs; a direct/no-JS request
   bypasses it. Needs a server-side (`.ts`, not `.client.ts`) middleware validating the
   session cookie during SSR.
8. **Frontend: Django CSRF bootstrap is read from the wrong origin's cookie** —
   `login.vue` reads `useCookie('csrftoken')` on the Nuxt origin, but Django's `csrftoken`
   cookie is scoped to the API origin (`localhost:8000` vs `localhost:3000` by default).
   Should fetch `/api/csrf/` and use the JSON body's `csrf_token`.
9. **Frontend: staff "contact reveal" modal is a UI stub** — it never calls the real
   `postStaffReauth()` endpoint; any staff session holder currently sees a fake "Confirmed"
   after ~120ms. This is pre-launch scaffolding, not a live bypass, but must not ship as-is.
10. **Infra: production image includes dev/test tooling** (`Dockerfile` installs
    `--with dev`), **bind-mounts source read-write** in compose, and **ships hardcoded
    fallback secrets** (`SECRET_KEY`, `POSTGRES_PASSWORD`, `REDIS_PASSWORD`) if `.env` is
    absent. All three should be addressed before any real production cutover.
11. **Infra: no Postgres backup automation, no Redis persistence volume, shallow `/health/`
    check with no DB/Redis readiness probe.** The project's own docs already state
    "production readiness: rejected / not claimed" — this review confirms that's accurate.

---

## 3. Full Findings Reference (by severity)

The three detailed sub-reports (backend, frontend, infrastructure) are summarized here by
count; ping me if you want the full unabridged findings re-expanded into this file.

| Area | Critical | High | Medium | Low | Nit |
|---|---|---|---|---|---|
| Backend (auth/payments/bookings) | 2 | 6 | 8 | 5 | 6 |
| Frontend (Nuxt/Vue) | 3 | 6 | 8 | 5 | 5 |
| Infrastructure/CI | 2 | 7 | 11 | 7 | 3 |

**What's already well hardened** (confirmed, not re-litigated): checkout object-level
authorization, Postgres exclusion constraints preventing double-booking, webhook
idempotency via `MpesaWebhookInbox`, PII hashing/redaction across logs, Redis-backed
fail-closed throttling, mass-assignment protection (see
`docs/security/MASS_ASSIGNMENT_MATRIX.md`), gallery upload path-traversal defenses, and an
extensive existing red-team test suite (`tests/security/`). GitHub Actions CI/CD is already
hardened against the OWASP CI/CD Top 10 per
`docs/security/OWASP_CICD_AUDIT_AND_INFRA_CHECKLIST.md`.

---

## 4. Recommended Next Steps (priority order)

1. Decide on the M-Pesa webhook shared-secret design (item 2.1) — this is the single
   highest-impact remaining gap since it's the payment trust boundary.
2. Fix the CIDR/reverse-proxy trust chain (item 2.2) before any staging/production Daraja
   cutover — currently payments would either be forgeable or entirely non-functional
   behind Caddy, depending on which way the CIDR list is "fixed" operationally.
3. Finish or remove staff OAuth (item 2.4) and wire the contact-reveal modal to the real
   reauth endpoint (item 2.9) before those staff features ship.
4. Convert the frontend staff-auth middleware to a server-side guard (item 2.7) and fix the
   CSRF cookie origin mismatch (item 2.8) — both are pre-launch blockers for the staff
   portal specifically, not the currently-deployed public site.
5. Schedule the infra hardening pass (item 2.10/2.11) as its own workstream before a real
   production deployment; none of it is exploitable today because nothing is in production
   yet, per the project's own documented status.
