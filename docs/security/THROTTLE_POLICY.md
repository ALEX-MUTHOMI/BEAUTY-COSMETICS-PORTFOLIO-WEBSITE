# Throttle Policy

Phase 3D uses Redis-backed token buckets. Redis failure is fail-closed with a
generic `503`; a throttle refusal is a generic `429` with `Retry-After` when a
wait can be calculated. Raw IPs, users, tokens, and handles are never stored in
the throttle-key suffix.

- Global DRF: anonymous `100/day`, authenticated `1000/day`.
- OTP: IP plus normalized email, `otp_request` (`5/min`).
- Staff login: IP plus email cooldown after five failures in ten minutes.
- STK: authenticated user plus IP, `checkout_stk_push` (`3/min`); legacy fake
  STK uses the existing `stk_push` scope.
- Booking hold/checkout, status polling, availability, CSRF, gallery/media,
  and contact reveal use explicit route scopes rather than global limits.
- Webhooks intentionally use provider-IP admission plus inbox/event
  idempotency, not a client rate limit that could drop valid payment callbacks.

Local tests override only the affected scope with low deterministic rates and
clear Redis throttle keys between cases. Production tuning remains a later
operational decision; limits must not be increased merely to satisfy tests.
