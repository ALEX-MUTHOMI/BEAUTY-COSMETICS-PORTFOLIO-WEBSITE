# Least Privilege and Deny-by-Default Route Policy

Production readiness: **rejected / not claimed**.

This policy closes Phase 3B-C control 4. Protected routes are deny-by-default;
public routes are public only when explicitly classified and response-minimized.

## Least Privilege Classes

| Class | Route groups | Allow condition | Deny/default behavior |
| --- | --- | --- | --- |
| Public allow | health, CSRF, legal, public catalog, availability, public gallery | Public-by-design and response-minimized. | Public routes still reject invalid object inputs generically. |
| Token public allow | booking status, booking checkout bridge | Valid random public booking token and state/context rules. | 404 or safe 400 without PII/object existence details. |
| Authenticated customer allow | checkout session create/detail/STK | Authenticated owner or server-derived owner. | 401/403/404; identity headers ignored. |
| Staff allow | staff schedule/week/detail/payment/gallery navigation | Active staff session and required permission. | 403 for non-staff/inactive/unauthorized staff. |
| Staff-with-condition allow | contact reveal, reauth | Active staff session, permission, recent reauth, reason/audit. | 403/400/404 generic; no phone/email on denial. |
| Provider/system allow | checkout webhook, Celery tasks | Source/IP/tunnel policy plus state-machine and idempotency validation. | 202/400/403 safe; no raw provider payload leak. |
| Disabled deny | legacy billing STK/webhook | No business actor allowed. | 410 after applicable preconditions; no payload echo. |
| Admin-only | Django admin | Admin authentication only; staging can disable/block. | admin login/blocked/404. |

## Deny-by-Default Evidence

| Policy | Evidence |
| --- | --- |
| Anonymous denied from protected checkout/staff/gallery objects. | `tests/security/test_bola_idor_anonymous_access.py` |
| Non-staff denied from staff endpoints even with role/header/query tampering. | `tests/security/test_bola_idor_staff_objects.py`, `tests/security/test_role_tampering.py` |
| Inactive staff denied. | `tests/security/test_bola_idor_staff_objects.py` |
| Other customer denied from owner-only checkout objects. | `tests/security/test_bola_idor_customer_objects.py` |
| Client role/header/query fields do not widen access. | `tests/security/test_role_tampering.py`, `tests/security/test_query_scope_tampering.py` |
| Disabled legacy routes remain disabled. | `tests/security/test_status_payment_tampering.py`, `tests/security/test_authorization_control_closeout.py` |
| Unknown sensitive routes fail closed. | `tests/security/test_authorization_control_closeout.py` |
| Public routes are response-minimized and public-by-design. | Newman, gallery tests, security headers tests. |

## Route Addition Rule

New endpoints must start from deny-by-default. The developer must explicitly
choose one least-privilege class, document its authorization attributes, and add
negative tests for anonymous, same-privilege non-owner, role/header tampering,
and unsafe object/reference guessing where applicable.
