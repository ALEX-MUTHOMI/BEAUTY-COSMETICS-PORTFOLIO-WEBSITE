# Frontend CSP Policy

Backend API CSP is not the final Nuxt/browser CSP story. The frontend already
uses `nuxt-security`, `nuxt-csurf`, and Cloudflare Turnstile integration in
`frontend/nuxt.config.ts`; this document defines the safe hardening boundary.

## Current Frontend Asset Inventory

- Scripts: `self`, Cloudflare Turnstile.
- Frames: `self`, Cloudflare Turnstile.
- Styles: current Nuxt build may require runtime-injected styles.
- Images: local/public assets and API-provided gallery URLs.
- Connect/API: local backend API in development, staging/production API domains
  in deployed environments.
- Fonts/media: no committed third-party font or media domains were identified in
  the current config.

## Proposed CSP By Environment

Local:

- allow `localhost` frontend/backend ports required for development;
- allow Cloudflare Turnstile challenge domains;
- do not copy local allowances into staging/production.

Staging:

- explicit frontend domain;
- explicit API domain;
- Cloudflare Turnstile challenge domains only if Turnstile is enabled;
- no broad `*`.

Production:

- HTTPS-only allowlist;
- no `unsafe-inline` unless the built Nuxt output proves it is required and the
  risk is documented;
- report-only rollout before enforce mode.

## Implementation Layer

The current implementation layer is Nuxt via `nuxt-security`. Reverse proxy or
CDN headers may be added later, but only one enforcing CSP policy should own the
final production response to avoid contradictory headers.

## Verification

Recommended commands:

```powershell
docker compose exec frontend-test npm run test
docker compose exec frontend-test npm run type-check
docker compose exec frontend-test npm run build
curl.exe -I http://localhost:3000/
```

This phase documents the policy and keeps backend CSP from being misrepresented
as complete frontend CSP. Further enforcement changes should include frontend
build and browser checks.

