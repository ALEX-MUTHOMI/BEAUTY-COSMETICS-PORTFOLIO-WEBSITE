# Phase 3C Response Privacy Patch Backlog

Phase 3C status: **fully closed on 2026-06-20**.

Production readiness: **rejected / not claimed**.

## Summary

One confirmed high response privacy exposure was found and patched narrowly
during this Phase 3C implementation pass.

Runtime patch status: **one narrow storage presentation patch applied**.

## Backlog Items

| ID | Severity | Route | Actor | Category | Observed behavior | Recommended action | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3C-HIGH-001 | High | `/api/gallery/public/*`, `/media/public/*` | anonymous | storage/media metadata | Public gallery variant URL was built by concatenating the raw storage key under the public base URL, exposing storage path structure. | Closed in 3C-PV: random variant UUID handle, published/public-only resolver, raw-key rejection, collision/stability/API tests, and bounded revocable caching. | Closed |
| 3C-MED-001 | Medium | checkout owner routes | authenticated owner | response contract documentation | Owner-scoped checkout UUID is intentionally exposed as `id` or `checkout_public_id` for flow recovery. This is safe only because Phase 3B owner/token checks exist. | Keep documented route-specific exception; do not expose provider IDs or ledger IDs. Revisit if public checkout URLs are added. | Tracked |
| 3C-LOW-001 | Low | STK initiation response | authenticated owner | coverage precision | Existing tests covered permissions/throttling but not the direct response shape. | Closed in 3C-PV with a fake-provider-only test that denies phone and Daraja identifiers from the response. | Closed |

## Final Closeout Evidence

`PHASE 3C-FINAL-E ACCEPTED — PHASE 3C FULLY CLOSED` after the local
all-passive scan completed in 502 seconds with `FAIL-NEW=0`, zero sensitive
marker hits, non-empty reports, and scanner cleanup. Final log/artifact hygiene
and host Git hygiene also passed (`GIT_SECRET_MARKER_FILE_COUNT=0`).

No critical or high Phase 3C response-privacy item remains open. `3C-MED-001`
remains a documented product-contract constraint, not an unresolved leak.

Next phase: **PHASE 3D — Rate-limit / Abuse / Throttling Inventory**.

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
