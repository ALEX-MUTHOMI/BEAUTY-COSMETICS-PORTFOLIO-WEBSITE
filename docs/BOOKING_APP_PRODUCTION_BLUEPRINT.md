# Booking App Production Blueprint

## Purpose

The `bookings/` app owns appointment scheduling foundations for services, resources, holds, operational booking state, reminders, rescheduling policy, urgent handling, and staff workflow. It does not own payment orchestration or financial truth.

## Domain Boundaries

- `bookings/` owns scheduling, capacity protection, booking lifecycle, reminders, reschedule requests, urgent policy flags, and staff workflow audit.
- `checkout/` owns customer-facing payment orchestration, M-Pesa provider interaction, callbacks, idempotency, and payment outcome events.
- `billing/` owns immutable financial truth, ledger transactions, audit events, settlement records, reconciliation, and financial corrections.
- Booking may store `checkout_session_id`, `billing_ledger_id`, or provider reference hashes for operational visibility only.

## Core Product Rules

- A booking must not become confirmed without a valid payment success signal from Checkout in a later integration phase.
- Two active bookings must not overlap for the same resource.
- Customers do not get a self-service refund portal in this phase; the operational remedy is policy-controlled rescheduling.
- Sunday is closed by default. Urgent Sunday handling requires surcharge and manual review in later phases.
- Urgent booking means paid priority handling, not guaranteed automatic confirmation.

## Booking State Machine

The lifecycle is service-controlled. Direct state mutation is not a sanctioned path.

Allowed foundation transitions include:

- `requested -> held`
- `held -> payment_pending`
- `held -> expired`
- `payment_pending -> confirmed`
- `payment_pending -> payment_failed`
- `confirmed -> reschedule_requested`
- `confirmed -> checked_in`
- `confirmed -> late`
- `confirmed -> no_show`
- `confirmed -> cancelled_by_client`
- `confirmed -> cancelled_by_business`
- `late -> checked_in`
- `late -> no_show`
- `checked_in -> in_progress`
- `in_progress -> completed`

Terminal and failed payment states require future audited correction flows before any promotion.

## PostgreSQL Overlap Protection

Booking capacity is protected with PostgreSQL, not only application checks. `btree_gist` enables an exclusion constraint combining `resource` equality with timestamp range overlap. The range is `[starts_at, ends_at)`, so a booking ending at 10:00 and another starting at 10:00 are adjacent and allowed.

Only blocking statuses reserve capacity:

- `held`
- `payment_pending`
- `confirmed`
- `reschedule_held`
- `checked_in`
- `late`
- `in_progress`

## Timezone Policy

The database stores timezone-aware UTC datetimes. Africa/Nairobi is used for business-hour boundaries, customer-facing interpretation, and presentation. Naive datetimes are rejected. Frontend ISO input with `+03:00` must be converted before persistence.

## PII, HMAC, And Redaction

Booking customer contact data is split by purpose:

- Encrypted fields support operational reminders and staff workflows.
- HMAC lookup hashes support deterministic search without exposing low-entropy phone or email values.
- Redacted display fields support logs and dashboards.

Plain SHA256 is forbidden for phone and email lookup because those inputs are enumerable. Raw phone numbers, email addresses, names, OTPs, payment references, and encryption material must not appear in logs or docs.

## Reminder Outbox

`BookingReminder` is a durable outbox. Creating the row is the source of truth for reminder intent. Celery or another worker may later dispatch reminders, but worker failure must not erase the reminder. Send-time checks must revalidate booking status, consent, and erasure.

## Redis Circuit Breaker

Redis counters provide cheap rolling-window abuse signals for hold exhaustion. Every `INCR` must set or refresh `EXPIRE` to avoid permanent lockout. Modes are `NORMAL`, `ELEVATED`, `ABUSE`, and `LOCKDOWN`. PostgreSQL aggregate scans are avoided during attack traffic.

## Reschedule And No-Refund Policy

