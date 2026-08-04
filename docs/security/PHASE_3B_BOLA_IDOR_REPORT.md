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

Medium follow-up items after Phase 3B discovery:

- Add explicit allowed-IP regression for disabled legacy billing webhook
  returning `410` - closed in Phase 3B-C.
- Decide whether future staff booking views require per-beautician row scoping;
  current implementation is staff-global by design after permission checks -
  documented in Phase 3B-C.
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
- Legacy billing webhook disabled-route behavior after allowlisted IP permission
  acceptance is covered in Phase 3B-C.
- Newman negative authorization cases remain a follow-up.

## Phase 3B-C Closeout Addendum

Phase 3B-C documents and verifies the five BOLA remediation controls:

- authorization rule on every inventoried route group;
- indirect reference/identifier policy;
- ABAC policy matrix without overbuilding a speculative framework;
- least privilege and deny-by-default route classification;
- repeatable security testing through `tests/security`, Turbo Pass, Newman,
  lint/security, host git hygiene, secret hygiene, Docker health, and worker
  ping.

Staff scoping decision: active authorized staff have global staff portal read
access by current product policy. Per-beautician row ownership is deferred until
the product introduces assignment/branch/resource-specific staff ownership.

## Phase 3B-F Final Closeout Addendum

Phase 3B-F resolved the two remaining execution caveats:

- `bookings/tests` completed as a full partition: 290 tests passed in 612.30s.
- `scripts/ci/turbo_pass.ps1` completed with `TURBO_PASS_RESULT=passed` after
  adding safe repo-local Docker config handling for shells that cannot read the
  host user's Docker credential config.

The five controls remain verified:

- authorization checks are documented for every inventoried object-bearing route
  group;
- public identifiers, direct internal identifiers, provider identifiers, ledger
  identifiers, and storage identifiers have documented handling rules;
- ABAC is represented through existing actor/resource/context attributes rather
  than a speculative framework;
- least privilege and deny-by-default behavior are tested for unknown sensitive
  routes, disabled legacy billing routes, staff permission boundaries, and
  customer-owned checkout access;
- repeatable testing is covered by `tests/security`, API/security partitions,
  Booking full partition, Docker Newman, Turbo Pass, lint/security, secret
  hygiene, Docker health, and Celery worker ping.

No critical/high BOLA, IDOR, mass-assignment, role-tampering, ABAC, or
least-privilege finding remains open for current product policy.

## Patch Backlog

Patch backlog: `docs/security/PHASE_3B_PATCH_BACKLOG.md`.
