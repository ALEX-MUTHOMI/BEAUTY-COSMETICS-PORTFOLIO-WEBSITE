# Authorization Resource Access Policy

Production readiness: **rejected / not claimed**.

This policy closes Phase 3B-C control 1: every resource access must have an
ownership, token, permission, provider, or disabled-route rule. Authorization is
deny-by-default for protected routes; public routes are explicitly documented as
public-by-design.

## Route Classifications

| Class | Meaning | Enforcement pattern |
| --- | --- | --- |
| Public-by-design | Safe public route with no private object access. | Route is intentionally public; response is minimized and tested for sensitive markers. |
| Authenticated-customer-owned | Customer object route. | DRF authentication plus queryset/service scoping by `request.user`. |
| Token-protected public status | Non-enumerable public token route. | Random UUID/token lookup plus zero-PII response and generic denial. |
| Staff-only | Active staff session and permission required. | Staff session guard plus `bookings.*` permission. |
| Staff-with-context | Staff route requiring extra attribute, such as recent reauth or reason. | Staff guard plus context attribute validation and audit. |
| System/provider-only | External or internal system route. | IP allowlist/sandbox tunnel guard, inbox idempotency, state-machine validation, task boundaries. |
| Disabled/legacy route | Route retained only for safe deprecation. | Permission precondition where relevant, then `410 Gone`; no business side effects. |
| Admin-only | Django admin if enabled locally. | Django admin authentication; staging can disable/block. |

## Resource Access Rules

| Route group | Class | Resource object | Actor rule | Enforcement location | Denial | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `/health/`, `/api/health-check/` | Public-by-design | none | Anonymous allowed. | `core.urls.health_check` + security headers tests. | n/a | Newman, security headers tests |
| `/api/csrf/` | Public-by-design | CSRF cookie | Anonymous allowed for SPA CSRF bootstrap only. | `ensure_csrf_cookie`, no-store headers. | n/a | security headers/OpenAPI tests |
| `/api/auth/request-otp/`, `/api/auth/verify-otp/` | Public auth perimeter | email/OTP challenge | Anonymous may request/verify only through throttled, generic OTP flow. | serializers, Turnstile/OTP service, throttles. | safe 400/403/429 | auth/security tests |
| `/api/bookings/catalog/*`, `/api/legal/*`, `/api/gallery/public/*` | Public-by-design | public catalog/legal/gallery objects | Anonymous allowed for public-active data only. | selectors filter active/published data. | safe 404/400 | public route tests, gallery red-team tests |
| `/api/bookings/availability/` | Public-by-design with object input | service/resource IDs | Anonymous may query public availability; invalid objects get generic denial. | availability service validation. | safe 400 | availability security tests |
| `/api/bookings/holds/` | Public booking intent | service/resource IDs, idempotency key | Anonymous can create only server-priced held booking. | hold service, server-side price policy, idempotency. | safe 400/409/429 | hold security tests, mass-assignment tests |
| `/api/bookings/checkout/` | Token-protected booking checkout | booking public ID | Caller must possess valid held-booking public ID and accepted policy; amount comes from server snapshot. | `BookingCheckoutContractService`. | safe 400 | checkout contract tests, mass-assignment tests |
| `/api/bookings/status/<public_booking_id>/` | Token-protected public status | booking public UUID | Token holder can view zero-PII status only. | status selector, generic 404. | 404 | BOLA tests, booking status red-team tests |
| `/api/checkout/sessions/` | Authenticated-customer-owned | checkout session | Authenticated user owns created session; client owner fields ignored. | `CheckoutSessionListCreateView`, service owner assignment. | 401/403/400 | checkout API tests, mass-assignment tests |
| `/api/checkout/sessions/<checkout_id>/` | Authenticated-customer-owned | checkout session | Only session customer can read. | `get_customer_checkout_or_none`. | 404 | BOLA/customer tests |
| `/api/checkout/sessions/<checkout_id>/mpesa/stk/` | Authenticated-customer-owned | checkout session/STK attempt | Only session customer can initiate STK; throttle applies. | selector, STK throttle, provider service. | 404/429/503 | checkout permission/throttle tests |
| `/api/checkout/mpesa/webhook/` | System/provider-only | provider callback event | Provider source must pass IP/tunnel policy; DB state must pass idempotency, amount, expiry, and state validation. | permission class, webhook inbox, checkout/billing services. | 202/400/403 | webhook/security/load tests |
| `/api/billing/stk-push/` | Disabled/legacy route | legacy STK payload | No actor may initiate billing-owned STK. | view returns `410`. | 410 | status/payment tampering tests |
| `/api/billing/mpesa-webhook/` | Disabled/legacy route | legacy webhook payload | If IP allowlist passes, route still returns `410`; checkout webhook is canonical. | `IsSafaricomIP`, view returns `410`. | 403/410 | 3B-C closeout test |
| `/api/staff/auth/*` | Staff-only/auth perimeter | staff session/reset challenge | Only valid active staff session may access staff session endpoints. | staff auth service/session guards. | 400/403/429 | staff auth tests |
| `/api/staff/bookings/schedule/`, `/api/staff/bookings/week/` | Staff-only | staff schedule read model | Active staff with `view_staff_portal` permission. | `_require_staff_permission`. | 403/400 | staff tests, role/query tampering tests |
| `/api/staff/bookings/<public_booking_id>/` | Staff-only | booking public UUID | Active staff with `view_staff_booking` permission. Current product policy is global staff access. | `_require_staff_permission`, staff selector. | 403/404 | 3B/3B-C staff tests |
| `/api/staff/bookings/<public_booking_id>/payment/` | Staff-only | payment summary | Active staff with `view_staff_payment_summary`; output is redacted. | `_require_staff_permission`, payment selector. | 403/404 | staff payment visibility tests |
| `/api/staff/bookings/<public_booking_id>/contact-access/` | Staff-with-context | customer contact info | Active staff with `view_staff_contact_details`, recent reauth, reason, and audit. | permission guard, recent reauth, service audit. | 403/400/404 | contact audit/red-team tests |
| `/api/staff/gallery/*` | Staff-only | gallery category/upload | Active staff session required; upload is quarantined/validated. | staff guard, gallery upload service. | 403/400/409/429 | gallery upload/security tests |
| `/api/customers/remembered-device/*` | Token-protected public convenience | remembered-device cookie token | Opaque token holder can access redacted convenience data only. | HMAC token lookup, redacted selectors. | generic denial | remembered-device tests |
| `/admin/` | Admin-only | admin session | Local admin only when enabled; staging can disable/block. | Django admin auth/settings/proxy. | login/404/blocked | staging policy docs |

## Release Rule

No route that accepts object IDs, tokens, owner-like fields, role-like fields,
status-like fields, or payment-like fields may be added without updating:

- `docs/security/BOLA_IDOR_ACCESS_MATRIX.md`
- this policy document
- relevant negative authorization tests in `tests/security/`
- API/Newman coverage where the route is externally exposed

## Status

All inventoried high-risk protected route groups have documented rules and test
evidence. Production readiness remains rejected.
