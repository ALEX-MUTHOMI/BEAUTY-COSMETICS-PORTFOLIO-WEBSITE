# ADR-004: Booking PII GDPR-Style Privacy

## Status

Accepted

## Context

Booking needs operational contact data for reminders and staff workflow, but phone and email values are sensitive and enumerable.

## Decision

Store encrypted operational PII, keyed-HMAC lookup hashes, and redacted display values. Plain SHA256 is forbidden for phone and email lookup.

## Consequences

Reminder delivery can decrypt contact fields when consent allows. Search can use HMAC values. Logs and dashboards use redacted fields.

## Security Implications

Raw PII logging is prohibited. Erasure removes decryptable contact data while preserving accounting-safe operational history.

## Testing Implications

Tests must prove raw names, phones, and emails are not stored in plaintext fields and that missing secrets fail closed outside debug mode.
