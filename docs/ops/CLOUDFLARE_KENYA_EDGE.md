# Cloudflare edge for Kenya latency (Safaricom / Airtel)

Operator runbook. Phase 3D-PLUS still does **not** auto-provision Cloudflare;
this document is the deploy checklist + rollback for `sheeaesthetics.co.ke`.

## Goals

- Cache marketing `/images/*` at Nairobi/Mombasa PoPs so return visits and second navigations stop re-pulling heroes from origin over slow mobile data.
- Never cache booking mutations (`/api/bookings/**` POST) or private gallery drafts.
- Keep origin nginx (`frontend-edge`) as the source of truth for `/images` sendfile.

## DNS / proxy

1. Add the zone in Cloudflare; set nameservers at the registrar.
2. Orange-cloud (proxied) A/AAAA (or CNAME) for `sheeaesthetics.co.ke` and `www` → origin VPS that publishes **frontend-edge :80** (and API host if separate).
3. SSL/TLS mode: **Full (strict)** with a valid origin cert (or Cloudflare Origin CA).
4. Enable HTTP/2, HTTP/3, Brotli. Leave Polish/Mirage **off** for beauty heroes (use pre-resized 640/960/1280 instead).

## Cache Rules (recommended)

| URI / match | Action |
|-------------|--------|
| `/images/*` | Cache Everything; Edge TTL ≥ 30d (origin already sends `immutable` 1y) |
| `/_nuxt/*` | Cache Everything; long TTL |
| `/api/bookings/*` | **Bypass** cache |
| `/api/customers/*` | **Bypass** cache (remember-device cookies) |
| `/api/csrf/` | Bypass |
| HTML `/`, `/book/*`, `/booking/*` | Bypass or short TTL only if SSR is fully public |

Respect origin `Cache-Control`. Do not “Cache Everything” on `/media/public/` without matching the 5-minute revoke policy in app code.

## WAF / bots (align with WAF_CDN_ABUSE_POLICY.md)

- Bot Fight / managed challenge on volumetric scrapes of `/images/*` (allow normal browsers).
- Challenge repeated `/media/` resolver misses and raw media probing.
- **Do not** challenge STK initiate or checkout POSTs after Turnstile success.
- Preserve M-Pesa webhook paths (provider allowlist / shared secret stays in Django).

## App env when going live behind Cloudflare

Set (examples):

```bash
CSRF_TRUSTED_ORIGINS=https://sheeaesthetics.co.ke,https://www.sheeaesthetics.co.ke
CORS_ALLOWED_ORIGINS=https://sheeaesthetics.co.ke,https://www.sheeaesthetics.co.ke
NUXT_PUBLIC_SITE_URL=https://sheeaesthetics.co.ke
NUXT_PUBLIC_API_BASE_URL=https://api.sheeaesthetics.co.ke   # or same-origin proxy path
ALLOWED_HOSTS=sheeaesthetics.co.ke,www.sheeaesthetics.co.ke,...
TRUSTED_PROXY_CIDRS=<Cloudflare IP ranges>
SECURE_SSL_REDIRECT=True
```

Keep local compose defaults (`http://127.0.0.1:3000`) for desk development.

## Rollback

1. Cloudflare DNS: set the production record to **DNS only** (grey cloud) so traffic hits origin directly — images still served by nginx-edge; latency rises but site stays up.
2. Or pause the zone / revert nameservers at the registrar (slower).
3. Remove any Cache Rule that accidentally cached `/api/bookings/*` immediately if checkout misbehaves.
4. Confirm CSRF/CORS still list the public HTTPS origins after rollback if you stay on CF hostnames.

## Verify (Kenya)

- Cold vs warm LCP on a phone tethered to Safaricom/Airtel data (or WebPageTest Nairobi).
- Target: LCP ≤ ~3s on Slow 3G-class after CF warm; booking hold interactive ≤ ~2s p95 once page is ready.
- `node frontend/scripts/sync-prod-images.mjs` then recreate `frontend-edge` with `docker/images-prod`.
- `node frontend/scripts/sim-hero-assets.mjs --clients 100` against the public edge hostname.

### Local smoke baseline (origin nginx edge, pre-Cloudflare)

Recorded during implementation:

- `/images/hero-makeup-960.jpg` → 200 + `Cache-Control: public, max-age=31536000, immutable`
- `/images/_cand1.jpg` → 404 (underscore deny)
- 100 visits × homepage + first-paint heroes → 0 failures, image p95 ≪ 2s

Cloudflare PoP warm is expected to improve **first** Kenya cold loads further once DNS is orange-clouded.
