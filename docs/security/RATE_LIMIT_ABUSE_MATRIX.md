# Rate-Limit and Abuse Matrix

Phase 3D inventory date: 2026-06-20. Production readiness remains rejected.

| Route group | Actor/key | Abuse and existing control | Required control | Expected abuse response | Status |
| --- | --- | --- | --- | --- | --- |
| CSRF bootstrap | anonymous IP | token bootstrap | IP token bucket | generic `429` | covered |
| OTP request | anonymous IP + normalized email | Redis `otp_request` throttle | retain hashed composite key | generic `429` | covered |
| Staff login | IP + email | cooldown after failures | retain generic cooldown | generic `429` | covered |
| Availability | anonymous IP | input bounds plus explicit scope | route token bucket | generic `429` | covered |
| Booking hold | anonymous IP | idempotency/capacity/circuit breaker plus explicit scope | route token bucket | generic `429` | covered |
| Booking checkout bridge | anonymous IP | idempotency/state lock plus explicit scope | route token bucket | generic `429` | covered |
| Public status | IP | generic `404`, read-only, explicit scope | route token bucket | generic `404` or `429` | covered |
| Checkout create/detail | authenticated user + IP | explicit route scopes and idempotency | route scopes | generic `429` body plus `Retry-After` | covered |
| STK initiation | authenticated user + IP | Redis `checkout_stk_push`, idempotency | retain and test | generic `429` | covered |
| Webhook | allowlisted provider IP + event id | permission and inbox replay idempotency | intentional no client throttle | generic `400`/`202` | covered |
| Legacy billing routes | caller | disabled `410` | retain non-reflective denial | generic `410` | covered |
| Public gallery | anonymous IP | capped output, generic `404`, explicit scope | route token bucket | generic `429` | covered |
| Public media resolver | anonymous IP | published/public resolver, generic `404`, explicit scope | route token bucket | generic `404` or `429` | covered |
| Staff contact reveal | staff user | permission, recent auth, reason, audit, explicit scope | staff-user token bucket | generic `429` | covered |
| Staff booking/payment reads | staff user | permission/redaction only | documented global/session bounds | generic `403`/`404` | follow-up |

All throttle keys must be hashed before Redis storage. Throttle responses are
minimal and must not disclose PII, provider, ledger, token, storage, or object
existence data.

High-volume test traffic is classified separately from customer activity:
100/1,000 immediate polls use copied, test-only scope overrides and assert the
production setting is restored. This does not alter the operational policy.
