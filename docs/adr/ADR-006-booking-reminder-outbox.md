# ADR-006: Booking Reminder Outbox

## Status

Accepted

## Context

Reminder dispatch can fail after a booking transaction commits. Relying only on Celery task enqueue creates lost-reminder risk.

## Decision

Persist `BookingReminder` rows as a transactional outbox. Workers later sweep pending rows and recheck sendability.

## Consequences

Reminder intent survives worker, Redis, and provider outages.

## Security Implications

Send-time checks must honor consent and erasure. Provider IDs and failures must be hashed or redacted.

## Testing Implications

Tests must assert pending rows are durable, cancellable, and not sendable after erasure or consent loss.
