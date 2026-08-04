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
| Public status | session/IP fallback | generic `404`, read-only, explicit scope | token bucket plus invalid-token score/cooldown | generic `404` or `429` | covered |
| Checkout create/detail | authenticated customer + IP | explicit route scopes and idempotency | route scopes plus invalid-detail score/cooldown | generic `429` body plus `Retry-After` | covered |
| STK initiation | authenticated user + IP | Redis `checkout_stk_push`, idempotency | retain and test | generic `429` | covered |
| Webhook | allowlisted provider IP + event id | permission and inbox replay idempotency | intentional no client throttle; rejected-source signal | generic `400`/`202`/`403` | covered |
| Legacy billing routes | caller | disabled `410` | retain non-reflective denial | generic `410` | covered |
| Public gallery | anonymous IP | capped output, generic `404`, explicit scope | route token bucket | generic `429` | covered |
| Public media resolver | session/IP fallback | published/public resolver, generic `404`, explicit scope | token bucket plus invalid-handle/raw-path score | generic `404` or `429` | covered |
| Staff contact reveal | staff/session/IP fallback | permission, recent auth, reason, audit, explicit scope | route token bucket plus probe/reauth score | generic `403`/`429` | covered |
| Staff booking/payment reads | staff user | permission/redaction only | documented global/session bounds | generic `403`/`404` | follow-up |

All throttle keys must be hashed before Redis storage. Throttle responses are
minimal and must not disclose PII, provider, ledger, token, storage, or object
existence data.

High-volume test traffic is classified separately from customer activity:
100/1,000 immediate polls use copied, test-only scope overrides and assert the
production setting is restored. This does not alter the operational policy.

Temporary actions are route-scoped and TTL-bound. They use hashed actor keys,
not raw IP or identifiers, and are never permanent network bans. Distributed
abuse remains a WAF/CDN and operational-review concern.
