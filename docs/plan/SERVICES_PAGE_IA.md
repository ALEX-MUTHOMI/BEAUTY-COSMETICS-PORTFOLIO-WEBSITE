# Services Page Information Architecture Plan

**Status:** Phase 2 complete — secure booking handoff (2026-07-06)

## Phase 1 mobile & visual (final)

- [x] Neutral white / `#fafafa` sections — removed heavy pink gradients
- [x] Active tabs: soft rose tint + dark text (not solid rose fill)
- [x] Touch targets ≥ 44px on tabs, paths, details links
- [x] Mobile book bar clearance (`padding-bottom` + safe areas)
- [x] Day banner stacks on narrow screens
- [x] `@media (hover: hover)` — hover only on pointer devices; `:active` on tap
- [x] E2E: `e2e/services-mobile.spec.ts`  
**Last updated:** 2026-07-06  
**Owners:** Frontend / product  

## Problem statement

The homepage and `/services` both present packages, singles, and a detailed treatment menu with different structures and nav targets. Users cannot tell whether to use **Packages** (homepage anchor), **Our Services** (separate page), or **Treatment menu** (third path). Marketing priority is **full packages**; a large segment books **single treatments** (e.g. one wax or massage).

## Booking intents (canonical model)

| Intent | Days | User need | Business priority |
|--------|------|-----------|-------------------|
| **Full package** | Tue & Wed | Multiple treatments, one visit | Primary — market first |
| **Single treatment** | Mon · Thu – Sat | One service category or specific item | Secondary — must be frictionless |

The **treatment menu** is not a third intent. It is the **price list** for singles (and transparency for package inclusions).

## Page roles

| Page | Role |
|------|------|
| **Homepage (`/`)** | Marketing, trust, featured packages, singles teaser, book CTA |
| **Services (`/services`)** | Canonical pricing & detail: packages → singles → menu under singles |

## Vocabulary (locked)

- **Full package** — Tue & Wed, multiple treatments in one private visit  
- **Single treatment** — Mon · Thu – Sat, one service  
- **Treatment menu** — Detailed options under single treatments (not a separate booking type)

## Navigation (Phase 1)

| Nav label | Target | Notes |
|-----------|--------|-------|
| Our Services | `/services` | Pricing hub |
| Packages | `/services#full-packages` | Canonical package detail |
| Singles | `/services#single-sessions` | Canonical singles + menu entry |

Homepage `#packages` and `#singles` sections remain for scroll-on-home marketing; primary nav points to `/services` anchors.

## `/services` layout (Phase 1)

1. Hero — “How would you like to visit?” + day-rule banner  
2. **Two** intent paths (not three): Full package (emphasized) | Single treatment  
3. Full packages section (`#full-packages`)  
4. Single treatments section (`#single-sessions`) with category cards  
5. Treatment menu nested under singles (`#treatments`) — “All treatments & prices”  
6. Footer CTA  

Hash allowlist (security): `full-packages`, `single-sessions`, `facials`, `massage`, `waxing`, `makeup`. Unknown hashes are ignored.

## User journeys

### Package client (primary)

Home → Welcome “Full glow days” or Nav Packages → `/services#full-packages` → Book package.

### Single wax / massage client

Home → “Single sessions” or Nav Singles → `/services#single-sessions` → Waxing card “See all options” → `#waxing` tab → select treatment → book.

## Phases

### Phase 1 — IA & nav (this release)

- [x] Document plan (this file)  
- [x] Two-intent services hero; remove third path card  
- [x] Nest treatment menu under singles  
- [x] Align header/footer nav to `/services` anchors  
- [x] Homepage welcome + singles link to `/services`  
- [x] Single cards deep-link to category tabs (allowlisted hashes)  
- [x] Day-rule banner on services page  

### Phase 2 — Booking handoff & availability (complete)

