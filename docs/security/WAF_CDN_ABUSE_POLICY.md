# WAF and CDN Abuse Policy

This is an operator policy. Phase 3D-PLUS does not create or modify a
Cloudflare, CDN, DNS, firewall, or production WAF configuration.

| Layer | Owns | Does not replace |
| --- | --- | --- |
| Django/Redis | route throttles, actor actions, generic denials | distributed botnet controls |
| CDN/browser cache | public gallery/media cache | authorization/private media protection |
| WAF/CDN | bot challenge, volumetric filters, IP/ASN reputation | booking/payment authorization/idempotency |
| Operator review | redacted candidate action | permanent automatic bans |

Future edge rules should challenge/restrict repeated opaque-media resolver
misses and invalid raw `/media/` paths, use short route-aware mitigation for
booking-status/gallery abuse, and preserve provider webhook availability. Do
not blindly challenge authenticated checkout/payment mutations or cache private
media. Public variants alone may be cached within their revocation policy.

## Route policy map

| Surface | Edge policy | Safety boundary |
| --- | --- | --- |
| Public gallery and media resolver | cache public variants; challenge repeated resolver misses and raw media paths | never cache or expose private/draft/quarantine media |
| Booking-status polling | rate/challenge sustained anonymous polling and identifier probing | retain generic application responses; do not infer booking existence |
| Checkout-detail polling | monitor authenticated retry bursts; use narrow challenge only after route evidence | do not apply broad challenges to payment mutations |
| Auth/OTP | bot challenge and short burst controls at the edge | preserve the application Turnstile/OTP policy and recovery flow |
| Staff-route probing | protect non-staff request bursts and review redacted candidates | avoid shared-office IP lockouts; authorization stays in Django |
| Provider webhook | retain provider source admission and availability | coordinate every edge rule with the provider allowlist and callback SLO |

## Emergency and false-positive procedure

Every candidate needs monitoring/dry-run, false-positive review, rollback
ownership, and staged validation. Start with a route-scoped challenge or
short-lived rate rule, record only redacted aggregate evidence, and name an
operator who can revert the rule. Escalation to an IP/ASN rule requires review
of shared-IP impact, customer-support impact, provider webhook impact, and a
rollback test. Edge rules must not consume raw values from application logs or
disclose a denial reason.

## Redis-pressure boundary

Edge controls must reduce the number of abusive requests that reach
Django/Redis. Redis is an internal admission-control dependency, not a
volumetric bot shield; it must not be expected to absorb distributed abuse on
its own. Real WAF/CDN deployment, monitoring, and rollback validation remain a
staging/production follow-up.
