# CASS Frontend Integration — Security

The Nuxt `/book` flow is a **thin client** over CASS. Booking policy (weekdays, capacity, classification) lives on the backend only.

## API flow

```
/book handoff → resolve-handoff → calendar → availability → hold → checkout → status poll
```

| Step | Endpoint | Backend throttle |
|------|----------|------------------|
| Resolve | `GET /api/bookings/catalog/resolve-handoff/` | `catalog_resolve` 15/min |
| Calendar | `GET /api/bookings/calendar/` | `availability` 30/min |
| Day slots | `GET /api/bookings/availability/` | `availability` 30/min (shared) |
| Hold | `POST /api/bookings/holds/` | `booking_hold` 5/min |
| Checkout | `POST /api/bookings/checkout/` | `booking_checkout` 8/min |
| Status | `GET /api/bookings/status/<id>/` | `booking_status` 30/min |

## Client-side defense in depth

### Read path — `bookingRequestGovernor.ts`

| Control | Purpose |
|---------|---------|
| Calendar load cooldown (2s) | Blocks handoff/query churn from re-firing resolve+calendar |
| Load token | Drops stale resolve/calendar responses after newer handoff |
| Day-slot min interval (450ms) | Stops rapid day-button spam |
| 12 slot fetches / minute cap | Session-local budget under backend 30/min |
| `AbortController` | Cancels superseded availability fetches (wrong-day race) |
| Calendar interaction lock | Disables other days while slots load |
| HTTP 429 handling | Generic user message, no internals |

### Write path — `bookingSubmitGovernor.ts` + `useBookCheckout.ts`

| Control | OWASP alignment | Purpose |
|---------|-----------------|---------|
| Click gate (1.2s) | API4 Unrestricted Resource Consumption | One hold/checkout chain per user gesture |
| In-flight submit lock | — | Prevents double-submit race from multi-click |
| Stable hold idempotency key | API6 Unrestricted Access / replay | Same key on accidental double-click |
| Stable checkout idempotency key | API6 | Safe retry after network blip |
| 3 holds / min, 2 checkouts / min | API4 | Client budget under server 5/min and 8/min |
| CSRF bootstrap + `X-CSRFToken` | API2 Broken Auth | Credentialed POST with Django token |
| Turnstile on details step | API6 Bot abuse | Human verification before hold |
| Abuse mode on 429 / short TTL | Circuit breaker mirror | Tightens UX when backend signals pressure |
| Honeypot field | Bot scripts | Silent reject if hidden field filled |
| Customer input validation | API8 Integrity | No raw user strings without normalization |
| `textGuards` sanitization | XSS | Strip control chars from API copy |
| Status poll backoff | API4 | 2s → 15s cap, honors `Retry-After` |
| Generic error messages | API8 | No backend internals in DOM |

**Server throttles remain authoritative.** Client limits protect UX and reduce accidental abuse; they do not replace Redis/IP throttles.

## Phase 3e Option A (locked)

All 23 marketing slugs use **type-level** weekdays only. No per-treatment overrides in production.

## Key modules

| Module | Role |
|--------|------|
| `useBookFlow.ts` | Calendar read orchestration |
| `useBookCheckout.ts` | Hold → checkout submit orchestration |
| `bookingWriteApi.ts` | Typed POST/GET parsers for hold, checkout, status |
| `bookingCsrf.ts` | Django CSRF cookie bootstrap |
| `bookingIdempotency.ts` | Stable idempotency key builders |
| `bookingCustomer.ts` | Client validation + honeypot |
| `bookingStatusPoll.ts` | Post-checkout status polling with backoff |
| `pages/booking/status/[publicId].vue` | Customer status surface |
