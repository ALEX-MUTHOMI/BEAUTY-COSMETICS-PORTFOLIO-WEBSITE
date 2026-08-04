# Bot and Retry-After Policy

The API returns generic `429` JSON and a numeric `Retry-After` header. It never
places bucket counts, score, actor identity, cooldown reason, provider details,
or object existence in the response.

1. A normal route throttle allows or returns generic `429`.
2. A denial adds one score point.
3. At the cooldown threshold, a route action with a TTL is created.
4. A request during that action is rejected before view/database work, adds two
   points, and can escalate to temporary ban or WAF candidate.
5. `Retry-After` is the action TTL when an action exists, otherwise the
   token-bucket wait; it is always positive.

One accidental retry is not an action under default policy. A client that keeps
retrying before the advertised wait is. This keeps a normal Booking SPA poller
cheap while making a retry loop expensive only to itself.

The shared frontend retry helper honors a valid numeric `Retry-After` and
rejects malformed values without causing an immediate retry. Future callers
must use one in-flight poll per booking/checkout, backoff on retryable errors,
deduplicate components, and stop on terminal state.

There is currently no public booking-status SPA caller wired to that helper.
This is a backend contract and future UI requirement, not a claim of finished
customer-flow wiring. Runtime remains `booking_status=30/min` and
`checkout_detail=60/min`; higher durability values are test-only overrides.
