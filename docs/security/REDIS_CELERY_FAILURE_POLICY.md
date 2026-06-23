# Redis and Celery Failure Policy

## Redis admission control

`users.services.get_redis_client()` uses a process-cached Redis client with a
0.25-second connect timeout, 0.5-second socket timeout, health checks, and no
retry-on-timeout loop. These values are configurable and fail fast rather than
accumulating blocked web workers.

| Namespace | Purpose | TTL | Raw identifier |
| --- | --- | --- | --- |
| `throttle:*` | route token bucket | twice route period | never |
| `abuse:score:*` | suspicious-event counter | score window | never |
| `abuse:action:*` | temporary route action | action duration | never |
| `otp:*` | existing OTP state | 5 minutes | separate legacy namespace |

Every `RedisTokenBucketThrottle` route fails closed on Redis error with generic
`503`: booking hold/checkout, checkout create/detail/STK, staff contact,
gallery/media, booking status, availability, and CSRF. Current public-read
behavior is therefore fail-closed, not an unverified graceful-degradation
promise. The post-response abuse scorer fails silently only because it never
grants access or changes the route response; admission remains fail-closed.

## Celery failure boundary

Celery queues (`billing`, `receipts`, `express_auth`, `gallery`, and default)
handle asynchronous work. Booking and payment truth must stay in synchronous
database transaction/idempotency paths. A notification or delivery failure must
not create a different booking/payment fact.

Phase 3D-PLUS does not claim a real provider/email call, Redis restart, worker
outage, or production drill. Staging/Phase 3J must prove bounded task retries,
terminal/dead-letter handling, queue and worker alerts, idempotent task replay,
Redis/Celery restart without duplicate financial truth, and operator
reconciliation for failed receipt/notification delivery.
