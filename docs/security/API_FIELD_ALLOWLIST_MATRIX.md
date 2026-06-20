# API Field Allowlist Matrix

Production readiness: **rejected / not claimed**.

This matrix documents intended response fields for high-risk API response
classes. Authorization controls from Phase 3B decide who may reach a route;
this matrix decides what the allowed actor may receive.

## Public Routes

Allowed:

- health status: `status`;
- catalog/service/package display data needed for selection;
- legal document publication fields;
- public gallery display fields;
- random opaque public optimized variant UUID URL, dimensions, format, and size.

Forbidden:

- customer PII;
- staff private fields;
- payment state internals;
- provider references;
- storage keys and private buckets;
- raw payloads;
- debug/internal fields.

Evidence:

- `tests/security/test_response_privacy_gallery.py`
- Docker Newman response privacy assertions

## Public Booking Intent Routes

Allowed:

- `booking_public_id`;
- `status`;
- `hold_expires_at`;
- `starts_at`;
- `ends_at`;
- `selection`;
- `next_action`;
- `hold_ttl_minutes`;
- safe amount/currency only where needed for checkout.

Forbidden:

- raw customer phone/email/name in hold/status responses;
- ledger IDs;
- provider identifiers;
- raw payment payloads;
- staff fields;
- server debug fields.

Evidence:

- `tests/security/test_response_privacy_booking.py`

## Booking Checkout Bridge

Allowed:

- `booking_public_id`;
- `status_url`;
- `status_api_url`;
- `checkout_public_id`;
- `booking_status`;
- `payment_status`;
- `amount`;
- `currency`;
- `next_action`.

Route-specific exception:

- `checkout_public_id` is an opaque owner/booking-token scoped checkout session
  UUID. It is allowed only as the next-action handle for the checkout flow and
  must not carry provider or ledger truth.

Forbidden:

- ledger internals;
- provider request IDs;
- raw provider payloads;
- raw customer PII;
- hidden booking state internals.

## Customer-Owned Checkout Routes

Allowed:

- `id` for the owner-scoped checkout session;
- `status`;
- `amount` on owner detail;
- `attempt_id` and attempt status on STK initiation if owner-scoped.

Forbidden:

- ledger ID;
- merchant request ID;
- checkout request ID;
- M-Pesa receipt;
- raw callback/provider payload;
- raw phone number;
- unrelated booking/customer fields.

Evidence:

- `tests/security/test_response_privacy_checkout_billing.py`
- fake-provider direct STK response privacy test (`attempt_id`, `status` only)

## Provider And Legacy Billing Routes

Allowed:

- generic accepted status on checkout webhook;
- generic deprecation detail on disabled legacy billing routes.

Forbidden:

- raw provider payload echo;
- checkout request ID;
- merchant request ID;
- M-Pesa receipt;
- ledger ID;
- phone/email;
- stack traces.

Evidence:

- `tests/security/test_response_privacy_checkout_billing.py`
- `tests/security/test_response_privacy_errors.py`

## Staff Routes

Allowed under current product policy:

- operational booking schedule fields;
- safe customer display name;
- `contact_redacted` availability markers;
- booking status and payment status;
- redacted staff payment summary.

Contact reveal exception:

- `phone` and `email` are allowed only on the audited staff contact reveal
  route after staff permission, active session, recent reauth, and reason.

Forbidden:

- raw provider payloads;
- raw ledger IDs;
- checkout internals;
- auth/session tokens;
- storage keys;
- audit internals;
- unrelated customer PII.

Evidence:

- `tests/security/test_response_privacy_staff.py`

## Gallery And Media Routes

Allowed:

- public image ID;
- title and description after sanitization;
- category/subcategory display fields;
- random opaque public optimized variant UUID URL/dimensions/format/size;
- warning/sensitivity flags that are part of public display policy.

Forbidden:

- quarantine key;
- original private key;
- storage key;
- private bucket/path;
- hash values;
- staff owner internals;
- draft/private image metadata.

Evidence:

- `tests/security/test_response_privacy_gallery.py`
- `tests/security/test_public_gallery_variant_url_privacy.py`

## Phase 3C Final Confirmation

The 2026-06-20 local all-passive closeout reported zero sensitive-marker hits.
This confirms that the allowlist remains coupled to opaque gallery handles,
generic media denial responses, and the fake-provider STK response contract;
it does not authorize provider, storage, or production traffic.

## Error And Denial Responses

Allowed:

- generic `detail`;
- generic `status`;
- safe validation message.

Forbidden:

- stack traces;
- exception classes;
- SQL/database details;
- request payload echo;
- object existence details where inappropriate;
- PII;
- tokens;
- provider payloads;
- checkout/ledger IDs;
- storage keys.

Evidence:

- `tests/security/test_response_privacy_errors.py`
