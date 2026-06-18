# Phase 3B BOLA / IDOR / Mass Assignment Discovery Report

## Executive Verdict

`PHASE 3B DISCOVERY ACCEPTED - NO CRITICAL/HIGH BOLA FINDINGS FOUND`

Production readiness: **REJECTED / NOT CLAIMED**.

This phase added targeted discovery tests and matrices for object-level
authorization, cross-user access, anonymous protected-object access, staff
boundary abuse, mass assignment, role/header/query tampering, and payment/status
tampering. No broad business logic, booking flow, checkout/billing truth,
gallery behavior, or staff auth/session behavior was intentionally changed.

## Scope

Apps and route groups assessed:

- `bookings`: public catalog, availability, holds, checkout bridge, booking
  status, staff portal, staff contact reveal, staff gallery, public gallery,
  remembered-device routes by existing coverage.
- `checkout`: checkout session create/detail/STK, M-Pesa webhook by existing
  coverage.
- `billing`: disabled legacy STK route and disabled legacy webhook route policy.
- `users`: OTP/auth routes by existing Phase 3A coverage.
- `core`: health, CSRF, OpenAPI disabled-by-default policy by existing coverage.

Actors assessed:

- Anonymous.
- Customer owner.
- Other customer.
- Authenticated non-staff.
- Authorized staff.
- Staff without contact permission.
- Inactive staff.
- Provider webhook/system paths by existing checkout/billing tests.

## Object Access Matrix Summary

- Total inventoried route groups: **34**.
- High-risk objects: booking public IDs, checkout session IDs, checkout request
  IDs, billing ledger correlation IDs, receipt/status tokens, staff contact
  reveal IDs, gallery storage/media objects, remembered-device tokens.
- Public-by-design routes: health, CSRF bootstrap, legal docs, public catalog,
  public availability, public gallery, and token-based booking status.
- Main gap: explicit allowed-IP regression for disabled legacy billing webhook
  returning `410` after IP permission acceptance.

See `docs/security/BOLA_IDOR_ACCESS_MATRIX.md`.

## BOLA / IDOR Result

| Area | Result | Evidence |
| --- | --- | --- |
| Customer-to-customer checkout access | Other customer cannot read or initiate STK for another user's checkout, even with role/user headers and query params. | `tests/security/test_bola_idor_customer_objects.py` |
| Booking status token | Public token route returns status-only payload and does not expose raw customer PII/internal IDs/provider data. Invalid/missing tokens are generic and indistinguishable. | `tests/security/test_bola_idor_customer_objects.py` |
| Anonymous protected-object access | Anonymous users cannot access checkout session details, staff booking detail, staff contact reveal, or staff gallery. | `tests/security/test_bola_idor_anonymous_access.py` |
| Staff boundary | Non-staff cannot use headers/query role claims to access staff routes. Staff without contact permission cannot reveal contact details. Inactive staff access is denied. | `tests/security/test_bola_idor_staff_objects.py` |
| Gallery/private object access | Public gallery query tampering does not include private/unpublished images or storage fields. | `tests/security/test_query_scope_tampering.py` |
| Disabled billing STK route | Legacy billing STK remains disabled and does not echo submitted object IDs/provider IDs. | `tests/security/test_bola_idor_customer_objects.py`, `tests/security/test_status_payment_tampering.py` |

## Mass Assignment Result

Dangerous fields tested:

- Ownership: `customer`, `customer_id`, `user_id`.
- Role/admin: `role`, `is_staff`, `is_superuser`.
- Booking/payment state: `status`, `booking_status`, `payment_status`,
  `is_paid`.
- Payment truth: `amount`, `currency`, `provider_reference`, `provider_status`,
  `checkout_id`, `ledger_id`, `receipt_token`.

Endpoints tested:

- `POST /api/bookings/holds/`.
- `POST /api/bookings/checkout/`.
- `POST /api/checkout/sessions/`.
- `POST /api/billing/stk-push/`.

Result: dangerous fields were rejected, ignored, or overwritten server-side.
No test proved that client-supplied server-owned fields take effect.

See `docs/security/MASS_ASSIGNMENT_MATRIX.md`.

## Role / Header / Query Tampering Result

Payload/query/header tampering tested:

- `role=admin`, `is_staff=true`, `scope=all`, `include_private=true`.
- `X-Role`, `X-Admin`, `X-User-Id`, `X-Staff-Id`,
  `X-Forwarded-User`.

Result: authorization remained based on authenticated server-side identity,
session state, and permissions. Untrusted headers and query parameters did not
widen staff, checkout, or public gallery access in the tested routes.

See `docs/security/ROLE_TAMPERING_MATRIX.md`.

## Status / Payment / Booking State Tampering Result

Attempts tested:

- Client tried to create paid checkout sessions directly.
- Client tried to force booking checkout bridge into `confirmed`/`paid`.
- Client tried to submit provider references, ledger IDs, receipt tokens, and
  fake payment status.
- Client tried disabled legacy billing STK route with payment truth fields.

Result: checkout sessions remained `created` or `payment_pending` as appropriate;
booking checkout remained server/provider-controlled; no `LedgerTransaction`
success was created by client-side payload fields.

## Findings

No confirmed critical/high findings were found by Phase 3B tests.

Medium follow-up items:

- Add explicit allowed-IP regression for disabled legacy billing webhook
  returning `410`.
- Decide whether future staff booking views require per-beautician row scoping;
  current implementation is staff-global by design after permission checks.
- Add selected Newman negative cases for deployment/API contract parity.
- Build route response allowlists in Phase 3C.

See `docs/security/PHASE_3B_PATCH_BACKLOG.md`.

## No-Finding Evidence

- Cross-customer checkout access is denied with generic `404`.
- Anonymous protected-object access is denied.
- Non-staff role/header tampering does not open staff routes.
- Mass-assigned owner/customer/role/status/payment fields do not take effect.
- Public gallery query widening does not expose unpublished/private storage data.
- Public booking status remains zero-PII and token-based.
- Legacy billing STK route remains disabled.

## Gaps

- Phase 3B did not run active ZAP, full ZAP, Burp, DDoS tooling, real Daraja,
  real email providers, or real R2.
- Phase 3B did not prove production readiness.
- Phase 3B did not change staff global-scope product behavior.
- Legacy billing webhook needs a tighter explicit disabled-route test after
  allowlisted IP permission acceptance.
- Newman negative authorization cases remain a follow-up.

## Patch Backlog

Patch backlog: `docs/security/PHASE_3B_PATCH_BACKLOG.md`.
