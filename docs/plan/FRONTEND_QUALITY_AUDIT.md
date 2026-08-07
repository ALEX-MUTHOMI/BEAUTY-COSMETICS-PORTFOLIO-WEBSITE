# Frontend quality audit (CodeRabbit-style)

**Branch:** `audit/frontend-full-quality`
**Status:** Living audit — findings feed remediation PRs
**Scope:** `frontend/` (Nuxt 3) — thin client over Django; no mock SPA money path

## Diff log (GitHub)

| Range | Purpose |
|-------|---------|
| [7457602...8d87bc2](https://github.com/ALEX-MUTHOMI/aesthetic-os/compare/7457602...8d87bc2) | Guest booking conversion → remember-device → STK copy |
| [85fbf82...9eb8246](https://github.com/ALEX-MUTHOMI/aesthetic-os/compare/85fbf82...9eb8246) | Fortress Nuxt patches + SiteLoader types |
| Backend money path | See [BACKEND_QUALITY_AUDIT.md](./BACKEND_QUALITY_AUDIT.md) |

Related: [CASS_FRONTEND_SECURITY.md](./CASS_FRONTEND_SECURITY.md), [GDPR_DPA_2019_BOOKING_DATA_MAP.md](../security/GDPR_DPA_2019_BOOKING_DATA_MAP.md), [CLOUDFLARE_KENYA_EDGE.md](../ops/CLOUDFLARE_KENYA_EDGE.md), [AGENTIC_AEO_CLOUDFLARE.md](../ops/AGENTIC_AEO_CLOUDFLARE.md)

---

## Checklist (every ring)

Correctness · Privacy (no PII leak) · Thin Django client · TDD · Comments · CSP/cookies · Agent Readiness / AEO

---

## Ring F1 — Booking / money UI

| Severity | Finding | Evidence |
|----------|---------|----------|
| Major | Remember-device GET used `credentials: omit` by default — device cookie may not send cross-origin | `rememberDevice.ts` → `publicBookingGet` |
| Minor | Playwright e2e thin on hold→checkout→STK | e2e suite CSP-heavy |
| OK | Guest STK boundary locked to `/api/bookings/checkout/mpesa/stk/` | `bookingGuestStkBoundary.spec.ts` |
| OK | CSRF + Turnstile + idempotency on writes | `bookingWriteApi.ts`, governors |

---

## Ring F2 — Staff PII surface

| Severity | Finding | Evidence |
|----------|---------|----------|
| OK | Contact reveal requires re-auth | `StaffContactRevealModal.vue` |
| OK | No JWT/Bearer in localStorage (staff cookie session) | `staffAuth.ts` + red-team |
| Minor | Large staff panels (~768–659 lines) | readability debt |

---

## Ring F3 — Landing / marketing

| Severity | Finding | Evidence |
|----------|---------|----------|
| Major | `pages/index.vue` ~3k lines — structure debt | hero/work/offer/visit monolith |
| OK | No public contact form posting PII (WA/tel only) | `useLandingContact.ts` |
| OK | Gallery via Django public API | `homeWorkGallery.ts` |

---

## Ring F4 — Security infra

| Severity | Finding | Evidence |
|----------|---------|----------|
| Major | CSP missing explicit `object-src` / `base-uri` / tight `connect-src` in live config | `nuxt.config.ts` vs `securityHeaders.spec.ts` |
| OK | Sentry scrubber GDPR/DPA | `sentryPiiScrubber.ts` |
| OK | Funnel debug: no email/phone | `funnelEvents.ts` |

---

## Ring F5 — Privacy / DPA UX

| Severity | Finding | Evidence |
|----------|---------|----------|
| Blocker | Privacy page not aligned with legal draft; no rights-request UI | `pages/privacy.vue` vs API `privacy/rights-request/` |
| Major | Data map published on API but not linked from privacy page | `GET /api/bookings/privacy/data-map/` |

---

## Ring F6 — Agentic AEO

| Severity | Finding | Evidence |
|----------|---------|----------|
| OK | Origin sitemap + `llms.txt` + Content Signals robots | `frontend/public/` |
| OK | FAQPage / OfferCatalog JSON-LD + Meru citation copy | `agentSeo.ts`, FAQ/services pages |
| Ops | CF Agent Readiness / Markdown / Labyrinth | [AGENTIC_AEO_CLOUDFLARE.md](../ops/AGENTIC_AEO_CLOUDFLARE.md) (zone must be orange-clouded) |

---

## Remediation tracking

| ID | Finding | Status |
|----|---------|--------|
| F1-cred | Remember-device GET `credentials: include` | Fixed (prior PR) |
| F1-e2e | Playwright money-path hold→STK→status with fixtures | Fixed this arc |
| F3-split | Extract landing SFCs (hero/glow/work/offer/steps/packages/reviews/visit) | Fixed this arc |
| F4-csp | Tighten CSP object/base/connect-src + cookie contract | Fixed (prior PR) |
| F4-tt | Permissions-Policy + CSP report-only / Trusted Types prep (env-gated) | Fixed this arc |
| F5-privacy | Align privacy page + rights-request form | Fixed (prior PR) |
| F5-thin | Vitest thin-client / no Nuxt PII proxy contract | Fixed (prior PR) |
| F5-agent-pii | Agent/DOM PII storage + staff reveal red-team Vitest | Fixed this arc |
| F6-aeo | Origin AEO assets + CF Agent Readiness runbook | Fixed this arc |

---

## Can a client safely book?

Gate: Django owns holds/checkout/STK; Nuxt is credentialed thin client; Turnstile+CSRF; no plaintext PII in browser storage; privacy rights intake available; origin CSP + Permissions-Policy; CF Client-Side Security + Agent Readiness when orange-clouded; good agents can cite Meru salon via sitemap/`llms.txt`/JSON-LD without indexing money-path or staff.