The customer remedy is rescheduling, not self-service refunds. The old slot must not be released until a new slot is safely held. Free reschedules link to the original billing ledger for traceability. Additional-fee reschedules must create a new Checkout session in a later phase, not mutate Billing ledger truth.

## Staff And Beautician Security

Staff views must default to redacted customer contact data. Any reveal of operational contact fields must be permission checked and written to `StaffActionAuditEvent`. Bulk export and dashboard filtering need explicit authorization and redaction in later phases.

## Enumeration Protection

Public lookup uses `public_id` plus customer proof such as phone HMAC. Internal primary keys must not be exposed. Unknown records should return generic responses.

## Observability Requirements

Booking state transitions, contact reveals, reminder outcomes, reschedule decisions, and circuit-breaker mode changes need correlation IDs and redacted structured logs. Observability must not include raw PII.

## B5 Customer Status, OTP, Reminder, And Reschedule Policy

B5 preserves guest booking. Customers are not forced into accounts, usernames, or passwords. The booking form remains the transactional source of customer truth for a single booking: full name, email, phone, selected service, and selected slot are stored through encrypted values, HMAC lookup hashes, and redacted display fields. Raw email and phone are not primary keys.

The minimal status API at `/api/bookings/status/<public_booking_id>/` does not require OTP. It is designed for post-payment polling and only returns bounded, customer-safe state: booking/payment/receipt/email/reminder/reschedule status, schedule presentation in Africa/Nairobi, service name, and next action. It must not expose raw PII, encrypted fields, internal UUIDs, checkout IDs, ledger IDs, provider references, receipt tokens, exact provider quota details, or stack traces. Malformed and unknown public IDs return the same generic 404 schema.

OTP is required only for sensitive follow-up actions such as rescheduling, later receipt access, contact update, or future private booking access. OTP is not required to create a booking, pay, or view the minimal status page. OTP challenges store only HMAC/hash values, expire quickly, are single-use, enforce max attempts, and are rate-limited by recipient hash, booking public ID, IP hash, and user-agent hash. Responses are anti-enumeration by design.

Rescheduling requires a short-lived, server-side, scoped customer action session produced by OTP verification. The session is scoped to booking and purpose, expires quickly, and is consumed after use. Free rescheduling does not create fake Billing ledger rows. Booking remains the scheduling owner; Checkout remains payment orchestration; Billing remains immutable financial truth.

Reschedule policy is no-refund by design. The allowed customer remedy is policy-controlled rescheduling. Cutoff hours, max reschedule count, Monday-Saturday 07:00-19:00 Africa/Nairobi business hours, Sunday rejection, and PostgreSQL overlap constraints are enforced. Failed reschedules keep the original confirmed booking intact. Successful reschedules cancel old pending reminders and create new reminder rows for the new appointment time.

Reminder delivery uses `BookingReminder` as a durable outbox and `BookingReminderDeliveryService.send_due(now=None, limit=100)` as the bounded worker service. Reminder rows are created only for confirmed, non-erased bookings with consent. Delivery uses the fake provider in default tests, rechecks booking/customer state before send, retries provider failures with backoff, caps attempts, and moves exhausted failures to admin review. Reminder failures must not corrupt Booking, Checkout, Billing, receipts, or payment state.

## B1 Implementation Status

Implemented in B1:

- Booking foundation models.
- PostgreSQL `btree_gist` and overlap exclusion constraint.
- UTC-aware datetime enforcement.
- PII encryption, HMAC lookup, and redacted display utilities.
- State-machine service.
- Reminder outbox skeleton.
- Reschedule request foundation.
- No-refund financial history policy foundation.
- Staff action audit foundation.
- Redis circuit-breaker skeleton.
- Booking unit/security tests.

Implemented in B2:

