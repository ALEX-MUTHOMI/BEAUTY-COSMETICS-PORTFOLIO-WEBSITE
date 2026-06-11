# B8A Refactor Map — Visible Backend Reorganization

## Phase 2C-B8A Execution Date
2026-06-10

## Summary
Reorganized `bookings/` from a flat service directory into a modular-monolith
layered structure: `domain/`, `selectors/`, `infrastructure/`, and `services/`.

## Layering Convention

| Layer              | Import Path                    | Purpose                                      | ORM Access | Side Effects |
|--------------------|--------------------------------|----------------------------------------------|------------|--------------|
| `domain/`          | `bookings.domain.*`           | Pure business rules (no I/O, no ORM)         | ❌          | ❌            |
| `selectors/`       | `bookings.selectors.*`        | Read-only queries + presentation logic       | ✅ Read     | ❌            |
| `infrastructure/`  | `bookings.infrastructure.*`   | External provider / storage adapters         | ❌          | ✅ (external) |
| `services/`        | `bookings.services.*`         | Mutation workflows, orchestration            | ✅ R+W      | ✅            |
| `api/`             | `bookings.api.*`              | Thin HTTP adapters (views → services)        | ❌ (delegate) | ❌         |

## File Movement Table

### Moved to `bookings/domain/` (Pure Business Rules)

| Before                                | After                                  | Reason                         |
|---------------------------------------|----------------------------------------|--------------------------------|
| `bookings/services/circuit_breaker.py` | `bookings/domain/circuit_breaker.py`  | Redis-backed, no Django ORM    |
| Day-policy rule helpers in `bookings/services/day_policy.py` | `bookings/domain/day_policy.py` | Deterministic weekday/window validation helpers only |

**Not moved** (failed purity check — use Django ORM writes):
- `services/day_policy.py` — canonical ORM-backed policy lookup, `transaction.atomic`, `select_for_update`, `BookingDayState.objects`
- `services/state_machine.py` — `transaction.atomic`, `Booking.objects.select_for_update`, `BookingAuditEvent.objects.create`
- `services/policy.py` — `BusinessHours.objects.filter()`

### Moved to `bookings/selectors/` (Read-Only Queries)

| Before                                  | After                                       | Reason                              |
|-----------------------------------------|---------------------------------------------|---------------------------------------|
| `bookings/views.py` (7 inline functions) | `bookings/selectors/booking_status.py`     | Status presentation / selector logic  |
| `bookings/services/catalog.py`          | `bookings/selectors/public_catalog.py`      | Re-export of read-only catalog queries |
| `bookings/services/public_lookup.py`    | `bookings/selectors/public_lookup.py`       | Read-only booking lookup              |
| `bookings/services/gallery_public.py`   | `bookings/selectors/gallery_public.py`      | Read-only gallery queries (verified)  |

### Moved to `bookings/infrastructure/` (Provider/Storage Adapters)

| Before                                   | After                                          | Reason                              |
|------------------------------------------|------------------------------------------------|---------------------------------------|
| `bookings/services/email_provider.py`    | `bookings/infrastructure/email_provider.py`    | Email provider (Resend/Mailgun/Fake)  |
| `bookings/services/gallery_storage.py`   | `bookings/infrastructure/gallery_storage.py`   | Local/R2 object storage adapter       |
| `bookings/services/receipt_pdf.py`       | `bookings/infrastructure/receipt_pdf.py`       | PDF generation infrastructure         |

## Compatibility Wrappers

All old import paths remain functional via zero-logic wrappers in `bookings/services/`:

```python
# Example: bookings/services/email_provider.py
# Compatibility wrapper. Canonical implementation lives in bookings.infrastructure.email_provider.
from bookings.infrastructure.email_provider import *  # noqa: F401,F403
```

### Wrapper Index

