# Phase 3B Role / Header / Query Tampering Matrix

Production readiness: **rejected / not claimed**.

Authorization must derive from authenticated server-side identity, permissions,
and provider callback validation. Client-submitted roles, headers, IDs, and
query parameters must not widen access.

## Tampering Inputs

| Channel | Inputs tested | Expected behavior |
| --- | --- | --- |
| Payload | `role=staff`, `role=admin`, `is_staff=true`, `is_superuser=true`, `permissions`, `groups` | Ignored/rejected; user role unchanged. |
| Query | `role=admin`, `is_staff=true`, `staff_id`, `customer_id`, `include_private=true`, `scope=all`, `owner_id` | Cannot widen access or include private objects. |
| Headers | `X-Role`, `X-User-Id`, `X-Staff-Id`, `X-Forwarded-User`, `X-Admin` | Never trusted for app authorization. |

## Route Results

| Route | Actor | Tampering vector | Expected result | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `/api/staff/bookings/schedule/` | customer | role/admin query + role headers | 403, no staff schedule payload | `tests/security/test_role_tampering.py::test_role_headers_and_query_params_do_not_widen_staff_portal_authorization` | covered |
| `/api/staff/bookings/<id>/` | customer | role/admin/staff headers | 403, no booking data | `tests/security/test_bola_idor_staff_objects.py::test_non_staff_customer_cannot_use_headers_or_query_to_access_staff_booking_detail` | covered |
| `/api/checkout/sessions/<id>/` | other customer | `X-User-Id`, `X-Role`, `X-Forwarded-User` | 404, no checkout data | `tests/security/test_role_tampering.py::test_untrusted_identity_headers_do_not_change_checkout_object_owner` | covered |
| `/api/checkout/sessions/<id>/mpesa/stk/` | other customer | identity/role headers | 404, no STK attempt | `tests/security/test_bola_idor_customer_objects.py::test_customer_cannot_read_or_initiate_another_customers_checkout_with_tampered_identity` | covered |
| `/api/gallery/public/categories/<slug>/` | anonymous | `include_private=true`, `scope=all`, `owner_id` | public-only output, no storage keys/unpublished titles | `tests/security/test_query_scope_tampering.py::test_public_gallery_query_scope_cannot_include_private_or_storage_fields` | covered |
| `/api/staff/bookings/schedule/` | customer | `customer_id`, `include_private=true`, `scope=all` | 403, no staff schedule payload | `tests/security/test_query_scope_tampering.py::test_staff_schedule_query_scope_tampering_does_not_bypass_authentication` | covered |

## Findings

No confirmed role/header/query tampering defect was found in Phase 3B tests.

## Notes

- Staff booking views are currently staff-global by design after a user has an
  active staff session and the required permission. Phase 3B did not invent
  per-beautician row ownership where no assignment model exists.
- If future per-beautician scoping is added, this matrix must be updated with
  Staff A / Staff B cross-object tests.
