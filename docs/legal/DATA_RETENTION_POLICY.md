# Data Retention Policy

Version: `v2026.06-draft`

Effective date: `[legal-review-date]`

Status: Draft for legal review before production.

Business legal name: `[business legal name]`

Contact email: `[privacy contact email]`

## Record Categories

Booking records, payment and ledger records, receipt records, reminder records, reschedule records, OTP challenges, notification records, logs, support requests, and audit records are retained only for defined operational, legal, accounting, fraud-prevention, and security purposes.

Operational customer records are retained only while needed for booking, payment, receipt, reminder, reschedule support, dispute handling, security, fraud-prevention, legal, accounting, or support purposes. They do not create customer login accounts and should be minimized, erased, or anonymized when retention is no longer justified and legal/accounting constraints permit.

## Retention Strategy

Operational PII should be minimized, encrypted, HMACed, redacted, erased, or anonymized where compatible with financial and booking audit obligations. Raw OTPs are not retained. Raw provider payloads should not be logged by default.

Remembered-device active tokens should expire after a short configurable period, normally 30 to 90 days. The browser cookie contains only an opaque token, and the database stores only a keyed-HMAC token hash. Expired or revoked remembered-device records should be cleaned up or anonymized after the defined operational review period.

OTP challenges should be deleted or anonymized after their short security-retention window, normally 30 to 90 days. Booking flow sessions and non-sensitive status recovery state should expire quickly, normally 30 to 60 minutes unless a shorter security policy applies.

## Backups

Backups may retain data until their normal rotation expires. Backup access must be limited and audited.

## Deletion And Review

Deletion, anonymization, and legal-hold decisions require policy review. Accounting-safe financial history should preserve integrity while minimizing personal identifiers.

## Legal Review

This document is an engineering draft. It must be reviewed and approved by qualified legal counsel before production.
