# Privacy Policy

Version: `v2026.06-draft`

Effective date: `[legal-review-date]`

Status: Draft for legal review before production.

Business legal name: `[business legal name]`

Contact email: `[privacy contact email]`

Physical/service location: `[service location placeholder]`

Support channel: `[support channel placeholder]`

Governing law: `[qualified counsel to confirm governing law]`

## Data Collected

The booking system may collect customer name, email, phone number, booking details, payment status references, receipt metadata, reminder and reschedule records, OTP challenge records, technical logs, and security metadata.

The system creates an operational customer record for booking, payment, receipt, reminder, reschedule support, security, fraud-prevention, and legal/accounting purposes. This customer record is not a login account, does not create a password, and does not expose booking history by itself.

The system does not require a customer password for guest booking flows and does not use marketing messages without a separate opt-in. Customers may optionally choose to remember details on the same device for faster repeat booking. Remembered-device convenience stores only an opaque security token in the browser cookie and does not store name, email, phone number, booking ID, receipt token, or payment provider reference in the cookie.

Staff/beautician accounts are separate from customer booking records. Staff authentication may process staff email, password hash, session metadata, password-reset challenge metadata, re-authentication events, and staff security audit events. Staff passwords are not stored in plaintext, reset tokens are stored only as hashes, and staff security audit metadata must be redacted or HMACed.

## Purpose

Data is used to create bookings, initiate checkout, verify payment status, deliver receipts and reminders, protect sensitive actions with OTP, prevent abuse, support customers, and maintain accounting-safe records.

Remembered-device convenience is used only to show a redacted contact summary and reuse saved contact details for a normal future booking. Sensitive actions such as rescheduling, receipt access, contact changes, private booking access, and data-rights requests still require OTP or another approved verification step.

## Payment And Email Processors

M-Pesa or other payment providers process payment prompts and callbacks. Email providers may process redacted delivery requests for receipts, OTPs, and reminders. Hosting, logging, security, database, queue, and cache providers may process technical records.

## Security And Minimization

Operational contact data should be encrypted where needed for later delivery, indexed using keyed HMAC where lookup is required, and redacted in logs, dashboards, public APIs, receipts, emails, and tests. Raw OTPs must not be stored.

Remembered-device lookup tokens must be generated with cryptographically secure randomness. The database stores only keyed-HMAC token hashes. Expired, revoked, forged, or malformed tokens must fail safely and must not reveal whether a customer exists.

## International Customers

The service applies one Kenya Data Protection Act, 2019 / ODPC-aware and GDPR-grade privacy baseline to all customers where practical. Appointment truth remains Africa/Nairobi regardless of browser timezone or customer location. Data may be processed in locations where hosting, payment, email, security, logging, storage, or support providers operate, subject to appropriate safeguards and contractual review before production.

## Rights Requests

Customers may request access, correction, deletion, restriction, or other applicable privacy-rights handling through `[privacy request channel]`. Some financial and booking records may need to be retained for legal, accounting, fraud-prevention, or dispute purposes.

Requests relating to Kenya Data Protection Act, 2019 rights, ODPC complaints/escalations, GDPR data subject rights, and other applicable privacy rights should be routed through `[privacy request channel]` until a production privacy contact and operational workflow are approved.

## Retention And Breach Contact

Retention periods are described in the Data Retention Policy. Breach notification and regulator/customer contact requirements must be reviewed by qualified counsel before production.

## Cookies And Sessions

Essential cookies and session/security controls may be used to protect requests and status flows. Advertising cookies are not expected unless a future consent flow is added.

The optional remembered-device cookie is an essential convenience/security cookie only when the customer explicitly chooses it. It is revocable through forget-device behavior and must be HttpOnly, Secure in production, SameSite-protected, expiring, and free of raw personal data.

Staff portal sessions are essential security sessions for authorized staff only. They do not create customer accounts, do not grant access from customer remembered-device cookies, and expire after configured idle and absolute limits. Recent password re-authentication may be required before staff can reveal operational customer contact details.

## Legal Review

This document is an engineering draft. It must be reviewed and approved by qualified legal counsel before production.
