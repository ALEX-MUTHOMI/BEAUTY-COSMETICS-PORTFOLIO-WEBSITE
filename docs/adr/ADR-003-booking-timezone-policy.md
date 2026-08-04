# ADR-003: Booking Timezone Policy

## Status

Accepted

## Context

Customers and staff operate in Africa/Nairobi, while the backend must avoid ambiguous local timestamps.

## Decision

Persist timezone-aware UTC datetimes. Reject naive datetimes. Apply Africa/Nairobi for business-hour boundaries, validation, and presentation.

## Consequences

Frontend timestamps with `+03:00` are converted to UTC before persistence. The database remains consistent across clients.

## Security Implications

Attackers cannot extend holds or bypass closed-day policy using timezone ambiguity.

## Testing Implications

Tests must cover UTC persistence, Nairobi boundary validation, stale/future metadata, and naive datetime rejection.
