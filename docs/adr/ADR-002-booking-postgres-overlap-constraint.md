# ADR-002: Booking PostgreSQL Overlap Constraint

## Status

Accepted

## Context

A simple unique constraint on start time cannot prevent partial overlaps such as 09:30 to 10:30 against 10:00 to 11:00.

## Decision

Use PostgreSQL `btree_gist` and an exclusion constraint combining resource equality with `TSTZRANGE(starts_at, ends_at, "[)")` overlap checks. Only blocking statuses participate.

## Consequences

The database rejects concurrent overlapping active bookings. Adjacent bookings are allowed because the upper bound is exclusive.

## Security Implications

Double-booking race attacks must hit a database constraint, not only application validation.

## Testing Implications

Tests must assert overlapping active bookings fail and adjacent bookings pass.
