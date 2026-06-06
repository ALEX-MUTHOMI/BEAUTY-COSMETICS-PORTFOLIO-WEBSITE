# Cookie Notice

Version: `v2026.06-draft`

Effective date: `[legal-review-date]`

Status: Draft for legal review before production.

Business legal name: `[business legal name]`

Contact email: `[privacy contact email]`

## Essential Cookies

The service may use essential security, CSRF, session, booking flow continuity, rate-limit, customer action/session security, and status-recovery cookies or equivalent storage needed for secure operation.

Essential cookies help protect requests, prevent cross-site request forgery, preserve short booking or OTP status flows, and reduce abuse. They must not contain raw phone numbers, raw email addresses, OTPs, payment provider references, or other unnecessary personal data.

If a customer explicitly chooses "Save my details on this device for faster booking next time", the service may set an optional remembered-device cookie. This cookie contains only an opaque random token, not the customer's name, email, phone number, booking ID, receipt token, payment reference, or provider identifier. The server stores only a keyed-HMAC hash of the token and returns only a redacted contact summary.

Remembered-device convenience does not create a login account and does not allow sensitive actions such as rescheduling, receipt download, contact updates, or private booking history access without OTP or another approved verification step. Customers can forget/revoke the remembered device, which clears the cookie and invalidates the server-side token hash.

Staff portal sessions use essential HttpOnly, SameSite-protected Django session cookies. Staff auth state is server-side; staff bearer tokens must not be stored in `localStorage` or `sessionStorage`. Staff sessions expire after configured idle and absolute lifetimes, and sensitive actions such as customer contact reveal require recent password re-authentication.

## Analytics And Advertising

We do not currently use analytics or marketing cookies. Advertising cookies are not part of the current baseline. If analytics, marketing, or third-party advertising cookies are added later, they must be reviewed and gated behind an appropriate consent flow before loading.

## Legal Review

This document is an engineering draft. It must be reviewed and approved by qualified legal counsel before production.
