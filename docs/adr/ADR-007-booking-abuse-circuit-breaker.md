# ADR-007: Booking Abuse Circuit Breaker

## Status

Accepted

## Context

Attackers can exhaust booking holds and force database-heavy capacity checks.

## Decision

Use Redis rolling counters for abuse signals and modes: `NORMAL`, `ELEVATED`, `ABUSE`, and `LOCKDOWN`. Every `INCR` must refresh `EXPIRE`.

## Consequences

The system can shorten hold TTLs and require stronger proof under attack without scanning PostgreSQL aggregates.

## Security Implications

Redis failures fail safe to lockdown. Counters must expire to avoid permanent denial of service.

## Testing Implications

Tests must cover mode transitions, expiry refresh, and Redis failure behavior.
