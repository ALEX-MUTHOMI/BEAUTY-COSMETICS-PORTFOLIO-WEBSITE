# Configuration Architecture

This project currently uses a centralized Django settings module in
`core/settings.py`. Configuration changes must preserve fake-provider defaults
for local, test, and normal CI execution.

## Safety Rules

- Default provider mode must not call real Daraja, email providers, or R2.
- Real Daraja sandbox tests must remain opt-in with `--run-external`.
- Secrets must come from environment variables only.
- Daraja credentials, email provider keys, R2 credentials, and payment tokens
  must never be exposed through frontend or `NUXT_PUBLIC_*` variables.
- Staging and production env files must remain untracked.
- Committed env examples may contain placeholders only.

## Current Settings Ownership

| Area | Owner | Notes |
| --- | --- | --- |
| Django security flags | `core/settings.py` | `DEBUG`, hosts, CSRF/CORS, secure proxy and admin-gating flags |
| Celery/Redis | `core/settings.py` | Queue names and broker URLs come from env |
| Checkout/Billing providers | `core/settings.py` and app adapters | Fake provider is the safe default for tests and CI |
| External Daraja sandbox | `tests/external/` and management command | Must be run explicitly, never during default pytest |

## Deferred Split

A settings package split (`core/settings/base.py`, `local.py`, `test.py`,
`staging.py`, `production.py`) is intentionally deferred. It has a broad blast
radius and should be done only with full Docker regression, Newman/API checks,
and secret-hygiene gates.
