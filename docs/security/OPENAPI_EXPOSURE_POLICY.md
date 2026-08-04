# OpenAPI Exposure Policy

OpenAPI is a security-sensitive inventory surface. It can help OWASP ZAP and
contract tooling, but it can also reveal routes and internal concepts if exposed
carelessly.

## Runtime Policy

- Default runtime: `ENABLE_OPENAPI_SCHEMA=False`.
- Default route result: `/api/schema/` returns `404`.
- Local security-scan profile: `ENABLE_OPENAPI_SCHEMA=True`.
- Production/staging exposure is not approved by default.

The schema endpoint is intended for local passive scanning and API contract
verification unless a separate deployment decision approves it.

## Sensitive-Surface Controls

The schema builder:

- filters routes to a curated safe API inventory;
- excludes admin routes;
- excludes legacy/internal payment identifiers where possible;
- redacts banned sensitive markers from generated strings.

Tests assert that the schema does not expose categories such as passkeys,
consumer secrets, access tokens, refresh tokens, session IDs, receipt tokens,
checkout IDs, ledger IDs, merchant request details, provider payloads, raw
callbacks, storage keys, private buckets, phone/email query markers, password
markers, token hashes, or generic secrets.

## ZAP Usage

Use safe/passive API scanning only:

```powershell
.\scripts\security\zap_baseline_local.ps1 -Mode api -MaxMinutes 10
```

Do not run active API scanning against local, staging, or production without a
separate approved test plan.

## Remaining Work

Phase 3B should add object-authorization and role-tampering checks against the
API inventory. Any new endpoint must be reviewed before inclusion in the schema.