- Service-layer availability engine.
- Africa/Nairobi business-day slot generation.
- 07:00-19:00 default Monday-Saturday windows.
- Sunday closed for normal availability.
- Service duration and buffer-aware candidate windows.
- Interval merging and free-window subtraction.
- Blocking booking, active hold, and blackout exclusion.
- Expired/cancelled/payment-failed booking non-blocking behavior.
- Per-resource daily capacity foundation.
- Bounded date range validation.
- Redis availability request counter with TTL.
- PII-safe, public-ID-only response shape.

Implemented in B3:

- Atomic hold creation service with server-side service duration and UTC persistence.
- PostgreSQL exclusion-constraint enforcement for overlapping active holds under concurrency.
- Idempotency-key retry handling for slow mobile networks and repeated Pay/hold attempts.
- HMAC-backed idempotency request fingerprints stored only in redacted audit metadata.
- Redis rolling hold-attempt and hold-created counters with TTL.
- Abuse-mode hold TTL shortening through the booking circuit-breaker signal.
- Hold expiry cleanup service that transitions stale `held` bookings to `expired`.
- Audit events for hold creation and expiry.
- Generic unavailable/conflict errors that do not reveal customer, booking, phone, or email details.
- XSS/PII-safe hold response shape with no price, raw notes, raw phone, or raw email.

Implemented in B4:

- Booking-to-Checkout contract service for HELD booking checkout creation.
- Server-side Booking price snapshots used for Checkout amount creation.
- Booking `HELD -> PAYMENT_PENDING` transition on checkout creation/payment initiation.
- Checkout session linkage with `purchasable_type="booking"` and internal booking correlation.
- Booking confirmation only after Checkout success and Billing ledger success evidence.
- Duplicate Checkout and duplicate success callback idempotency.
- Payment failure/cancel/timeout handling that does not confirm Booking.
- Expired-hold late payment reconciliation history without silent booking confirmation.
- Operational BookingFinancialHistory entries for checkout, pending, success, confirmation, failure, and manual review.
- Redis checkout-attempt counters with TTL and Redis-outage-safe behavior.
- PII-safe, public-ID-only payment contract responses.

Implemented in B4A:

- Booking confirmation hardening with explicit Billing ledger `SUCCESS` verification, checkout correlation, amount/currency checks, and booking purchasable linkage validation.
- Transactional confirmation rollback proof: Booking confirmation, audit, financial history, receipt, and notification outbox creation commit all-or-nothing.
- Duplicate callback protection for one confirmation audit event, one payment success history event, one booking confirmed history event, one receipt, and one email notification outbox row.
- Failure-after-success safety: later failed/cancelled/timeout provider events cannot de-confirm a confirmed booking and do not create a refund path.
- Success-after-failure policy: valid late success after a failed provider event is routed to manual review instead of automatic confirmation.
- Expired-hold late payment reconciliation remains manual review; it does not silently confirm or double-book a released slot.
- Customer trust-layer foundation: `BookingReceipt` and `BookingNotification` outbox are generated only after confirmed paid bookings.
- Receipt download foundation with high-entropy hashed expiring tokens, generic errors, and `receipt_downloaded` audit events.
- Receipt and notification snapshots contain redacted customer contact data only and never raw provider callback payloads or Billing ledger truth.

Implemented in B4B:

- Secure `Booking Payment Receipt` PDF generation from receipt snapshots without introducing a tax-invoice workflow.
- Two transactional email outbox types after confirmed paid booking: `booking_confirmed` and `payment_receipt`.
- Fake email provider default for local/CI tests plus Resend/Mailgun-compatible provider interfaces for opt-in external tests.
- Bounded notification delivery service with provider-message hashing, redacted failure storage, retry support, erased-customer skip, and unconfirmed-booking skip.
- Secure receipt PDF download through hashed expiring tokens and audited download events.
- Email/PDF delivery cost and deliverability guidance in `docs/BOOKING_EMAIL_RECEIPT_DELIVERY.md`.

## Deferred Phases

- B5 Reminder Worker and Reschedule Portal.
- B6 Urgent Booking.
- B7 Staff Dashboard.
- B8 Red-Team, Load, and Observability.
