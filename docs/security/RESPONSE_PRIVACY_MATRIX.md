# Response Privacy Matrix

Production readiness: **rejected / not claimed**.

Phase 3C moves from object authorization to response minimization. The
question for every row is: once the actor is allowed to reach the route, does
the response contain only intended fields?

| Route group | Method | Actor | Response class | Intended fields | Forbidden fields | Existing/new evidence | Risk | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/health/`, `/api/health-check/` | GET | anonymous | public | `status` | debug, env, secrets | Newman, security headers tests | Low | Covered |
| `/api/csrf/` | GET | anonymous browser | public bootstrap | CSRF bootstrap JSON/cookie | session IDs, app secrets, debug | Newman, security headers tests | Medium | Covered |
| `/api/bookings/catalog/*` | GET | anonymous | public catalog | public services/packages | customer PII, internal staff/payment/storage data | Newman, catalog tests | Medium | Covered |
| `/api/bookings/availability/` | GET | anonymous | public availability | slots and public selection data | customer PII, booking internals, staff fields | availability security tests, Newman | Medium | Covered |
| `/api/bookings/holds/` | POST | anonymous intent holder | public booking intent | hold token, status, schedule, selection, next action | phone/email, ledger, provider, debug, staff fields | `test_response_privacy_booking.py` | High | Covered |
| `/api/bookings/checkout/` | POST | held booking token holder | token checkout bridge | booking token, checkout public handle, amount, currency, next action | provider IDs, ledger IDs, raw customer PII, raw payloads | `test_response_privacy_booking.py` | High | Covered |
| `/api/bookings/status/<public_id>/` | GET | token holder | public/token status | status, schedule, receipt/email/reminder status, next action | phone/email, checkout provider IDs, ledger IDs, token echo beyond booking reference | `test_response_privacy_booking.py` | High | Covered |
| `/api/checkout/sessions/` | POST | authenticated customer | owner-only checkout | owner checkout ID, status | ledger/provider IDs, raw phone, payload echo | `test_response_privacy_checkout_billing.py` | High | Covered |
| `/api/checkout/sessions/<id>/` | GET | authenticated owner | owner-only checkout | owner checkout ID, status, amount | provider payload, private booking ID, owner PII | `test_response_privacy_checkout_billing.py` | High | Covered |
| `/api/checkout/sessions/<id>/mpesa/stk/` | POST | authenticated owner | owner-only payment action | attempt ID/status only | Daraja IDs, receipt, raw phone, token, provider body | checkout tests, denylist policy | High | Covered by existing route tests; direct 3C STK response test deferred to avoid provider side effects |
| `/api/checkout/mpesa/webhook/` | POST | provider/system | provider callback | generic accepted/malformed status | raw callback, Daraja IDs, receipt, ledger, phone | `test_response_privacy_checkout_billing.py`, `test_response_privacy_errors.py` | Critical | Covered |
| `/api/billing/stk-push/` | POST | any | disabled | generic 410 detail | payload echo, ledger/provider/payment data | `test_response_privacy_checkout_billing.py` | High | Covered |
| `/api/billing/mpesa-webhook/` | POST | provider/system | disabled | generic 410 detail | payload echo, provider IDs, phone | `test_response_privacy_checkout_billing.py` | High | Covered |
| `/api/staff/bookings/schedule/`, `/week/` | GET | active staff | staff-only | operational schedule rows | raw contact, provider payload, storage/auth internals | staff tests, Newman | High | Covered |
| `/api/staff/bookings/<id>/` | GET | active staff | staff-only detail | operational booking detail | provider payload, ledger IDs, storage/auth internals | `test_response_privacy_staff.py` | High | Covered |
| `/api/staff/bookings/<id>/payment/` | GET | permitted staff | staff-only payment summary | redacted payment status/amount/provider availability | ledger IDs, raw provider refs, receipt IDs | `test_response_privacy_staff.py` | High | Covered |
| `/api/staff/bookings/<id>/contact-access/` | POST | permitted/recently reauth staff | staff-with-context | audited phone/email reveal only | provider/storage/auth/audit internals | `test_response_privacy_staff.py` | Critical | Covered |
| `/api/gallery/public/*` | GET | anonymous | public gallery | published display fields and opaque public variant URLs | storage keys, private buckets, drafts, EXIF, owner internals | `test_response_privacy_gallery.py` | High | Covered; 3C-HIGH-001 patched |
| `/api/staff/gallery/categories/` | GET | active staff | staff navigation | category/subcategory navigation fields | upload storage internals, hashes, owner internals | `test_response_privacy_gallery.py` | Medium | Covered |
| Error/denial routes | mixed | anonymous/customer/staff/provider | error/denial | generic `detail`/status | stack traces, object existence leaks, PII, provider/storage internals | `test_response_privacy_errors.py` | High | Covered |

## Gaps And Deferred Items

- STK initiation response privacy is covered by existing checkout permission and
  throttle tests, but Phase 3C did not add a direct STK response test because
  this discovery phase must not call a real provider. Future fake-provider STK
  response inspection can be added in Phase 3D without changing provider truth.
- If product policy changes from global staff booking visibility to
  per-beautician or branch scoping, the response matrix and ABAC tests must be
  reopened.
