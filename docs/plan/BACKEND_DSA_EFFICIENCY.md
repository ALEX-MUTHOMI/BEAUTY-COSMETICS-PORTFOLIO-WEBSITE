# Backend booking efficiency

**Status:** Living ops contract (production)
**Related:** [CALENDAR_SERVICE_PHASE_3.md](./CALENDAR_SERVICE_PHASE_3.md), [GUEST_MONEY_PATH.md](../ops/GUEST_MONEY_PATH.md), [RELEASE_CHECKLIST.md](../ops/RELEASE_CHECKLIST.md), [BACKEND_QUALITY_AUDIT.md](./BACKEND_QUALITY_AUDIT.md)

## What this is

Rules for keeping the booking hot path fast and honest under load:

- Bound wall-clock time and DB query counts per request
- Avoid N+1 availability round-trips (batch by date window)
- Invalidate Redis calendar capacity when blocking status changes
- Run Celery Beat so holds and unpaid checkouts release capacity

```text
ResolveHandoff → CalendarBuild → RedisCache + BulkCapacity GROUP BY
DaySlots → IntervalMergeSubtract → Hold + ExclusionConstraint
Confirm / HoldExpire / CheckoutExpire→PaymentFailed → CapacityGenBump
```

## SLOs

| Path | p95 wall | Max DB queries (cold) | Gate |
|------|----------|----------------------|------|
| Calendar build | < 2.0s | ≤ 120 | `tests/latency/test_calendar_service_latency.py` |
| Availability (≤14 days) | < 2.0s | ≤ 40 single-day / ≤ 80 fourteen-day | `tests/latency/test_availability_service_latency.py` |
| Hold create | < 2.0s | ≤ 60 | `tests/latency/test_hold_service_latency.py` |

Calendar summary first; slot detail on day tap where the client asks. When the calendar still needs slots for classification, fetch them in **batches**, never one availability call per day.

## Indexes

| Query | Index / constraint |
|-------|--------------------|
| Bulk capacity by date | `bookings_local_date_status_idx` |
| Overlap / busy range | resource start/range indexes + GiST `exclude_booking_resource_overlap` |
| Hold expiry sweep | `status=held` + `hold_expires_at` (Beat limit 500) |

Do not add indexes without `EXPLAIN` evidence under load.

## Cache and invalidation

- Redis calendar payload TTL ≈ 45s (`bookings/services/calendar_cache.py`)
- Capacity generation token per `local_booking_date`; bump forces cache miss
- Bump on: hold create, hold expire, confirm, cancel, payment failed (including checkout expiry), and other blocking transitions via `transition_booking`
- Contract tests: `bookings/tests/test_calendar_capacity_invalidation.py`

## Beat jobs (must run in staging/prod)

| Beat key | Task | Purpose |
|----------|------|---------|
| `sweep-stale-booking-holds` | `bookings.tasks.sweep_stale_holds` | Expire held bookings; bump capacity |
| `sweep-expired-checkout-sessions` | `bookings.tasks.sweep_expired_checkouts` | Expire unpaid checkouts; mark linked `payment_pending` bookings `payment_failed`; bump capacity |

Ops: [RELEASE_CHECKLIST.md](../ops/RELEASE_CHECKLIST.md) §4 and [GUEST_MONEY_PATH.md](../ops/GUEST_MONEY_PATH.md).

## Primary modules

- `bookings/services/booking_calendar.py` — orchestration, bulk capacity, batched slots
- `bookings/services/availability.py` — interval merge/subtract
- `bookings/domain/yield_scheduling.py` — yield / anchors
- `bookings/services/calendar_cache.py` — Redis + capacity gen
- `bookings/services/hold_expiry.py` — hold expiry + capacity bump
- `bookings/services/query_observability.py` — query/latency counters for gates
- `bookings/services/state_machine.py` — FSM + invalidation
- `checkout/services.py` — checkout expiry (frees unpaid booking capacity)

## Desk scale (defer until metrics demand)

Only when staff list/search p95 degrades:

1. Keyset pagination for staff booking lists
2. Prefix / trigram search if HMAC + `icontains` is not enough

Suggested trigger: staff search p95 > 500ms or soft list caps hit regularly.
