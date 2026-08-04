# ADR-008: Booking Staff Dashboard Security

## Status

Accepted

## Context

Staff booking dashboards expose sensitive operational data and are high-value abuse targets.

## Decision

Default staff views must show redacted contact data. Contact reveal and status overrides require permission checks and audit events.

## Consequences

Later dashboard work must build around RBAC, redacted summaries, audited reveal, and protected exports.

## Security Implications

Unrestricted CSV export or bulk contact reveal is prohibited until explicitly designed and tested.

## Testing Implications

Tests must prove unauthorized reveal fails, authorized reveal audits, and summaries stay redacted.
