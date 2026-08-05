# Backend DSA Efficiency (Booking App)

**Status:** Living contract (production efficiency — not interview prep)
**Related:** [CALENDAR_SERVICE_PHASE_3.md](./CALENDAR_SERVICE_PHASE_3.md), [BOOKING_APP_PRODUCTION_BLUEPRINT.md](../BOOKING_APP_PRODUCTION_BLUEPRINT.md), [GUEST_MONEY_PATH.md](../ops/GUEST_MONEY_PATH.md), [RELEASE_CHECKLIST.md](../ops/RELEASE_CHECKLIST.md)

## Principle

Efficiency means: **bounded CPU per request**, **O(1)/O(log n) DB seeks via indexes**, **constant round-trips (no N+1)**, **cheap invalidation**, and **admission control under abuse**.

Scope: `bookings/` hot path (resolve → calendar → availability → hold) plus checkout confirmation signals and Celery outbox that free capacity.

```text
ResolveHandoff → CalendarBuild → RedisCache + BulkCapacityGROUPBY
DaySlots → IntervalMergeSubtract → Hold + ExclusionConstraint
CheckoutConfirm / HoldExpire → CapacityGenBump
```

---

## 20-concept map

| # | Concept | Decision | Backend action / module |
|---|---------|----------|-------------------------|
| 01 | Asymptotics / RAM | HARDEN | SLOs below; `duration_ms` + `query_count` on hot paths |
| 02 | Arrays / dynamic arrays | KEEP | 8 offered days; ≤14 availability range days |
| 03 | Linked lists | SKIP | Redis/PG own durability |
| 04 | Stacks | SKIP | No undo ADT on booking path |
| 05 | Queues / deques | HARDEN | Celery Beat hold/checkout expiry; outbox drain |
| 06 | Hash tables | HARDEN | Redis cache keys, FSM maps, HMAC lookup hashes |
| 07 | Bits | SKIP | Not a booking bottleneck |
| 08 | Recursion | HARDEN | Iterative interval/time walks only |
| 09 | Binary search | SKIP | Day-scale linear free-window scan is enough |
| 10 | Sorting | KEEP | Sort-before-merge in `bookings/services/availability.py` |
| 11 | Binary trees | SKIP | Unused |
| 12 | BSTs / ordered indexes | HARDEN | Postgres B-tree + GiST exclusion; see indexes |
| 13 | Heaps | SKIP | Urgent flag is policy, not heap scheduler |
| 14 | Tries | SKIP / defer | Staff search stays HMAC/`icontains` until volume forces upgrade |
| 15 | Union-Find | SKIP | No connectivity problem |
| 16 | BFS/DFS graphs | KEEP lite | Booking/checkout FSM adjacency maps only |
| 17 | Shortest paths | SKIP | No routing product |
| 18 | Greedy | KEEP | Interval packing + yield floor-division |
| 19 | DP | SKIP | Capacity is closed-form |
| 20 | D&C + systems | HARDEN | Batching, cache, indexes, throttle, Beat |

### Explicit non-goals

Union-Find, Dijkstra/Floyd, classic DP tables, tries-as-router, in-memory heaps for scheduling, Python BST-of-intervals (Postgres + sorted arrays win).

---

## SLOs (Concept 01 / 20)

| Endpoint / path | p95 wall clock | Max DB queries (cold, default window) | Gate |
|-----------------|----------------|----------------------------------------|------|
| Calendar build (`BookingCalendarService`) | < 2.0s | ≤ 120 | `tests/latency/test_calendar_service_latency.py` |
| Calendar HTTP `GET /api/bookings/calendar/` | < 2.0s | (same service) | same + API test |
| Availability (≤14 days) | < 2.0s | ≤ 40 for single-day / ≤ 80 for 14-day | `tests/latency/test_availability_service_latency.py` |
| Hold create | < 2.0s | ≤ 60 | `tests/latency/test_hold_service_latency.py` |

Distinguish **CPU Big-O** (interval merge) from **round-trip Big-O** (one bulk `GROUP BY`, batched availability windows, Redis get/setex).

Two-phase API remains mandatory: calendar summary first; slots on day tap where the client requests them (Phase 3 G6). Default calendar may still compute slots for non-full offered days for classification — those calls must be **batched**, never one availability round-trip per day.

---

## Indexes (Concept 12)

| Query shape | Index / constraint | Status |
|-------------|-------------------|--------|
| Bulk capacity by date | `bookings_local_date_status_idx` (`local_booking_date`, `status`) | Present |
| Overlap / busy range | `bookings_resource_start_idx`, `bookings_resource_range_idx` + GiST `exclude_booking_resource_overlap` | Present |
| Hold expiry sweep | Filter `status=held` + `hold_expires_at` — uses status index + row filter; Beat limit 500 | Sufficient at current volume |

Do not add vanity indexes without `EXPLAIN` evidence under load.

---

## Cache & invalidation (Concepts 06, 20)

- Redis calendar payload TTL ≈ 45s (`bookings/services/calendar_cache.py`).
- Capacity generation token per `local_booking_date`; key includes gen → bump forces miss.
- Invalidation required on: hold create, hold expire, confirm, cancel, and any blocking↔non-blocking transition via `transition_booking` / explicit bump helpers.
- Contract tests: `bookings/tests/test_calendar_capacity_invalidation.py`.

---

## Admission control & async (Concepts 05, 06, 20)

### Must be running (staging/prod)

| Component | Purpose |
|-----------|---------|
| Celery Beat `sweep-stale-booking-holds` (60s) | Free held capacity |
| Celery Beat `sweep-expired-checkout-sessions` (60s) | Free payment-pending capacity |
| Redis token-bucket + circuit breaker | Availability/hold storm shield |
| Reminder/receipt outbox workers | Idempotent drain (hash keys) |

Ops checklist: [RELEASE_CHECKLIST.md](../ops/RELEASE_CHECKLIST.md) §4 + [GUEST_MONEY_PATH.md](../ops/GUEST_MONEY_PATH.md).

---

## Phase F — deferred desk scale (Concepts 02, 14)

Upgrade **only when** staff list/search p95 degrades under real volume:

1. **Keyset pagination** for staff booking lists (replace soft `[:500]` caps in `bookings/services/staff_portal.py`).
2. **Prefix / trigram search** if HMAC exact + `icontains` is insufficient — not a classic in-process trie unless typeahead is a product requirement.

Trigger metrics (suggested): staff search p95 > 500ms or list pages regularly hitting the soft cap with user complaints.

---

## Primary modules

- `bookings/services/booking_calendar.py` — orchestration, bulk capacity, batched slots
- `bookings/services/availability.py` — merge/subtract, bounded range
- `bookings/domain/yield_scheduling.py` — greedy yield / anchors
- `bookings/services/calendar_cache.py` — Redis + capacity gen
- `bookings/services/hold_expiry.py` — expiry + capacity bump
- `bookings/services/state_machine.py` — FSM + invalidation
- `bookings/services/query_observability.py` — query counting for logs/tests
- `core/throttling.py` — token bucket
