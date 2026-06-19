# ABAC Policy Matrix

Production readiness: **rejected / not claimed**.

The app does not need a new generic ABAC engine at this stage. Its access model
already uses attribute-based decisions in services, selectors, permission
classes, and state machines. This matrix documents those attributes and makes
the staff scoping decision explicit.

## Actor Attributes

| Attribute | Meaning |
| --- | --- |
| anonymous | No authenticated user/session. |
| authenticated_customer | Authenticated customer user. |
| booking_token_holder | Caller has a valid booking public status/checkout token. |
| checkout_owner | Authenticated user equals `CheckoutSession.customer`. |
| non_owner_customer | Authenticated user does not own the requested object. |
| staff_active | Staff account is active and staff session is valid. |
| staff_permission | Staff user has required `bookings.*` permission. |
| staff_recent_reauth | Staff user recently reauthenticated for sensitive action. |
| inactive_staff | Staff account exists but is inactive. |
| provider_source | Request passes configured provider IP/tunnel policy. |
| system_task | Internal task/service execution path. |

## Resource Attributes

| Attribute | Meaning |
| --- | --- |
| booking_public_id | Random public booking identifier. |
| booking_state | HELD, PAYMENT_PENDING, CONFIRMED, EXPIRED, etc. |
| hold_valid | Hold exists, is not expired, and is eligible for checkout. |
| checkout_customer | User owning checkout session. |
| checkout_state | CREATED, PAYMENT_PENDING, STK_SENT, PAID, FAILED, EXPIRED, CANCELLED. |
| payment_amount_snapshot | Server-derived immutable amount/currency snapshot. |
| provider_event_hash | Deduplication key for webhook inbox. |
| gallery_visibility | Published/public vs private/quarantine/archived. |
| contact_reveal_eligible | Staff has permission, recent reauth, reason, and auditable request. |
| route_disabled | Legacy route retained only for safe 410 response. |

## Context Attributes

| Attribute | Meaning |
| --- | --- |
| http_method | GET/POST route behavior. |
| csrf_session | CSRF/session context for browser state-changing routes. |
| source_ip_policy | Safaricom/trusted-proxy/sandbox callback source validation. |
| provider_mode | Fake provider for default tests; real providers opt-in only. |
| security_scan_mode | OpenAPI is gated and disabled by default. |
| idempotency_key | Repeated customer/provider actions must be idempotent. |
| request_headers | Untrusted for app authorization except controlled proxy security context. |
| query_scope | Untrusted; cannot widen object access. |

## High-Risk ABAC Rules

| Action | ABAC rule | Evidence |
| --- | --- | --- |
| View checkout session | `authenticated_customer` and `checkout_owner`; ignore identity headers/query params. | BOLA customer tests, role tampering tests. |
| Initiate STK | `authenticated_customer`, `checkout_owner`, non-terminal checkout state, idempotency and throttle pass. | checkout API/throttle tests, BOLA customer tests. |
| Process M-Pesa callback | `provider_source`, valid callback shape, matching provider attempt, matching amount, acceptable checkout state, idempotent event hash. | checkout webhook/security/load tests. |
| Create booking hold | public route, valid active service/resource, server-side price/duration, capacity policy, idempotency. | hold and mass-assignment tests. |
| Create booking checkout | valid held booking token, policy accepted, hold not expired, server amount snapshot. | checkout contract and mass-assignment tests. |
| View booking status | valid public booking token; response is zero-PII and generic on invalid token. | booking status and BOLA tests. |
| View staff booking detail | `staff_active`, valid staff session, `view_staff_booking` permission. Global staff access is current product policy. | staff portal tests, 3B-C staff policy test. |
| Reveal customer contact | `staff_active`, valid session, `view_staff_contact_details`, `staff_recent_reauth`, non-empty reason, audit event. | staff contact audit/red-team tests. |
| View public gallery | public route, `gallery_visibility=published`, optimized public variants only. Query scope cannot include private content. | gallery public and query tampering tests. |
| Use disabled legacy billing routes | route is disabled; payload and provider fields are not processed. | disabled route tests. |

## Staff Scoping Decision

Current product policy: **Option A - Global Staff Access Is Current Product Policy**.

Meaning:

- Active staff with the required permission can access staff portal booking
  read models globally.
- Staff A / Staff B row ownership is not a current requirement because no
  assignment/branch/resource ownership policy is present.
- Non-staff, inactive staff, expired staff sessions, and staff without required
  permissions remain denied.
- If per-beautician/per-resource scoping becomes a product requirement, it must
  be implemented in a patch phase with Staff A / Staff B cross-object tests
  before release.

## Status

ABAC policy is documented and test-backed without adding a speculative generic
authorization framework.
