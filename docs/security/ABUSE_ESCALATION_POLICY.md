# Abuse Escalation Policy

Phase 3D-PLUS adds a bounded, route-scoped abuse layer above Redis token
buckets. It is local application control, not a claim that a WAF or production
incident-response system is deployed. Production readiness remains rejected/not
claimed.

## State model

```text
normal -> rate_limited -> cooldown -> temporary_ban -> waf_candidate -> manual_review
                     \-> suspicious (invalid identifier or source signal)
```

`rate_limited` and `suspicious` are signals. Persisted actions are
`cooldown`, `temporary_ban`, and `waf_candidate`; each is route-scoped,
Redis-backed, hashed, and TTL-bound. `waf_candidate` is a redacted operator
handoff, not a claimed CDN/WAF rule.

## Cost model

Normal throttled traffic performs one Redis Lua admission call. It checks an
active action and updates the token bucket atomically; it does not increment an
abuse score, write a database audit row, inspect a body, or emit an abuse log.
Only denials and narrow suspicious responses increment a TTL-bound score.
Events are emitted only when an action changes, preventing log amplification.

## Default policy

| Setting | Value |
| --- | ---: |
| score window | 10 minutes |
| cooldown / temporary ban / WAF candidate score | 4 / 11 / 16 |
| cooldown / temporary ban / candidate TTL | 5m / 15m / 1h |
| retry before action expires | +2 score |

These controls do not alter production route rates. Tests use only scoped
`override_settings` values.

| Signal | Scope | Score |
| --- | --- | ---: |
| repeated `429` | current route | 1 |
| retry before `Retry-After` | current route | 2 |
| invalid booking status token | `booking_status` | 1 |
| invalid checkout detail | `checkout_detail` | 2 |
| invalid media handle/extension | `media_resolver` | 1 |
| raw non-public media path | `media_resolver` | 4 |
| non-staff contact reveal probe | `staff_contact_reveal` | 4 |
| rejected webhook source | `webhook` | 5 |

All responses remain generic. Enumeration-sensitive requests retain generic
`404` until a throttled route rejects with generic `429`; scoring introduces no
object-existence signal.

Authenticated actors use a hashed customer/staff identity. Anonymous requests
prefer a hashed session and use a hashed IP only as fallback. No automatic
permanent or global IP ban exists. Action expiry restores admission; a new
suspicious event can create a fresh action while its separate score window
remains active.

Verification: `test_abuse_escalation.py` covers generic response privacy,
Retry-After defiance, action expiry, hashed keys/events, and shared-IP actor
isolation. `test_abuse_signal_routes.py` covers staff probes, raw storage paths,
rejected webhooks, and fail-closed Redis admission.
