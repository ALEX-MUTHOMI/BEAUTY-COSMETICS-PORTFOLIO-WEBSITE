# AestheticOS

**The booking operating system for spa & aesthetics businesses.**

AestheticOS is a production-grade monorepo for portfolio galleries, appointment booking, M-Pesa checkout, staff operations, and immutable billing — built with Django 6, Nuxt 3 SSR, PostgreSQL, Redis, and Celery.

## Highlights

- Public portfolio gallery with secure image pipeline
- Appointment booking with atomic holds and PostgreSQL overlap protection
- Safaricom M-Pesa (Daraja) checkout with webhook idempotency
- Immutable billing ledger separate from booking state
- Staff portal for schedule, bookings, gallery, and payments
- Customer guest booking, OTP flows, and public status polling
- Enterprise-style CI: security scans, load tests, chaos testing, Newman acceptance

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.13, Django 6, DRF, Poetry |
| Frontend | Nuxt 3, Vue 3, Pinia, TypeScript |
| Data | PostgreSQL 16, Redis 7, Celery |
| Payments | M-Pesa Daraja STK + webhooks |
| Security | Turnstile, CSRF, rate limits, red-team test suite |

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

- API: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## Documentation

- [Backend architecture](docs/BACKEND_ARCHITECTURE.md)
- [Booking production blueprint](docs/BOOKING_APP_PRODUCTION_BLUEPRINT.md)
- [CI test matrix](docs/testing/CI_TEST_MATRIX.md)
- [Portfolio showcase (recruiter-safe)](showcase/README.md)

## Repository visibility

This codebase is intended to stay **private** for production security. Recruiter-facing materials live in [`showcase/`](showcase/) and can be published separately without exposing implementation details.

## Author

**Alex Muthomi** — [ALEX-MUTHOMI](https://github.com/ALEX-MUTHOMI)
