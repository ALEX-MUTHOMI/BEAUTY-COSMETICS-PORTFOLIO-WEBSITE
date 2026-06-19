# Phase 3B BOLA / IDOR Object Access Matrix

Production readiness: **rejected / not claimed**.

This matrix inventories object-bearing API surfaces for Phase 3B discovery. It
distinguishes public-by-design routes from protected object routes and records
the expected denial/privacy policy for hostile actors.

## Actor Model

| Actor | Meaning |
| --- | --- |
| Anonymous | No authenticated Django/DRF user. |
| Customer owner | Authenticated customer that owns the object. |
| Other customer | Authenticated customer attempting cross-user access. |
| Staff authorized | Active staff with required `bookings.*` permission and valid staff session. |
| Staff unauthorized | Active staff without the route permission or recent reauth where required. |
| Inactive staff | Staff account with `is_active=False`. |
| Provider webhook | External M-Pesa/Daraja callback perimeter. |
| System task | Celery/management command/service code, not public API. |

## Object Routes

| Route | Method | Object identifier | Identifier source | Allowed actor | Expected rule | Denial mode | Sensitive fields forbidden on denial | Existing tests | 3B tests | Risk | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/health/` | GET | none | none | Anonymous | Public liveness only | n/a | secrets, debug data | security headers, Newman | anonymous public route check | Low | covered |
| `/api/health-check/` | GET | none | none | Anonymous | Public liveness only | n/a | secrets, debug data | security headers, Newman | anonymous public route check | Low | covered |
| `/api/csrf/` | GET | CSRF cookie | cookie | Anonymous | Public CSRF bootstrap | n/a | session IDs, secrets | security headers, Newman | documented existing | Medium | covered |
| `/api/auth/request-otp/` | POST | email | body | Anonymous | Bot/OTP throttle controlled | 400/429 generic | OTP, account existence | OTP/security tests | documented existing | High | covered existing |
| `/api/auth/verify-otp/` | POST | email + OTP | body | Anonymous | OTP proves identity | 400 generic | OTP/account enumeration | OTP/security tests | documented existing | High | covered existing |
| `/api/bookings/catalog/services/` | GET | service catalog | server-side public set | Anonymous | Public active services only | n/a | internal IDs, inactive services | Newman, catalog tests | public route check | Low | covered |
| `/api/bookings/catalog/packages/` | GET | package catalog | server-side public set | Anonymous | Public active packages only | n/a | internal IDs, inactive packages | Newman, package tests | public route check | Low | covered |
| `/api/bookings/availability/` | GET | service/resource IDs | query | Anonymous | Public availability, generic errors | 400 generic | customer PII, booking IDs | availability security tests | matrix only | Medium | covered existing |
| `/api/bookings/holds/` | POST | service/resource IDs, idempotency key | body | Anonymous | Creates held booking with server pricing only | 400 generic | PII on denial, server amount truth | hold security/idempotency tests | `test_mass_assignment.py` | High | covered |
| `/api/bookings/checkout/` | POST | booking public ID, idempotency key | body | Anonymous with non-enumerable booking token | Checkout allowed only for valid held booking and accepted policy | 400 generic | PII, provider refs, ledger IDs | checkout contract tests | `test_mass_assignment.py` | High | covered |
| `/api/bookings/status/<public_booking_id>/` | GET | booking public UUID | path token | Anonymous/customer with token | Public status is token-based and zero-PII | 404 generic for invalid/missing | phone, email, internal booking ID, checkout ID, ledger ID, provider refs | status endpoint tests | `test_bola_idor_customer_objects.py` | High | covered |
| `/api/checkout/sessions/` | POST | idempotency key | body | Authenticated customer | Creates checkout owned by authenticated user only | 401/403 unauth, validation error | server-owned customer/role/status fields | checkout API tests | `test_mass_assignment.py`, `test_status_payment_tampering.py` | Critical | covered |
| `/api/checkout/sessions/<checkout_id>/` | GET | checkout UUID | path | Customer owner | Customer-scoped selector only | 404 for other customer | amount/provider data/IDs | checkout auth tests | `test_bola_idor_customer_objects.py`, `test_role_tampering.py` | Critical | covered |
| `/api/checkout/sessions/<checkout_id>/mpesa/stk/` | POST | checkout UUID | path | Customer owner | Customer-scoped selector plus STK throttle | 404 for other customer | amount/provider data/IDs | checkout auth/throttle tests | `test_bola_idor_customer_objects.py` | Critical | covered |
| `/api/checkout/mpesa/webhook/` | POST | checkout request ID | provider payload | Provider webhook | IP/sandbox callback perimeter, inbox, idempotency, amount/state validation | 202/400/403 safe | raw callback, receipt, provider IDs | webhook tests/security/load | documented existing | Critical | covered existing |
| `/api/billing/stk-push/` | POST | legacy payment fields | body | none | Disabled legacy route | 410 | submitted provider IDs/ledger IDs | billing tests/Newman | `test_bola_idor_customer_objects.py`, `test_status_payment_tampering.py` | High | covered |
| `/api/billing/mpesa-webhook/` | POST | legacy provider payload | body | none | Disabled legacy route behind IP permission | 403/410 | provider payload | billing tests | `test_authorization_control_closeout.py` | Medium | covered |
| `/api/staff/auth/login/` | POST | staff email/password | body | Staff account only | Generic login, no customer escalation | 400/429 generic | account existence, password | staff auth tests | matrix only | High | covered existing |
| `/api/staff/auth/logout/` | POST | session | cookie | Staff session | Logout current session only | generic | session IDs | staff auth tests | matrix only | Medium | covered existing |
| `/api/staff/auth/me/` | GET | session | cookie | Active staff session | Staff profile only | 403 | staff/customer PII | staff auth tests | anonymous access test | High | covered |
| `/api/staff/auth/reauth/` | POST | session/password | cookie/body | Active staff session | Recent auth only | 400/403 generic | password | staff tests | matrix only | High | covered existing |
| `/api/staff/bookings/schedule/` | GET | date/filter | query | Authorized active staff | Staff-global schedule by current design | 403 for non-staff/unauthorized | customer contact details | staff tests | `test_role_tampering.py`, `test_query_scope_tampering.py` | High | covered |
| `/api/staff/bookings/week/` | GET | date/filter | query | Authorized active staff | Staff-global week view by current design | 403 | customer contact details | staff tests | matrix only | High | covered existing |
| `/api/staff/bookings/<public_booking_id>/` | GET | booking public UUID | path | Authorized active staff | Staff-global booking detail by current design | 403/404 | phone/email unless contact reveal route | staff tests | `test_bola_idor_staff_objects.py` | High | covered |
| `/api/staff/bookings/<public_booking_id>/payment/` | GET | booking public UUID | path | Authorized active staff | Redacted payment summary only | 403/404 | ledger ID, checkout ID, provider refs | staff payment tests | matrix only | High | covered existing |
| `/api/staff/bookings/<public_booking_id>/contact-access/` | POST | booking public UUID | path | Authorized active staff with recent reauth and permission | Contact reveal only when permission and reason present | 403/404/400 generic | phone/email on denial | contact audit tests | `test_bola_idor_staff_objects.py` | Critical | covered |
| `/api/staff/gallery/categories/` | GET | gallery categories | server-side | Active staff | Staff-only upload navigation | 403 | storage keys | gallery tests | anonymous access test | Medium | covered |
| `/api/staff/gallery/images/` | POST | category/subcategory IDs, upload | body/file | Active staff | Quarantine/validate/upload only | 400/403/409/429 safe | storage keys, original filename/path | gallery upload tests | matrix only | High | covered existing |
| `/api/gallery/public/homepage/` | GET | public gallery | server-side | Anonymous | Published public optimized variants only | n/a | private storage keys, staff IDs | gallery tests | anonymous/query tests | Medium | covered |
| `/api/gallery/public/categories/<slug>/` | GET | category slug | path | Anonymous | Published public optimized variants only | 404 generic | private storage keys, unpublished titles | gallery tests | `test_query_scope_tampering.py` | Medium | covered |
| `/api/gallery/public/services/<slug>/` | GET | service/category slug | path | Anonymous | Published public optimized variants only | 404 generic | private storage keys | gallery tests | matrix only | Medium | covered existing |
| `/api/customers/remembered-device/*` | GET/POST | device cookie token | cookie/body | Anonymous with opaque remembered-device cookie | Redacted repeat-booking convenience only | generic | raw token, full PII | remembered-device tests | matrix only | High | covered existing |
| `/api/legal/documents/*` | GET | document type/version | path | Anonymous | Active legal docs only | 404 generic | draft/private docs | legal tests/Newman | matrix only | Low | covered existing |
| `/admin/` | any | admin session | cookie | Admin only when enabled locally | Disabled/blockable in staging | login/404/blocked | debug/secrets | staging audit docs | matrix only | High | deferred staging |

## Summary

- Total inventoried route groups: **34**.
- Critical object categories: checkout session ownership, webhook payment truth,
  staff contact reveal, booking checkout bridge.
- High-risk object categories: booking public status token, booking hold,
  staff booking/payment views, staff gallery upload, customer remembered-device
  token, disabled billing routes.
- Public-by-design routes were explicitly separated from protected routes.
- Phase 3B-C closes the legacy billing webhook follow-up with an explicit
  allowed-IP test proving the route still returns `410` after permission
  preconditions pass.
