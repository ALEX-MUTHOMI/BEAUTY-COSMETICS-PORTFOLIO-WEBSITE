# ADR-001: Booking Domain Boundaries

## Status

Accepted

## Context

Booking, Checkout, and Billing are separate bounded contexts. Mixing scheduling, provider orchestration, and ledger truth creates coupling and weakens financial correctness.

## Decision

`bookings/` owns scheduling and booking workflow. `checkout/` owns payment orchestration. `billing/` owns immutable financial truth. Booking may store checkout and billing references only for operational visibility.

## Consequences

Booking cannot initiate M-Pesa, process provider callbacks, or mutate ledger records. Later integration must use narrow contracts.

## Security Implications

Attackers cannot force ledger success by manipulating booking endpoints. Payment and financial invariants remain isolated.

## Testing Implications

Booking tests must prove scheduling behavior without crossing into Checkout or Billing. Integration tests later prove the contract between domains.
