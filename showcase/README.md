# AestheticOS — Portfolio Overview

Recruiter-facing summary of **[aesthetic-os](https://github.com/ALEX-MUTHOMI/aesthetic-os)** — the public source for Shee Aesthetics’ booking operating system.

**Tagline:** *The booking operating system for aesthetics businesses.*

## Elevator pitch

**AestheticOS** is a full-stack spa & aesthetics booking platform: public portfolio, appointment scheduling, M-Pesa payments, staff portal, and an immutable billing ledger — with security testing treated as a first-class concern.

## Problem

Aesthetics and spa businesses need more than a brochure site:

- Showcase work without leaking raw uploads
- Take bookings with real capacity rules (no double-booking)
- Accept mobile money (M-Pesa) reliably under webhook retries and duplicates
- Give staff a secure operations portal without exposing customer PII casually
- Keep financial records auditable and separate from booking UI state

## Solution

| Module | Responsibility |
|--------|----------------|
| **Bookings** | Catalog, availability, holds, lifecycle, gallery, staff workflows |
| **Checkout** | Payment orchestration, M-Pesa STK, webhooks, idempotency |
| **Billing** | Immutable ledger, settlements, financial audit events |
| **Core** | Auth, throttling, Celery, security headers, OpenAPI |

## Design choices that matter

1. **PostgreSQL exclusion constraints** — overlap protection at the database layer, not only in Python
2. **Checkout ↔ Billing contract** — booking state never directly mutates ledger truth
3. **Webhook inbox + idempotency** — duplicate M-Pesa callbacks cannot double-credit
4. **Response privacy** — staff/customer APIs redact fields by role and context
5. **Defense in depth** — Turnstile, CSRF, rate limits, abuse circuit breaker, large automated security suite

## Tech stack

| Area | Choices |
|------|---------|
| Backend | Python 3.13, Django 6, DRF |
| Frontend | Nuxt 3 (SSR), Vue 3, Pinia, TypeScript |
| Database | PostgreSQL 16 |
| Queue / cache | Redis 7, Celery |
| Payments | Safaricom M-Pesa via Daraja API |
| Bot protection | Cloudflare Turnstile |
| Testing | pytest, Playwright, Newman/Postman, OWASP ZAP (CI), load & chaos suites |
| Deploy | Docker multi-stage builds, GitHub Actions |

## Features

- [x] Public portfolio gallery with optimized variants
- [x] Service catalog, bundles, and day-capacity policies
- [x] Atomic booking holds with expiry
- [x] M-Pesa STK push + callback normalization
- [x] Immutable billing ledger and settlement records
- [x] PDF receipts and email outbox with retry/DLQ
- [x] Staff portal (dashboard, bookings, gallery upload, payments)
- [x] Customer OTP for sensitive actions
- [x] Legal/policy acceptance flows
- [x] CI: lint, security scan, integration, Docker build gates

## Code patterns (sanitized)

See [SNIPPETS.md](./SNIPPETS.md) for short, secret-free excerpts (bounded contexts, overlap constraints, SSR security perimeter).

Full implementation: **[github.com/ALEX-MUTHOMI/aesthetic-os](https://github.com/ALEX-MUTHOMI/aesthetic-os)**

## Contact

**Alex Muthomi** · GitHub: [@ALEX-MUTHOMI](https://github.com/ALEX-MUTHOMI)
