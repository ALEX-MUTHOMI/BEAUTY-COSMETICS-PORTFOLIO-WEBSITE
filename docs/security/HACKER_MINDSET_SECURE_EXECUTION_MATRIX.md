# Hacker-Mindset Secure Execution Matrix

**Status:** Active hardening pass (2026-07-09)  
**Method:** Assume a motivated attacker with browser access, leaked status URLs, forged Origin/Host, webhook spoofing, and staff-session theft. Every control must fail closed under abuse.

**Related:** `ENTERPRISE_CODE_REVIEW_2026_07.md`, `INCIDENT_FAIL_CLOSED_RUNBOOK.md`, senior eval canvas.

---

## Attacker goals (money path)

| Goal | Attack | Fail-closed control |
|------|--------|---------------------|
| Steal a held slot / force STK to victim phone | Guess `checkout_id` UUID + call STK | Guest STK requires CSRF + `booking_public_id` bind + phone HMAC match to booking customer |
| Cascade-skip payment gates | Slow CI / reorder jobs | Already: `payment-security` before load/chaos |
| Forge M-Pesa success | POST fake webhook from random IP | IP allowlist **and** shared-secret header when configured / always in live |
| Tunnel bypass in “prod” | Set `DARAJA_ENV=sandbox` + tunnel host | Tunnel bypass requires sandbox **and** explicit allow flag (or DEBUG) |
| Exhaust holds | Spam holds / never pay | Beat sweeps expire holds + checkouts; throttles + Turnstile |
| Scrape booking PII via status | Bombard status GETs | Runtime throttle 20/min + FE governor |
| Staff contact dump | Stolen staff cookie, skip reauth | Real `postStaffReauth`; contact-access already requires recent reauth server-side |
| SSR staff HTML leak | Hit `/staff/*` without JS | Universal `staff-auth` middleware (not `.client` only) |
| CSRF on staff login | Read Nuxt-origin cookie | Bootstrap token from `/api/csrf/` JSON body |

---

## Execution sequence (this pass)

| # | Workstream | Proof |
|---|------------|-------|
| 1 | Guest-safe STK + `/book` wire | Red-team: wrong booking id / wrong phone → 404/403; happy path → 202 |
| 2 | Celery Beat hold/checkout expiry | Unit + schedule registered; compose beat service |
| 3 | Status UX: pending / failed / retry STK | FE calls STK; status copy + retry without open redirect |
| 4 | Webhook shared secret + tunnel lockdown | Missing/wrong secret → 403 when required; live never tunnel-bypasses |
| 5 | Staff reauth + CSRF origin + SSR middleware | Modal calls API; login uses API CSRF; middleware not client-only |
| 6 | Deep health + prod image without `--with dev` | `/api/health-check/` probes DB/Redis; Dockerfile `INSTALL_DEV` arg |
| 7 | Privacy product (partial) | Keep ticketed rights API; document remaining UX as follow-on |

---

## Explicit non-goals (still not production certification)

- Live Sentry DSN provisioning
- Full prod CD / backup automation
- Daraja cryptographic signature (Safaricom does not sign; shared secret is our edge control)
- Completing staff OAuth callbacks

**Production readiness remains not claimed** until real-money mode boot checks, deploy, and Daraja staging cutover are green.

---

## Implemented in this pass (code)

| Control | Location |
|---------|----------|
| Guest STK (CSRF + booking↔checkout bind + phone HMAC) | `bookings/services/guest_stk.py`, `POST /api/bookings/checkout/mpesa/stk/` |
| `/book` initiates STK after checkout | `frontend/src/booking/useBookCheckout.ts` |
| Status retry STK UX | `frontend/pages/booking/status/[publicId].vue` |
| Webhook shared secret + live require | `checkout/webhook_auth.py`, `IsAuthorizedMpesaWebhook` |
| Tunnel bypass opt-in only | `DARAJA_SANDBOX_ALLOW_TUNNEL_CALLBACKS` |
| Celery Beat hold/checkout expiry | `CELERY_BEAT_SCHEDULE`, `beat` compose service |
| Staff reauth wired | `StaffContactRevealModal.vue` → `postStaffReauth` |
| Staff CSRF from API | `pages/staff/login.vue` → `/api/csrf/` |
| Staff middleware SSR+client | `middleware/staff-auth.ts` |
| Deep readiness | `GET /api/health-check/` probes DB+Redis |
| Prod image without dev deps | `Dockerfile` `INSTALL_DEV` ARG |
| Red-team proofs | `tests/security/test_guest_stk_and_webhook_hardening.py` |
