# Identifier and Indirect Reference Policy

Production readiness: **rejected / not claimed**.

This policy closes Phase 3B-C control 2: public-facing identifiers must be
indirect, non-sequential, tokenized, or protected by strong server-side
authorization.

## Identifier Classes

| Class | Examples | Policy | Evidence |
| --- | --- | --- | --- |
| Internal DB IDs | `Booking.id`, `LedgerTransaction.id`, internal FK values | Internal only. If ever routed externally, must be protected by server-side authorization and must not leak on denial. | BOLA/security tests assert internal IDs are absent from status/payment responses. |
| Public booking status tokens | `Booking.public_id` in `/api/bookings/status/<id>/` | Random UUID public token, zero-PII response, generic invalid/missing denial. | `test_public_booking_status_token_is_public_safe_but_does_not_reveal_private_owner_data`, `test_invalid_and_missing_booking_status_tokens_are_indistinguishable_and_generic`. |
| Checkout session UUIDs | `/api/checkout/sessions/<uuid>/` | Direct UUID is accepted only after authenticated owner-scoped lookup. Other users receive `404`. | `test_customer_cannot_read_or_initiate_another_customers_checkout_with_tampered_identity`. |
| Provider identifiers | checkout request ID, merchant request ID, receipt | Stored hashed/redacted where required; never accepted as user authority; webhook must pass provider/state validation. | checkout webhook, redaction, and billing tests. |
| Gallery/media identifiers | category slug, image public IDs, storage keys | Public routes expose only published/optimized public data. Private storage keys remain server-side. | gallery public/privacy/query tests. |
| Remembered-device tokens | opaque device cookie token | Raw token stored hashed and returns redacted convenience data only. | remembered-device token tests. |
| Disabled legacy payment identifiers | legacy billing STK/webhook payload fields | Route remains disabled. Payload identifiers must not be reflected or processed. | Phase 3B and 3B-C disabled-route tests. |

## Safety Requirements

- Public tokens must be non-sequential and generic on invalid/missing lookup.
- Direct IDs require authenticated ownership or explicit permission checks.
- Client-submitted owner, role, status, or payment identifiers are never
  authorization facts.
- Disabled legacy routes must remain safe even if attacker satisfies preliminary
  permission/IP conditions.
- Response bodies must not expose checkout IDs, ledger IDs, provider payloads,
  storage keys, raw tokens, phone numbers, or emails unless the route explicitly
  exists to reveal a redacted/authorized value.

## Medium Follow-Up Closure

Phase 3B follow-up `3B-FU-001` is now covered by
`tests/security/test_authorization_control_closeout.py::test_disabled_legacy_billing_webhook_returns_410_after_ip_allowlist_accepts_request`.
The test configures a local allowlisted source and proves the legacy billing
webhook still returns `410` without reflecting provider identifiers.

## Phase 3B-F Verification

Phase 3B-F re-verified identifier safety with targeted BOLA/IDOR tests, the
full Booking partition, Docker Newman API acceptance, and Turbo Pass. No public
contract was expanded to expose internal IDs, provider identifiers, ledger IDs,
receipt tokens, storage keys, raw phone numbers, or raw email addresses.
