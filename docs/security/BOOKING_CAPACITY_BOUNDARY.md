# Booking Capacity Boundary

Rate limiting is not booking capacity management. Phase 3D-PLUS blocks abusive
HTTP admission cheaply; it does not prove real staffing capacity, day-level
schedules, concurrent checkout volume, provider capacity, or a 1,000-booking
production event.

Existing holds, idempotency, transactions, and capacity/circuit-breaker controls
remain booking truth. A later staging capacity phase must measure concurrent
hold/create/checkout races, locks, expiry/release behavior, database pools,
queue pressure, and provider callbacks. Tuesday/Wednesday business policies
must be read from actual booking configuration, never inferred from throttles.

No Phase 3D-PLUS control changes lifecycle, pricing, payment truth, staff
schedules, or capacity policy.
