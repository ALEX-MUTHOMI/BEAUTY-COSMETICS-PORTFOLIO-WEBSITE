# Phase 3C Response Privacy Report

## Executive Verdict

`PHASE 3C-FINAL-E ACCEPTED — PHASE 3C FULLY CLOSED`

Production readiness: **REJECTED / NOT CLAIMED**.

> Phase 3X hold (2026-06-20): Phase 3C was accepted from completed evidence,
> but persistent security-matrix instability requires revalidation after the
> root-cause fix. This is not evidence of a confirmed privacy regression.

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
  fake-provider-only response privacy test. Closed in Phase 3C-PV with a test
  proving the STK response contains only an owner-scoped attempt ID and status.

## Public Gallery Variant URL Privacy Verification

`3C-HIGH-001` was re-verified in Phase 3C-PV and the original HMAC-only URL
patch was strengthened because it did not provide a controlled media resolver.

- Public gallery URLs now use the existing random `GalleryImageVariant.public_id`
  UUID, not a storage key or a deterministic transform of one.
- `public_variant_url()` accepts only a UUID public handle plus a validated image
  extension; raw storage keys are rejected.
- `/media/public/<variant-uuid>.<format>` resolves only when the variant is
  `is_public=True` and its image is `PUBLISHED`.
- The resolver streams the internal storage object only after that database
  policy check. Unknown, malformed, archived, draft, quarantined, failed, and
  non-public variants receive generic `404` responses.
- Public responses remain stable for a variant, differ for different variants,
  contain no raw storage path, bucket, original upload, quarantine, or hash.
- Public media caching is bounded to five minutes; URLs are not marked
  immutable so archiving can revoke access promptly.

Deployment note: when `GALLERY_PUBLIC_BASE_URL` is absolute, its origin must
route `/media/public/*` to this resolver or an equivalent policy-enforcing
media service. A CDN must never map opaque handles directly to private storage
keys.

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

## Final Passive Security And Hygiene Closeout

On 2026-06-20, the local-only final closeout ran:

```powershell
.\scripts\ci\run_security_passive_gate.ps1 -Mode all-passive
```

- Duration: 502 seconds.
- Health, root, OpenAPI, and Newman-through-ZAP passive modes completed.
- Every mode reported `FAIL-NEW=0` and `ZAP_SENSITIVE_MARKER_HITS=0`.
- HTML, Markdown, and JSON reports were present and non-empty for every mode.
- Newman-through-ZAP completed 30 requests, 91 assertions, and 0 failures.
- Project-owned ZAP containers were cleaned up; none remained after the run.
- The default runtime was restored: Docker services were healthy, Celery returned
  `pong`, and `/api/schema/` returned `404` when evaluated in its HTTPS request
  context.
- Recent web, worker, db, redis, frontend, and frontend-test logs had no
  traceback, internal-error, storage, provider, token, secret, or PII-value
  leaks. A worker `email` label was a static marker with no address-shaped
  value.
- Generated reports, local `.env`, and local SQLite data remain ignored and
  untracked. Host Git hygiene returned `GIT_SECRET_MARKER_FILE_COUNT=0`.

The only passive warnings were existing low/informational items: CSRF cookie
non-HttpOnly policy, expected client/error responses in schema placeholders,
and cacheability observations. They are non-blocking and contain no sensitive
marker hit. No active or full ZAP scan was used.

## Phase 3C Closeout

`3C-HIGH-001 CLOSED — public gallery storage-key exposure eliminated and verified.`

The public gallery uses opaque variant UUID handles, its resolver allows only
published/public variants, and malformed, unknown, private, draft,
quarantined, failed, or unpublished handles receive generic `404` responses.
The frontend accepts backend `/media/public/...` paths only and rejects raw
storage-style or external URLs. Fake-provider direct STK initiation returns
only `attempt_id` and `status`.

Next planned work: **PHASE 3D — Rate-limit / Abuse / Throttling Inventory**.

## No Production Readiness Claim

This phase improves response privacy evidence only. Production readiness remains
rejected until staging, operational monitoring, incident response, live payment
canary, and release enforcement are complete.
