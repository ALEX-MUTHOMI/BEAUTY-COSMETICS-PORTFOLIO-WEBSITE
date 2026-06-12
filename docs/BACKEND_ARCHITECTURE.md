# Backend Architecture And Refactor Map

This document records the Phase 2C-B8 backend modularization audit. It is a refactor guide, not permission to weaken security controls or change domain behavior.

## Bounded Contexts

- `bookings/` owns booking catalog exposure, availability, holds, booking lifecycle, receipt notifications, gallery media workflow, legal acceptance, staff portal workflows, and customer booking status.
- `checkout/` owns customer-facing payment orchestration, M-Pesa provider adapters, STK initiation, webhook inbox, provider callback normalization, idempotency, expiry/cancel handling, and the Checkout -> Billing contract.
- `billing/` owns immutable ledger truth, financial audit events, settlement records, provider/reference hashing, financial redaction, and audited correction paths.
- `core/` owns project settings, URL composition, correlation IDs, shared throttling, Celery, and deployment security flags.

Bookings may reference Checkout and Billing only through explicit service contracts. Booking must not process M-Pesa callbacks or write ledger truth directly.

## Audit Table

| Path | Current responsibility | Problem | Suggested target | Risk | Tests protecting it | Safe now |
| --- | --- | --- | --- | --- | --- | --- |
| `bookings/models.py` | Booking, receipt, notification, gallery, staff data models | Very large model file with many subdomains | Keep stable until model extraction can be done without migration churn | High | `bookings/tests`, integration, security | No |
| `bookings/api_views.py` | Public API adapters for catalog, availability, holds, checkout bridge | Public API concerns were flat at app root | `bookings/api/public_views.py` with compatibility shim | Low | `tests/api`, Newman, `bookings/tests` | Yes |
| `bookings/views.py` | Public booking status HTTP adapter | **B8A DONE**: 7 status functions extracted to `bookings/selectors/booking_status.py`; view is now thin | — | Low | `tests/api`, `bookings/tests`, security | Yes |
| `bookings/services/availability.py` | Slot search and capacity rules | Performance/security sensitive scheduling algorithm | `bookings/services/availability/engine.py` later | High | availability/load/security tests | No |
| `bookings/services/holds.py` | Hold creation, abuse controls, idempotency | Concurrency and anti-bot sensitive | Split only with dedicated hold regression suite | High | hold, load, API, security tests | No |
| `bookings/services/day_policy.py` | ORM-backed day-policy lookup and row-locked capacity snapshots | Database lock boundary; must not move wholesale into domain | Keep service canonical; pure helpers only in `bookings/domain/day_policy.py` | High | day-policy, hold, full-package, load tests | No |
| `bookings/services/checkout_contract.py` | Booking to Checkout/Billing coordination | Cross-context state consistency | Keep as explicit anti-corruption layer | High | booking checkout contract, integration, security | No |
| `bookings/services/receipt_pdf.py` | Compatibility wrapper | **B8A DONE**: Canonical at `bookings/infrastructure/receipt_pdf.py` | — | Low | receipt PDF/security tests | Yes |
| `checkout/views.py` | DRF perimeter for checkout/session/STK/webhook | Thin and correctly catches provider/state errors | Keep API layer | Medium | checkout/security/integration tests | No |
| `checkout/services.py` | Checkout orchestration, locking, webhook processing | Financial attack surface | Keep stable; split only with callback storm tests running | High | checkout/load/security/integration tests | No |
| `checkout/providers/mpesa.py` | Real Daraja adapter | External payment boundary | Keep isolated under providers | High | Daraja adapter/external contract tests | No |
| `billing/services.py` | Ledger/audit/settlement state changes | Immutable financial truth | Keep service-only writes | High | billing tests and integration | No |
| `core/settings.py` | Security/env configuration | Broad blast radius | Keep centralized; change only via tests | Medium | manage.py check, security tests | No |
| `core/urls.py` | URL composition and admin gating | Public route exposure risk | Keep explicit, test route exposure | Medium | API/Newman/security tests | No |

## Target Module Map

The safe long-term shape is:

- `bookings/api/`: public booking API adapters and response contracts.
- `bookings/domain/`: pure business rules — no ORM, no side effects. (**B8A: created**, contains `circuit_breaker.py`; day-policy pure helpers live in `day_policy.py`)
- `bookings/selectors/`: read-model queries and status payload assembly. (**B8A: created**, contains `booking_status.py`, `public_catalog.py`, `public_lookup.py`, and a `gallery_public.py` compatibility wrapper)
- `bookings/infrastructure/`: external provider/storage adapters. (**B8A: created**, contains `email_provider.py`, `gallery_storage.py`, `receipt_pdf.py`)
- `bookings/services/`: booking business services and state transitions. (Trimmed: moved 7 modules to domain/selectors/infrastructure, wrappers remain)
- `bookings/receipts/`: receipt PDF, artifact reuse, notification outbox, and delivery retry policy. (Future)
- `bookings/gallery/`: secure media bounded context. (**B8E: created**, contains `selectors/public_gallery.py`; quarantine, validation, publishing, and cleanup service splits remain future work)
- `bookings/staff/`: staff authentication, portal selectors, and staff security policy. (Future)
- `checkout/providers/`: fake and real provider adapters only.
- `checkout/services/`: checkout orchestration and webhook transaction boundary.
- `billing/services/`: ledger/audit/settlement transitions only.

## Refactor Rules

- Keep views thin and service-backed.
- Keep serializers as validation-only.
- Keep financial mutation in Billing services.
- Keep provider orchestration in Checkout services/adapters.
- Preserve existing import compatibility during moves.
- Run Docker checks before and after each bounded move.
- Do not move high-risk service code without first running its targeted concurrency/security suite.

## B8E Incremental Refactor Note

B8E moved only low-risk read-only/test-support code:

- `tests/factories/booking_factories.py` is the canonical shared booking factory module.
- `bookings/tests/factories.py` remains a wrapper for old test imports.
- `bookings/gallery/selectors/public_gallery.py` is the canonical public gallery read model.
- `bookings/selectors/gallery_public.py` and `bookings/services/gallery_public.py` remain compatibility wrappers.

The high-risk gallery processing/upload service, staff auth/session workflows,
booking state machine, and checkout/billing payment contracts remain in their
existing service modules until each can be split with a dedicated security and
concurrency test slice.
