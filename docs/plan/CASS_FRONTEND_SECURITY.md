# CASS Frontend Integration — Security

The Nuxt `/book` flow is a **thin client** over CASS. Booking policy (weekdays, capacity, classification) lives on the backend only.

## API flow

```
/book handoff → resolve-handoff → calendar → availability (per day tap)
```

| Step | Endpoint | Backend throttle |
|------|----------|------------------|
| Resolve | `GET /api/bookings/catalog/resolve-handoff/` | `catalog_resolve` 15/min |
| Calendar | `GET /api/bookings/calendar/` | `availability` 30/min |
| Day slots | `GET /api/bookings/availability/` | `availability` 30/min (shared) |

## Client-side defense in depth

`frontend/src/booking/bookingRequestGovernor.ts` reduces click/bot exhaustion before requests reach Django:

| Control | Purpose |
|---------|---------|
| Calendar load cooldown (2s) | Blocks handoff/query churn from re-firing resolve+calendar |
| Load token | Drops stale resolve/calendar responses after newer handoff |
| Day-slot min interval (450ms) | Stops rapid day-button spam |
| 12 slot fetches / minute cap | Session-local budget under backend 30/min |
| `AbortController` | Cancels superseded availability fetches (wrong-day race) |
| Calendar interaction lock | Disables other days while slots load |
| HTTP 429 handling | Generic user message, no internals |

**Server throttles remain authoritative.** Client limits protect UX and reduce accidental abuse; they do not replace Redis/IP throttles.

## Phase 3e Option A (locked)

All 23 marketing slugs use **type-level** weekdays only. No per-treatment overrides in production.

## Not yet wired (hold → checkout)

When holds are connected, also require:

- Stable `idempotency_key` per hold attempt
- Disable Continue on submit
- Turnstile before hold under abuse (backend circuit breaker exists)
- CSRF via `credentials: 'include'` + `nuxt-csurf`
