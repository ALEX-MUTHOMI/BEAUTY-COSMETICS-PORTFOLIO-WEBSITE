# ADR-005: Booking No-Refund Reschedule Policy

## Status

Accepted

## Context

The product policy avoids a customer self-service refund flow in the Booking domain.

## Decision

Booking supports reschedule requests. Billing remains the owner of financial corrections. Free reschedules reference original billing evidence. Additional-fee reschedules later create Checkout sessions.

## Consequences

Booking does not create zero-value ledger rows or mutate Billing state.

## Security Implications

Attackers cannot use rescheduling to rewrite financial truth or create refunds from Booking.

## Testing Implications

Tests must prove Booking stores operational financial history only and does not expose refund creation.
