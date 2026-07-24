# Landing / marketing frontend modules

Nuxt stays a **static-ish marketing + booking UI**. Django owns auth, payments,
and PII. Browser calls `NUXT_PUBLIC_API_BASE_URL` directly — do not add Nuxt
`server/` API routes that proxy booking or secrets.

## File map

| Module | Role |
|--------|------|
| `landingContent.ts` | Copy, packages, contact fail-closed helpers |
| `useLandingContact.ts` | Runtime WhatsApp/phone from `runtimeConfig` |
| `primaryBookHref.ts` | Day-aware Book target (Africa/Nairobi) |
| `useLandingBookCta.ts` | Header/footer/sticky Book href (handoff + day bias) |
| `bookingHandoff.ts` | Deep links into `/book/...` + last-path memory |
| `heroMedia.ts` | Hero slide image sources + responsive variants |
| `homeWorkGallery.ts` | Public gallery fetch with short abort + static fallback |
| `funnelEvents.ts` | Lightweight `shee-funnel` CustomEvents (no PII) |
| `useLandingSeo.ts` | Shared SEO meta for landing layout pages |

## Contact / WhatsApp

Set `NUXT_PUBLIC_WHATSAPP_E164` (E.164 digits, no `+`). Until set, UI shows
pending copy and hides `wa.me` / `tel:` links. Never use `254700000000` live.

## Images

- Source of truth for local/dev: `frontend/public/images/`
- Edge/prod sync target: `frontend/docker/images-prod/` (see `scripts/sync-prod-images.mjs`)
- Scratch folders (`_new/`, `_ke_cands/`) are gitignored — do not commit candidates
