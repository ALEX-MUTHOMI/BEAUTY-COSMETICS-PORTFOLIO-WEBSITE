# Services page load — issue log

**Date:** 2026-07-05  
**Route:** `/services`  
**Report:** Navigation to Services felt very slow (full-screen “Loading…” delay).

## Root cause

1. **`SiteLoader` lived in `layouts/landing.vue`**  
   Every public page using the landing layout (including `/services`, `/privacy`, `/terms`) mounted the loader and ran the same preload pipeline as the homepage.

2. **Homepage assets preloaded on Services**  
   `SiteLoader` blocked the UI while preloading `hero-1.jpg` (large hero image, up to **1800ms** timeout per asset) plus a **450ms** minimum display time — even though Services does not use the hero.

3. **`html.is-loading` on all landing pages**  
   The layout set `is-loading` on `<html>`, which sets `overflow: hidden` (`motion.css`) and prevented scrolling until the loader finished.

## Impact

| Scenario | Before fix | Typical delay |
|----------|------------|---------------|
| Direct visit to `/services` | Full loader + hero preload | **~0.5–2.3s** |
| Click “Services” from homepage (same session) | Loader could re-run if layout remounted | **~0.5–2.3s** |
| After fix | No loader on `/services` | **Immediate SSR paint** |

## Fix (2026-07-05)

- Moved `SiteLoader` to **`pages/index.vue` only** (homepage).
- Removed `is-loading` from **`layouts/landing.vue`**; homepage sets it via `useHead`.
- `SiteLoader` skips on repeat homepage visits in the same tab (`sessionStorage: shee-loader-done`).
- `SiteLoader` clears `is-loading` on unmount (safe early navigation away from home).
- Services category images: only the first category loads eagerly; others use `loading="lazy"` and `fetchpriority="low"`.

## Verify

```powershell
docker compose build frontend
docker compose up -d frontend
```

1. Hard refresh `http://localhost:3000/services` — **no** full-screen loader.
2. Homepage `http://localhost:3000/` — loader still shows on first visit only.
3. Click **Our Services** — instant client navigation.

## Follow-ups (optional)

- Re-run `fetch-landing-images.ps1` for smaller JPEG widths if category images still feel heavy on slow networks.
- Add `@nuxt/image` for responsive `srcset` if image weight remains an issue.