| Old Path                              | Redirects To                                  |
|---------------------------------------|-----------------------------------------------|
| `bookings.services.circuit_breaker`   | `bookings.domain.circuit_breaker`             |
| `bookings.services.catalog`           | `bookings.selectors.public_catalog`           |
| `bookings.services.public_lookup`     | `bookings.selectors.public_lookup`            |
| `bookings.services.gallery_public`    | `bookings.selectors.gallery_public`           |
| `bookings.services.email_provider`    | `bookings.infrastructure.email_provider`      |
| `bookings.services.gallery_storage`   | `bookings.infrastructure.gallery_storage`     |
| `bookings.services.receipt_pdf`       | `bookings.infrastructure.receipt_pdf`         |

`bookings.services.day_policy` is intentionally not a wrapper. It remains the
canonical service for ORM-backed day-policy lookup and capacity locking. Pure
weekday/window helpers live in `bookings.domain.day_policy`.

## What Was NOT Changed

| Item                    | Reason                                                       |
|-------------------------|--------------------------------------------------------------|
| `models.py` split       | Migration surgery risk — requires dedicated subphase         |
| Staff sub-package       | High import churn (12 URL routes + 30+ staff tests)          |
| Gallery sub-package     | Deep coupling to models                                      |
| Test file relocation    | 168 test files with inter-file imports                       |
| `checkout/` and `billing/` | Already well-structured as separate Django apps           |

## Root Cleanup

| Path | Decision | Reason |
| --- | --- | --- |
| `requirements.txtcd` | Removed | Zero-byte typo artifact; no references found; Poetry remains canonical |
| `Caddyfile.staging` | Kept at root | `docker-compose.staging.yml` mounts it directly; moving requires a dedicated deployment-reference update |
| `docker-compose*.yml` | Kept at root | Documented Docker commands and CI/local workflows expect root Compose files |

## Before/After Tree

### Before
```
bookings/
├── api/
│   ├── __init__.py
│   └── public_views.py
├── services/           ← 28 files, mixed concerns
│   ├── availability.py
│   ├── bundles.py
│   ├── catalog.py          ← selector (re-export)
│   ├── checkout_contract.py
│   ├── circuit_breaker.py  ← pure domain rule
│   ├── ...
│   ├── email_provider.py   ← infrastructure
│   ├── gallery_public.py   ← selector
│   ├── gallery_storage.py  ← infrastructure
│   ├── public_lookup.py    ← selector
│   ├── receipt_pdf.py      ← infrastructure
│   └── state_machine.py
├── views.py            ← FAT: 7 domain functions + 1 HTTP view
└── ...
```

### After
```
bookings/
├── api/
│   ├── __init__.py
│   └── public_views.py
├── domain/             ← NEW: pure business rules
│   ├── __init__.py
│   ├── circuit_breaker.py
│   └── day_policy.py       ← pure weekday/window rules only
├── infrastructure/     ← NEW: external adapters
│   ├── __init__.py
│   ├── email_provider.py
│   ├── gallery_storage.py
│   └── receipt_pdf.py
├── selectors/          ← NEW: read-only queries + presentation
│   ├── __init__.py
│   ├── booking_status.py
│   ├── gallery_public.py
│   ├── public_catalog.py
│   └── public_lookup.py
├── services/           ← TRIMMED: mutation workflows only + compat wrappers
│   ├── availability.py
│   ├── bundles.py
│   ├── catalog.py          ← compat wrapper → selectors/
│   ├── checkout_contract.py
│   ├── circuit_breaker.py  ← compat wrapper → domain/
│   ├── ...
│   ├── email_provider.py   ← compat wrapper → infrastructure/
│   ├── gallery_public.py   ← compat wrapper → selectors/
│   ├── gallery_storage.py  ← compat wrapper → infrastructure/
│   ├── public_lookup.py    ← compat wrapper → selectors/
│   ├── receipt_pdf.py      ← compat wrapper → infrastructure/
│   └── state_machine.py
├── views.py            ← THIN: imports status_payload from selectors/
└── ...
```
