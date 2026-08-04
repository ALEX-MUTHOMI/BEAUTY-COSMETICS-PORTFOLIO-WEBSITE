# Temporary Actor Restriction Policy

“IP ban” is deliberately narrow here. Phase 3D-PLUS does not add a permanent
or global IP ban. It implements temporary, route-scoped Redis actions and uses
an IP only as an anonymous fallback.

| Request type | Restriction identity | Shared-IP protection |
| --- | --- | --- |
| Authenticated customer | hashed customer actor | isolated from another customer |
| Authenticated staff | hashed staff actor | isolated from another staff member |
| Anonymous session | hashed session actor | avoids broad IP action |
| Stateless anonymous | hashed IP actor | short TTL and route-scoped only |

Keys are `abuse:score:<scope>:<actor_type>:<hash>` and
`abuse:action:<scope>:<actor_type>:<hash>`. They contain no raw IP, email,
phone, token, checkout ID, booking ID, storage key, request body, or raw Redis
key in logs.

| State | HTTP effect | TTL |
| --- | --- | ---: |
| cooldown | generic `429` and `Retry-After` | 5 minutes |
| temporary ban | generic `429` and `Retry-After` | 15 minutes |
| WAF candidate | generic `429` on throttled routes | 1 hour |

There is no automatic `403` IP ban. That prevents an existence oracle and
reduces harm to carrier NATs, offices, and public Wi-Fi. A broader edge rule
requires human review using redacted route/action/score/actor-hash evidence.

Raw media paths and rejected webhook sources may be scored when no public route
owns the invalid path. Their current effect is candidate generation; WAF/CDN
enforcement is described in `WAF_CDN_ABUSE_POLICY.md`.
