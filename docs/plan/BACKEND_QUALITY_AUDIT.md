# Backend quality audit (CodeRabbit-style)

**Branch:** `audit/backend-full-quality`
**Status:** Living audit — findings feed remediation PRs
**Scope:** `bookings/`, `checkout/`, `billing/`, `users/`, `core/`

## Diff log (GitHub)

| Range | Purpose |
|-------|---------|
| [cd068b6...3e8d00f](https://github.com/ALEX-MUTHOMI/aesthetic-os/compare/cd068b6...3e8d00f) | DSA harden commit (no PR review trail) |
| [00148b1...ce6c4bb](https://github.com/ALEX-MUTHOMI/aesthetic-os/compare/00148b1...ce6c4bb) | Availability engine → calendar service |
| [ce6c4bb...3e8d00f](https://github.com/ALEX-MUTHOMI/aesthetic-os/compare/ce6c4bb...3e8d00f) | Calendar lineage through DSA |
| [f629fe2...ab666da](https://github.com/ALEX-MUTHOMI/aesthetic-os/compare/f629fe2...ab666da) | Guest money path / Beat expiry |
| [ab666da](https://github.com/ALEX-MUTHOMI/aesthetic-os/commit/ab666da) | Beat expiry hardening |

Note: PR #19 (`development` → `staging`) predates `3e8d00f` and is **not** the DSA review trail.

**DSA history note:** Pre-`3e8d00f` calendar control flow was flatter; it also had per-day availability N+1. Remediation keeps batching and restores readability — it does not revert to N+1.

---

## Checklist (every ring)

Correctness · Readability · Structure · TDD · Lint/types · Diff history

---

## Ring A — DSA / calendar

| Severity | Finding | File | Evidence |
|----------|---------|------|----------|
| Major | Slot fetch swallows all exceptions as empty days | `bookings/services/booking_calendar.py` | `except Exception: return {}` |
| Major | Hold expiry capacity bumps not deduped by date | `bookings/services/hold_expiry.py` | one Redis incr per expired row |
| Major | Docs claim checkout Beat frees payment-pending capacity | `BACKEND_DSA_EFFICIENCY.md` | Beat table row vs code |
| Major | Curriculum “20 concepts” obscures ops truth | `BACKEND_DSA_EFFICIENCY.md` | SKIP linked lists / bits |
| Minor | Batching tests cover partition helpers only | `test_calendar_slot_batching.py` | no O(batches) assert on build |
| Minor | Tests co-shipped with `3e8d00f` (not red→green TDD) | same commit | — |

---

## Ring B — Checkout / M-Pesa

| Severity | Finding | File | Evidence |
|----------|---------|------|----------|
| Blocker | Checkout expiry does not free calendar capacity | `checkout/services.py` `expire_due_checkout_sessions` | session→EXPIRED only; booking stays `payment_pending` |
| Blocker | FAILED webhook replay treated as DUPLICATE (never reprocessed) | `record_mpesa_webhook_event` | non-created → in-memory DUPLICATE |
| Blocker | Success on EXPIRED/CANCELLED checkout rejects money with no ledger path | `_process_locked_callback` | `CheckoutStateError` before billing |
| Major | STK network I/O inside `select_for_update` | `initiate_mpesa_stk` | lock held across Daraja |
| Major | Owner STK view does not catch `CheckoutStateError` | `checkout/views.py` | can 500 |
| Major | Inbox DUPLICATE not persisted | `record_mpesa_webhook_event` | no `.save()` |
| Major | Expiry tests ignore booking/capacity side effects | `test_checkout_expiry.py` | session only |

Compare: [f629fe2...ab666da](https://github.com/ALEX-MUTHOMI/aesthetic-os/compare/f629fe2...ab666da)

---

## Ring C — Billing / ledger

| Severity | Finding | File | Evidence |
|----------|---------|------|----------|
| Major | `external_correlation_id` indexed not unique → concurrent double ledger risk | `billing/models.py` | race on empty `select_for_update` |
| Major | Pending ledger leaves `checkout_request_id` NULL (unique allows many NULLs) | `billing/services.py` | Postgres NULL unique |
| Major | Immutability is save-path only (`QuerySet.update` bypass) | `billing/models.py` | docstring overstates |
| Major | Disabled Celery `process_mpesa_webhook` silently DLQs | `billing/tasks.py` | footgun if enqueued |
| Minor | Sequential “pressure” tests, not concurrent same id | billing tests | — |
| Minor | Nested atomic in `mark_ledger_success` obscures locks | `billing/services.py` | — |

---

## Ring D — Bookings rest (API / staff / notifications)

| Severity | Finding | File | Evidence |
|----------|---------|------|----------|
| Blocker | Staff password-reset outbox keeps raw tokens in memory | `staff_auth.py` | `STAFF_PASSWORD_RESET_OUTBOX` |
| Blocker | Weekly overview ignores beautician booking scope | `staff_portal.get_weekly_overview` | no `staff_user` / scope |
| Major | Public API maps broad `Exception` → 400 with no log | `api/public_views.py` | catalog/calendar/resolve |
| Major | Login lockout record fails open on Redis errors | `staff_auth.py` | `record_login_failure` |
| Major | Remember-device HTTP unthrottled | `customer_views.py` | no `@route_throttle` |
| Minor | Apple OAuth `@csrf_exempt` without boundary comment | `staff_auth_views.py` | — |

---

## Ring E — Users + core

| Severity | Finding | File | Evidence |
|----------|---------|------|----------|
| Blocker | Unknown throttle scope admits all traffic | `core/throttling.py` | `if rate is None: return True` |
| Major | OTP throttle docs say 5/hour; settings are 5/min | `users/throttles.py` vs `settings.py` | docstring drift |
| Major | Email redaction: 1 vs 2 visible local chars | `users/redaction.py` vs `users/tasks.py` | inconsistency |
| Major | Abuse-signal Redis fails open | `core/abuse.py` | opposite of throttle |
| Minor | Empty `PII_*` defaults lack adjacent secret comments | `core/settings.py` | — |

---

## Remediation tracking

| ID | Finding | Status |
|----|---------|--------|
| A1 | Slot fetch silent empty | Fixed this PR |
| A2 | Hold expiry date dedupe | Fixed this PR |
| A3 | Human DSA + money-path docs | Fixed this PR |
| B1 | Checkout expiry → fail booking + free capacity | Fixed this PR |
| B2 | FAILED webhook allows retry | Fixed this PR |
| C1 | Unique `external_correlation_id` (migration) | Deferred — follow-up PR |
| D1 | Week overview RBAC scope | Fixed this PR |
| E1 | Missing throttle scope fail closed | Fixed this PR |
| E2 | Unify email redaction | Fixed this PR |

Deferred to follow-up PRs when scope is large or migration-sensitive: B3 late-success reconciliation ledger, C1 unique constraint migration, D1 staff reset outbox delivery redesign, STK lock refactor.
