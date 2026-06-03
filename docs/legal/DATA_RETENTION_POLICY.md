# Data Retention Policy

Version: `v2026.06-draft`

Effective date: `[legal-review-date]`

Status: Draft for legal review before production.

Business legal name: `[business legal name]`

Contact email: `[privacy contact email]`

## Record Categories

Booking records, payment and ledger records, receipt records, reminder records, reschedule records, OTP challenges, notification records, logs, support requests, and audit records are retained only for defined operational, legal, accounting, fraud-prevention, and security purposes.

## Retention Strategy

Operational PII should be minimized, encrypted, HMACed, redacted, erased, or anonymized where compatible with financial and booking audit obligations. Raw OTPs are not retained. Raw provider payloads should not be logged by default.

## Backups

Backups may retain data until their normal rotation expires. Backup access must be limited and audited.

## Deletion And Review

Deletion, anonymization, and legal-hold decisions require policy review. Accounting-safe financial history should preserve integrity while minimizing personal identifiers.

## Legal Review

This document is an engineering draft. It must be reviewed and approved by qualified legal counsel before production.
