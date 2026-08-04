# Sensitive Field Denylist

Production readiness: **rejected / not claimed**.

This document defines response-field categories that must be forbidden or
explicitly justified per route. It is a test guide, not a blind global rule:
some routes intentionally expose safe public identifiers or audited staff
contact fields.

## PII

Controlled or forbidden by route:

- raw phone numbers;
- raw email addresses;
- full customer name on zero-PII public/token routes;
- staff contact details outside staff auth/session contracts;
- address or location fields if added later;
- free-form notes that may contain personal information.

## Authentication, Session, And Security

Forbidden in API responses unless the route explicitly exists to provide a
safe browser bootstrap value:

- password or password hash;
- OTP or verification code;
- session ID;
- access token;
- refresh token;
- API key;
- secret;
- passkey;
- reset token;
- verification token;
- token hash.

CSRF bootstrap may return the CSRF token by design; non-CSRF routes must not
echo CSRF/session values.

## Payment And Provider Metadata

Forbidden unless explicitly justified and owner-scoped:

- ledger ID;
- billing ledger ID;
- provider reference hash;
- merchant request ID;
- checkout request ID;
- M-Pesa receipt number;
- raw Daraja payload;
- callback payload;
- provider payload;
- raw payment attempt payload;
- provider status internals.

Current route-specific exception: customer-owned checkout routes expose an
opaque owner-scoped checkout session UUID as `id` or `checkout_public_id`.
This is allowed only with owner lookup or possession of a held booking token.

## Storage And Media

Forbidden from public and customer responses:

- storage key;
- private bucket;
- private object path;
- raw R2 path;
- quarantine key;
- original private key;
- signed URL internals;
- SHA-256 hashes;
- EXIF GPS or device metadata;
- internal processing metadata.

Public gallery responses may expose public optimized variant URLs only.

Public variant URL policy:

- URLs must use random variant identifiers, not a hash, encoding, slug, or
  derivation of a storage key.
- The public resolver must enforce `PUBLISHED` image state and `is_public`
  variant state before reading internal storage.
- CDN or reverse-proxy configuration must route public handles through the same
  policy or an equivalent access-controlled mapping.

## Internal And Debug Fields

Forbidden in external API responses:

- database ID where not explicitly part of an authenticated owner contract;
- owner ID;
- user ID;
- staff ID;
- internal ID;
- deleted flags;
- debug flags;
- audit IDs;
- exception class names;
- stack traces;
- SQL/database error details;
- model `__dict__` or `_state`.

## Error Response Rule

Error and denial responses may return a generic safe message or safe error
code. They must not reveal object ownership, private object existence, internal
state-machine details, provider identifiers, raw payloads, tokens, PII, storage
keys, or stack traces.

## Phase 3C Final Verification

The local all-passive closeout on 2026-06-20 reported zero sensitive-marker
hits across health, root, OpenAPI, and Newman-through-ZAP reports. The final
recent-log scan found no real sensitive value leakage; one worker `email` label
had no address-shaped value and was classified as a safe static marker.
