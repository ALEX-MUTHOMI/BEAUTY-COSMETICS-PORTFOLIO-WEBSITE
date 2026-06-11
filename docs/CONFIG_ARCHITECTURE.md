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

## Root File Ownership

| Path | Purpose | Root status | Security/pipeline decision |
| --- | --- | --- | --- |
| `.dockerignore` | Docker build exclusion rules | Keep at root | Excludes env/cache/local DB artifacts from images |
| `.env` | Local real environment | Must stay untracked | Ignored by `.gitignore`; never commit values |
| `.env.example` | Local placeholder contract | Keep at root | Placeholder-only values; safe to track |
| `.env.staging.example` | Staging placeholder contract | Keep at root | Placeholder-only values; safe to track |
| `.flake8` | Lint config | Keep at root | Tool expects root config |
| `.gitignore` | Git artifact protection | Keep at root | Protects env files, SQLite DBs, logs, reports, media, uploads |
| `.pre-commit-config.yaml` | Hook config | Keep at root | Tool expects root config |
| `Caddyfile.staging` | Restricted staging reverse proxy | Keep for now | May move to `deploy/` only with Compose/docs updates |
| `conftest.py` | Global pytest options and safe autouse fixtures | Keep small at root | External tests remain opt-in; shared fixture extraction deferred |
| `db.sqlite3` | Local SQLite fallback artifact | Must stay untracked | Removed from Git tracking; ignored going forward |
| `docker-compose*.yml` | Local/staging Docker orchestration | Keep at root | Moving would break documented commands |
| `Dockerfile` | Backend image build | Keep at root | Compose/CI reference root Dockerfile |
| `manage.py` | Django command entrypoint | Keep at root | Django convention/tool expectation |
| `poetry.lock`, `pyproject.toml` | Python dependency/tool config | Keep at root | Poetry expects root project files |
| `pytest.ini` | Pytest marker/settings config | Keep at root | Pytest expects root config |
| `README.md` | Repo overview | Keep at root | Human entrypoint |
| `requirements.txtcd` | Accidental zero-byte typo artifact | Removed | No references found; Poetry remains canonical |

## Production Fail-Closed Checks

- `ALLOWED_HOSTS` defaults to explicit local/test hosts only.
- `DEBUG=False` with `ALLOWED_HOSTS=*` raises `ImproperlyConfigured`.
- Docker Compose local defaults use explicit `localhost`, `127.0.0.1`,
  `0.0.0.0`, `web`, and `testserver` rather than wildcard hosts.
- Local Newman fake-webhook testing allows Docker bridge CIDRs only in the
  local Compose/default env path. Staging keeps the stricter Safaricom CIDR
  example.

## Deferred Split

A settings package split (`core/settings/base.py`, `local.py`, `test.py`,
`staging.py`, `production.py`) is intentionally deferred. It has a broad blast
radius and should be done only with full Docker regression, Newman/API checks,
and secret-hygiene gates.
