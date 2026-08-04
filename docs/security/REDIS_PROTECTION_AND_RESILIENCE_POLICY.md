# Redis Protection and Resilience Policy

## Purpose and boundary

Redis is a private, temporary control plane. It is not the outer perimeter and
is not durable booking, payment, ledger, capacity, authorization, or staff
truth. The intended production layering is:

```text
CDN/WAF/proxy -> Django admission and authorization -> Redis control plane -> PostgreSQL truth
```

Redis must never be reachable by browsers or the public internet. Production
requires a private network, network/security-group allowlists, authentication,
TLS where supported by the chosen service, and access limited to the approved
application and worker identities. Local Compose uses Redis authentication and
an internal service port only; this is not a production network certification.

## Redis usage inventory

| Area | Owner | Purpose | Namespace | TTL | Raw identifier state | Failure behavior | Classification |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Route throttling | `core.throttling.RedisTokenBucketThrottle` | Atomic token-bucket admission | `throttle:*` | yes | HMAC/hashed suffix | generic 503 | approved temporary control-plane state |
| Abuse score | `core.abuse.record_abuse_signal` | Suspicious-denial escalation | `abuse:score:*` | yes | actor hash only | signal omitted if unavailable; existing denial is retained | approved temporary control-plane state |
| Abuse action | `core.throttling` and `core.abuse` | cooldown, temporary ban, WAF candidate | `abuse:action:*` | yes | actor hash only | generic 429/503 as applicable | approved temporary control-plane state |
| Express OTP | `users.services.OTPService` | short-lived OTP verifier | `otp:express:v1:*` | 300 seconds | recipient HMAC key and OTP HMAC verifier | request is not admitted when protected Redis controls fail | approved temporary control-plane state |
| Customer booking OTP | `bookings.services.customer_otp` | temporary challenge/rate state | database challenge plus hashed control identifiers | bounded by policy | hashed identifier components | controlled denial | approved temporary control-plane state |
| Celery | `core.celery` | broker and result coordination | Celery-managed keys | broker policy | encrypted OTP delivery envelope; no raw task argument | worker retry policy | Celery/broker state |
| Test cleanup | `conftest.py` | remove test-only control state | selected `throttle:*`, `abuse:*`, `otp:*` | n/a | never printed | bounded SCAN/delete only | test-only state |

Redis must not own booking holds, booking status, checkout state, payment or
ledger state, staff authorization, media visibility, or capacity. Those are
enforced by Django and PostgreSQL models, transactions, state machines, and
constraints.

## Indirect-pressure threat model

| Surface | Redis work | Abuse risk | Outer production defense | Application response |
| --- | --- | --- | --- | --- |
| OTP request/verification | admission plus temporary verifier | spam and brute force | WAF bot challenge, proxy limits, app throttle | generic 429 or 503 |
| Booking status | admission | opaque identifier probing | WAF/proxy route rule | generic 404, 429, or 503 |
| Booking hold/checkout | admission | inventory/payment pressure | WAF/proxy and CSRF/auth | generic 429 or 503 before business work |
| Checkout detail/STK | authenticated admission | polling and payment pressure | auth, WAF/proxy route controls | generic 404, 429, or 503 |
| Public gallery/media resolver | admission and invalid-path signals | scraping and resolver enumeration | CDN cache and WAF route controls | generic 404, 429, or 503 |
| Staff contact access | admission and denial signal | PII probing | staff auth, reauth, WAF | generic 403, 429, or 503 |
| Provider webhook | source/signature admission | forged/replayed callback | provider-aware WAF allowlist | controlled generic denial |

Redis is an inner control plane behind edge, proxy, and application admission.
It must never be expected to absorb volumetric or distributed bot traffic by
itself. Public cacheable gallery variants should be served from CDN/browser
cache in production; private, draft, and quarantine content must never be
publicly cached.

## Failure and performance policy

Protected routes use one bounded Redis Lua decision where possible. Connection
and socket timeouts are explicit and short, and retry-on-timeout is disabled.
Redis admission failure returns a generic no-store 503 before serializer,
database, provider, or business work. Denied requests return generic 429 before
business work. Normal allowed requests maintain only token-bucket state and do
not create abuse-score or action state.

Low-risk public routes have an explicit conservative local behavior: if their
Redis admission check is unavailable, Django returns generic 503 rather than
silently failing open. Production CDN caching is the preferred availability
layer for cacheable public media and gallery reads.

Lua scripts must keep comments and static-analysis suppressions outside program
text where tooling could misinterpret them. The fake Redis test double must
assert the current three-key/twelve-argument/seven-result contract.

## Celery separation

The local stack currently shares Redis for Celery and control-plane state, using
separate application namespaces. OTP task arguments are encrypted before they
enter the broker, and task logs use redacted recipient information only.

Production recommendation: use separate managed Redis instances, or at minimum
separate ACLs, databases/namespaces, resource limits, monitoring, and ownership
for `throttle`/`otp`/`abuse` versus Celery broker/result traffic. A Celery
backlog must not starve admission control. This split and a restart/slow/failover
exercise are required Phase 3J staging work.

## Required monitoring and alerts

Monitor Redis latency, connection errors, CPU, memory, evictions, key growth,
throttle/OTP/abuse key counts, Celery queue depth, worker health, 429 rate, 503
rate, ignored Retry-After rate, and protected-route Redis-unavailable rate.

Alert on Redis unavailability or latency, memory/eviction risk, abnormal OTP,
booking-status, media-resolver, or staff-contact probes, Celery backlog, and a
spike in fail-closed 503 responses.

## Required runbooks

Maintain runbooks for Redis unavailable, slow Redis, restart/failover, abuse-key
growth, OTP delivery backlog, Celery broker backlog, emergency WAF rule,
false-positive rollback, and provider-webhook preservation.

Local Phase 3E1 verifies source-policy and bounded contracts only. Redis
restart, slow-response, unavailability, Celery-backlog, WAF/CDN challenge, and
rollback drills remain mandatory Phase 3J staging work.
