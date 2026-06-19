# Phase 3C Response Privacy Report

## Executive Verdict

`PHASE 3C DISCOVERY ACCEPTED WITH FINDINGS - HIGH STORAGE KEY EXPOSURE PATCHED`

Production readiness: **REJECTED / NOT CLAIMED**.

## Scope

Route groups assessed:

- public health, CSRF, catalog, legal, availability, gallery;
- booking hold, checkout bridge, and public status token responses;
- checkout create/detail, webhook, and disabled legacy billing responses;
- staff booking detail, staff payment summary, contact reveal, and contact
  denial responses;
- common malformed, denied, disabled, and unknown-route errors.

## Field Allowlist Result

Allowlist policy is documented in
`docs/security/API_FIELD_ALLOWLIST_MATRIX.md`.

Route-specific exceptions:

- `checkout_public_id` and checkout detail `id` are allowed only as
  owner/token-scoped opaque checkout handles.
- staff contact reveal may return `phone` and `email` only after staff
  permission, active session, recent reauth, reason, and audit.
- public gallery may return public optimized variant URLs, not private storage
  keys.
- CSRF bootstrap may return the CSRF token by design; this exception does not
  apply to unrelated routes.

## Sensitive Field Exposure Result

One high exposure was found in public gallery media URLs and patched narrowly.

| Category | Result |
| --- | --- |
| PII | Public booking status and hold/checkout bridge responses do not expose known raw test phone/email values. Staff contact reveal is the intentional audited exception. |
| Auth/session | Response tests deny password/session/token/passkey/secret marker categories outside documented bootstrap behavior. |
| Checkout/billing/provider | Webhook and disabled billing responses do not echo provider IDs, raw payloads, ledger IDs, or receipts. |
| Receipt/status token | Public status response exposes only the booking reference and safe status/read-model fields. |
| Storage/media | Public gallery response no longer exposes raw storage key paths in variant URLs. Quarantine keys, original private keys, hashes, private paths, and draft images remain hidden. |
| Internal/debug | Error responses do not expose stack traces, database details, exception classes, or object internals in the tested paths. |

## Domain Results

Booking:

- hold response is minimized;
- checkout bridge returns only next-action/payment display fields;
- public status token remains zero-PII;
- invalid status token is generic and non-reflective.

Checkout/Billing:

- checkout owner responses remain small and owner-scoped;
- cross-customer denial does not leak amount, private purchasable ID, or owner
  identity;
- webhook responses are generic and do not echo provider evidence;
- disabled legacy billing routes remain non-reflective `410` responses.

Staff:

- booking detail exposes operational schedule/payment-state fields only;
- payment summary exposes redacted provider reference state only;
- contact reveal intentionally returns contact fields through audited staff
  flow;
- denied contact reveal is generic and contains no raw contact values.

Gallery/Media:

- public gallery exposes only published public variants;
- draft/private image metadata remains hidden;
- staff category navigation does not expose upload/storage internals.

Errors:

- invalid tokens, unknown routes, malformed booking JSON, malformed webhook
  payload, and unsupported method responses do not expose sensitive categories
  in the tested cases.

## Findings

Critical: none confirmed.

High:

- `3C-HIGH-001`: public gallery variant URL exposed raw storage path structure.
  Patched by generating deterministic opaque public handles in
  `public_variant_url()` and updating tests to assert the raw storage key is not
  present.

Medium:

- `3C-MED-001`: owner-scoped checkout UUIDs are intentionally exposed as flow
  handles. This remains acceptable only because Phase 3B owner/token controls
  are enforced and documented.

Low:

- `3C-LOW-001`: direct STK initiation response privacy can receive a
  fake-provider-only test in a later phase; existing permissions/throttle tests
  still cover the route.

## Verification Plan

Phase 3C verification should include:

- `pytest tests/security -q`;
- API/security partition;
- booking partition;
- checkout/billing partition;
- unit/integration partition;
- Docker Newman;
- Turbo Pass;
- Django check and migration drift;
- lint/security and secret hygiene;
- Docker health and worker ping.

## No Production Readiness Claim

This phase improves response privacy evidence only. Production readiness remains
rejected until staging, operational monitoring, incident response, live payment
canary, and release enforcement are complete.
