# Phase 3B Mass Assignment Matrix

Production readiness: **rejected / not claimed**.

This matrix records server-owned fields tested against public/customer payment
and booking endpoints. The expected policy is endpoint-specific: dangerous
fields may be rejected, ignored, or overwritten by authenticated server-side
identity, but must not take effect.

## Dangerous Fields

| Field group | Fields | Expected policy |
| --- | --- | --- |
| Ownership | `id`, `user`, `user_id`, `customer`, `customer_id`, `owner`, `owner_id` | Reject/ignore/overwrite with authenticated or server-derived owner. |
| Staff/admin role | `role`, `is_staff`, `is_superuser`, `permissions`, `groups`, `staff`, `staff_id` | Never client-authoritative. |
| Tenant/scope | `business`, `business_id`, `tenant`, `tenant_id`, `org`, `org_id` | Never widen scope. |
| Booking lifecycle | `status`, `booking_status`, `contact_revealed`, `created_by`, `approved_by` | Only domain service/state machine may set. |
| Payment truth | `payment_status`, `is_paid`, `amount`, `currency`, `provider`, `provider_status`, `provider_reference`, `checkout_id`, `ledger_id`, `receipt_token` | Payment truth is checkout/provider/billing controlled. |
| Media/storage | `is_private`, `storage_key`, `image_url` | Upload pipeline/storage service controlled. |

## Endpoint Results

| Endpoint | Hostile fields tested | Expected behavior | Evidence | Result |
| --- | --- | --- | --- | --- |
| `POST /api/bookings/holds/` | `amount`, `currency`, `total_amount` | Reject client price tampering. | `tests/security/test_mass_assignment.py::test_booking_hold_rejects_client_price_mass_assignment` | covered |
| `POST /api/bookings/holds/` | `status`, `booking_status`, `payment_status`, `is_paid`, `is_staff`, `role`, `customer_id` | Ignore server-owned lifecycle/role fields and create only HELD booking. | `tests/security/test_mass_assignment.py::test_booking_hold_ignores_server_owned_status_and_role_fields` | covered |
| `POST /api/bookings/checkout/` | `payment_status`, `status`, `is_paid`, `amount`, `currency`, `provider_reference`, `ledger_id` | Ignore/reject payment truth tampering; mark booking payment pending only; no ledger success. | `tests/security/test_mass_assignment.py::test_booking_checkout_bridge_ignores_payment_truth_mass_assignment` | covered |
| `POST /api/checkout/sessions/` | `customer`, `customer_id`, `user_id`, `status`, `is_staff`, `is_superuser`, `provider_reference` | Owner is authenticated user; status remains CREATED; role fields do not mutate user. | `tests/security/test_mass_assignment.py::test_checkout_session_create_derives_owner_from_authenticated_user_not_payload` | covered |
| `POST /api/checkout/sessions/` | `status`, `payment_status`, `provider_status`, `provider_reference`, `checkout_id`, `ledger_id`, `receipt_token`, `is_paid` | Direct checkout create cannot create paid state or billing ledger. | `tests/security/test_status_payment_tampering.py::test_direct_checkout_create_cannot_mass_assign_paid_or_provider_state` | covered |
| `POST /api/billing/stk-push/` | payment/provider/status fields | Legacy billing STK route remains disabled with 410. | `tests/security/test_status_payment_tampering.py::test_disabled_billing_stk_endpoint_does_not_accept_client_payment_truth` | covered |
| `POST /api/staff/gallery/images/` | storage/internal media fields | Existing upload pipeline controls storage keys and validation. | gallery upload/security tests | covered existing |
| staff auth/reset routes | role fields | Existing staff auth only accepts credential/reset contract; role fields are not authoritative. | staff auth tests plus role tampering tests | covered existing |

## Findings

No confirmed critical/high mass-assignment defect was found in Phase 3B tests.

## Follow-Up

- Add Newman negative payload cases for the same dangerous fields where useful
  without increasing flakiness.
- Keep serializer-level field allowlists aligned with this matrix during future
  endpoint additions.
