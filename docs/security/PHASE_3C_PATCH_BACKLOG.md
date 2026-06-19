# Phase 3C Response Privacy Patch Backlog

Production readiness: **rejected / not claimed**.

## Summary

One confirmed high response privacy exposure was found and patched narrowly
during this Phase 3C implementation pass.

Runtime patch status: **one narrow storage presentation patch applied**.

## Backlog Items

| ID | Severity | Route | Actor | Category | Observed behavior | Recommended action | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3C-HIGH-001 | High | `/api/gallery/public/*` | anonymous | storage/media metadata | Public gallery variant URL was built by concatenating the raw storage key under the public base URL, exposing storage path structure. | Patched `public_variant_url()` to return deterministic opaque public handles and updated tests to forbid raw storage path exposure. | Closed |
| 3C-MED-001 | Medium | checkout owner routes | authenticated owner | response contract documentation | Owner-scoped checkout UUID is intentionally exposed as `id` or `checkout_public_id` for flow recovery. This is safe only because Phase 3B owner/token checks exist. | Keep documented route-specific exception; do not expose provider IDs or ledger IDs. Revisit if public checkout URLs are added. | Tracked |
| 3C-LOW-001 | Low | STK initiation response | authenticated owner | coverage precision | Existing tests cover permissions/throttling, but Phase 3C did not add a direct fake-provider STK response privacy test to avoid provider side effects in this phase. | Add a fake-provider-only direct STK response privacy test in a later abuse/rate-limit phase. | Deferred |

## Patch Rules For Future Findings

Critical/high findings require a narrow patch with tests before release. Safe
patch options include:

- dedicated route response serializers;
- explicit serializer field lists;
- `write_only=True` for sensitive input fields;
- redacted presentation fields;
- generic error response shaping;
- removal of storage/provider/ledger internals from public or customer routes.

Forbidden patch style:

- broad serializer rewrites;
- booking lifecycle changes;
- checkout/billing financial truth changes;
- staff policy changes without product approval;
- hiding findings by weakening denylist tests.