- [x] Allowlisted query params: `type`, `plan`, `category`, `treatment` via `parseBookHandoffQuery()`  
- [x] `/book` page — resolved selection, **live availability calendar**, time-slot picker  
- [x] Backend: `resolve-handoff` → `calendar` → `availability` (two-phase; no booking logic in Nuxt)  
- [x] Calendar: **offered weekdays only** (Tue/Wed packages, Mon/Thu–Sat singles), week grouping, roll-forward  
- [x] Package cards & treatment picker → secure `/book?…` URLs  
- [x] Unit + E2E security tests  
- [x] `seed_marketing_catalog` — DB rows for all homepage/services slugs  

### Phase 3 — Calendar service (booking domain)

**Design doc:** [CALENDAR_SERVICE_PHASE_3.md](./CALENDAR_SERVICE_PHASE_3.md)

Catalog-aware scheduling service: every marketing offering resolves to a `BookableSelection`, deterministic day classification, bounded algorithms, Newman contract tests, latency + security gates.

Sub-phases: 3a registry → 3b policy engine → 3d Newman/security → 3c performance → 3e per-service overrides (if needed).

### Phase 4 — Homepage dedupe (IA)

- Shorten homepage singles to teaser + link; avoid duplicate scroll on one journey  
- Optional `?intent=package|single` on `/services` for emphasis  

## Success metrics

- Package path: homepage or nav → package card → book in ≤3 clicks  
- Single path: nav → category → optional specific treatment → book in ≤4 clicks  
- No user reads full packages twice on one journey without choosing to  
- Analytics: `services_section_view`, `category_tab`, `treatment_select` (Phase 4+)

## Security notes (Phase 2)

- Book query tokens: `normalizeBookQueryToken()` — URI decode, strip path/query, `[a-z0-9-]+` only, max 64 chars  
- Package `plan` and treatment slugs resolved from static catalog allowlists (`bookingCatalog.ts`)  
- Treatment slug must match `category` or entire handoff rejected  
- Invalid `type` or unknown slugs → generic `/book` (no attacker-controlled labels rendered)  
- Day validation is **server-side only** (`bookings/domain/calendar.py`, `day_policy.py`); frontend renders API statuses  
- E2E: `frontend/e2e/book-handoff-security.spec.ts` — injection, CSP headers  

## Security notes (Phase 1)

- Section/category hashes validated via `parseServicesHash()` — URI decode, strip path/query, alphanumeric allowlist only  
- Unknown or malicious hashes (`<script>`, `javascript:`, encoded newlines) are ignored — no tab change, no `getElementById` with attacker input  
- `history.replaceState` only writes allowlisted section/category tokens  
- No user-controlled strings in `innerHTML` or `v-html` on services surfaces  
- External links: `rel="noopener noreferrer"` (existing header pattern)  
- E2E: `frontend/e2e/services-security.spec.ts` — hash injection, nav anchors, CSP headers

## Test plan (Docker)

```bash
docker compose build frontend
docker compose up -d frontend
# Manual: /services, /services#full-packages, /services#waxing
# Nav: Packages, Singles from header
docker compose --profile test up -d --build frontend-test
docker compose exec -T frontend-test npm run type-check
docker compose exec -T frontend-test npm run test
docker compose exec -T frontend-test npm audit --audit-level=high
PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:e2e -- e2e/services-security.spec.ts
PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:e2e -- e2e/book-handoff-security.spec.ts
```

## Security review (Phase 1)

| Threat | Mitigation |
|--------|------------|
| DOM XSS via `#hash` | `parseServicesHash()` + `normalizeServicesHash()` allowlist; rejects `<>"'`, path traversal, `javascript:` |
| Open redirect via hash | Only `full-packages`, `single-sessions`, `facials`, `massage`, `waxing`, `makeup` applied to scroll/tab state |
| `getElementById` injection | Hash token restricted to `[a-z0-9-]+` before use |
| CSP bypass (inline script) | Nuxt Security nonce CSP; no `unsafe-inline` in `script-src` (see `securityHeaders.spec.ts`) |
| Clickjacking | `X-Frame-Options: DENY` on `/services` |
| Secret leakage in HTML | E2E checks no `SECRET_KEY`, Turnstile secret in public HTML |
| Dependency CVEs | `npm audit --audit-level=high` in CI |

Automated coverage: `servicesNavigation.spec.ts` (unit), `e2e/services-security.spec.ts` (Playwright).
