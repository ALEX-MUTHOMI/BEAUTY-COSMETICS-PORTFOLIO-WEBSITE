# Security Headers Policy

This document describes the backend/API response-header policy. It does not
replace a future Nuxt/frontend CSP policy.

## Backend/API Header Policy

The Django backend applies security headers to API, health, utility, and error
responses:

- `Content-Security-Policy` blocks object embedding, external script/style
  execution, and framing for backend/API responses.
- `Permissions-Policy` disables browser capabilities that the API does not need,
  including camera, microphone, geolocation, USB, payment, and browsing topics.
- `Cross-Origin-Resource-Policy: same-origin` prevents unintended cross-origin
  resource inclusion.
- `Cross-Origin-Opener-Policy: same-origin` is provided by Django security
  settings where supported.
- `Referrer-Policy: same-origin` avoids leaking route details to external
  origins.
- `X-Content-Type-Options: nosniff` prevents content-type confusion.
- `X-Frame-Options: DENY` remains active through Django clickjacking middleware.
- Sensitive API, health, auth, checkout, booking, billing, staff, legal, and
  error responses are marked `no-store`.

Existing stricter or exact `Cache-Control: no-store` contracts are preserved.

## CSRF Cookie Policy

`csrftoken` intentionally remains JavaScript-readable because the decoupled
frontend must read it and submit it in the CSRF header. ZAP classifies this as
`Cookie No HttpOnly Flag`; this is accepted for the CSRF token only.

`sessionid` is expected to remain HttpOnly. In staging and production, cookies
must be `Secure` and use the configured SameSite policy over HTTPS.

## Frontend/Nuxt CSP Is Not Complete Yet

The backend CSP is not the final browser policy for the Nuxt application. The
frontend must receive a separate CSP later, after all production origins are
known. Future frontend CSP work may need to account for:

- image/CDN domains;
- font domains;
- analytics domains, if introduced;
- payment-provider redirect domains;
- map, social, or embed domains, if introduced.

Do not treat the backend CSP as proof that frontend XSS hardening is complete.

## Staging/Production Follow-Up

Before production:

- verify headers behind the real HTTPS reverse proxy/CDN;
- confirm proxy/CDN layers do not strip security headers;
- verify Secure cookie behavior over HTTPS;
- test the Nuxt-specific CSP separately;
- rerun passive ZAP and Newman through the staging domain.
