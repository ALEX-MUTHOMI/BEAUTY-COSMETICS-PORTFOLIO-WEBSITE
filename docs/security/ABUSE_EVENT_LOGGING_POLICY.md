# Abuse Event Logging Policy

Abuse events are small structured warning records emitted only when a temporary
route action is created or escalated. Diagnostics remain separately opt-in with
`AESTHETIC_OS_DIAGNOSTIC_TRACE`.

Allowed fields are event type, route name, actor type/hash, throttle scope,
action, retry duration, score, status family, Redis status, and correlation-ID
hash.

Never log raw IP, email, phone, token, session ID, booking/checkout/ledger/
receipt identifier, provider payload, body, response, query string, storage key,
bucket name, private media path, or raw Redis key. Client-supplied request IDs
are not trusted. Route names, not identifier-bearing paths, are logged.

No database audit write occurs for normal traffic or every `429`. Events are
transition-only. Production retention, transport, alerting, and access controls
remain deployment work requiring explicit review.
