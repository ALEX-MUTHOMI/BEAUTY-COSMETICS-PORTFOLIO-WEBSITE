# CASS Frontend Integration — Security

The Nuxt `/book` flow is a **thin client** over CASS. Booking policy (weekdays, capacity, classification) lives on the backend only.

## API flow

```
/book handoff → resolve-handoff → calendar → availability → hold → checkout → status poll
```

| Step | Endpoint | Backend throttle |
|------|----------|------------------|
| Resolve | `GET /api/bookings/catalog/resolve-handoff/` | `catalog_resolve` 60/min |
| Calendar | `GET /api/bookings/calendar/` | `availability` 30/min |
| Day slots | `GET /api/bookings/availability/` | `availability` 30/min (shared) |
| Hold | `POST /api/bookings/holds/` | `booking_hold` 5/min + Turnstile under abuse |
| Checkout | `POST /api/bookings/checkout/` | `booking_checkout` 8/min |
| Status | `GET /api/bookings/status/<id>/` | `booking_status` 30/min |

## OWASP-aligned controls

### Read path — `bookingRequestGovernor.ts`

| Control | Purpose |
|---------|---------|
| Calendar load cooldown (2s) | Blocks handoff/query churn |
| Load token | Drops stale resolve/calendar responses |
| Day-slot min interval (450ms) | Stops rapid day-button spam |
| 12 slot fetches / minute | Session budget under backend 30/min |
| `AbortController` | Cancels superseded availability fetches |
| `credentials: 'omit'` on GETs | No cookies on anonymous catalog reads |

### Write path — `bookingSubmitGovernor.ts` + server gates

| Control | OWASP | Purpose |
|---------|-------|---------|
| Click gate + in-flight lock | API4 | One hold→checkout chain per gesture |
| Stable hold/checkout idempotency | API6 | Survives double-click / retry |
| CSRF + `X-CSRFToken` | API2 | Credentialed POST only |
| **Server Turnstile under abuse** | API6 | `hold_bot_guard` verifies token when circuit ≠ NORMAL |
| Always send `turnstile_token` | API6 | Cannot omit field to skip server gate |
| Honeypot (client UX) | Bot scripts | Rejects form bots; API bots hit server throttles |
| Full slot identity bind | API8 | `startsAt` + resource + service must match daySlots |
| Safe status navigation | A01 | Allowlist `/booking/status/<uuid>/` only — no open redirect |
| Submit `AbortController` | API4 | Cancel hold/checkout on back/unmount |
| Generic errors | API8 | No backend internals in DOM |

**Server throttles + Turnstile under abuse are authoritative.** Client governors reduce accidental abuse; they do not replace Redis/IP throttles.

## Red-team coverage

| Suite | What it proves |
|-------|----------------|
| `bookingBotAbuse.redteam.spec.ts` | Multi-click / calendar spam / honeypot / XSS names |
| `bookingNavigation.spec.ts` | Open-redirect phishing via `status_url` |
| `bookingWriteApi.redteam.spec.ts` | No price mass-assignment; Turnstile always present |
| `tests/security/test_hold_turnstile_abuse_gate.py` | Server rejects holds under abuse without valid Turnstile |

## Phase 3e Option A (locked)

All 23 marketing slugs use **type-level** weekdays only. No per-treatment overrides in production.
