# Agentic AEO + Cloudflare Agent Readiness

Operator runbook for **promoting** Shee Aesthetics (Meru) to answer engines and assistants while **defending** malicious scrapers and synthetic booking abuse.

Prerequisite: production DNS for `sheeaesthetics.co.ke` / `www` is **orange-clouded** (see [CLOUDFLARE_KENYA_EDGE.md](./CLOUDFLARE_KENYA_EDGE.md)). Origin AEO assets (`sitemap.xml`, `llms.txt`, Content Signals in `robots.txt`, JSON-LD) ship from the Nuxt app regardless; dashboard Agent Readiness / Markdown for Agents / AI Labyrinth only activate once proxied.

Related: [WAF_CDN_ABUSE_POLICY.md](../security/WAF_CDN_ABUSE_POLICY.md), [CASS_FRONTEND_SECURITY.md](../plan/CASS_FRONTEND_SECURITY.md)

---

## Content Signals (chosen policy)

Local-service promotion posture:

| Signal | Value | Intent |
|--------|-------|--------|
| `search` | `yes` | Allow search / answer engines to discover and cite |
| `ai-input` | `yes` | Allow assistants to use page text when answering users |
| `ai-train` | `no` | Prefer not donating full site text to opaque training corpora |

Enforce training-scraper blocks with **Bot Fight / WAF / AI Labyrinth**, not robots alone. Origin `frontend/public/robots.txt` is the **source of truth** for signals + `Disallow: /staff`.

**Managed robots conflict rule:** if Cloudflare managed robots.txt would overwrite or strip custom Content Signals, **disable CF managed robots** and keep origin. Document the choice in the zone checklist below.

---

## Promote vs defend matrix

| Goal | Cloudflare / origin control | Notes |
|------|----------------------------|-------|
| Agents find marketing pages | Origin `sitemap.xml` + `llms.txt` | Exclude staff, status, confirmation, money UI |
| Clean agent reading | **Markdown for Agents** on `/`, `/services`, `/faq` | Dashboard → Fundamentals / Agent Readiness |
| Cite Meru salon | JSON-LD (`BeautySalon` / FAQ / OfferCatalog) + citation copy | Origin SSR |
| Track mention/citation | **AEO Visibility** (early access) | Beauty / Meru Kenya prompts |
| See crawl vs referral | **AI Operator Activity** | Act on scrapers that crawl without referring |
| Block training scrapers | Bot Fight + AI crawler rules + **AI Labyrinth** | Free-capable Labyrinth |
| Abuse volume | WAF rules from abuse policy | Never challenge STK after Turnstile |
| Script supply chain | Client-Side Security | Log → Allow; align with origin CSP |
| Money authority | Django Turnstile + throttles + governors | Edge only reduces volume to Redis |

---

## Promote checklist (Agent Readiness / AEO)

1. Open **Overview → Agent Readiness**; run **Diagnostics**; note failing quick wins.
2. Confirm origin serves:
   - `https://sheeaesthetics.co.ke/sitemap.xml`
   - `https://sheeaesthetics.co.ke/llms.txt`
   - `https://sheeaesthetics.co.ke/robots.txt` with `Content-Signal: search=yes, ai-input=yes, ai-train=no`
3. Enable **[Markdown for Agents](https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/)** for marketing paths (`/`, `/services`, `/faq`, `/privacy`). Do not prioritize `/book/**` or `/staff/**`.
4. Prefer **origin robots** over CF managed robots when signals differ (see conflict rule above).
5. Request / enable **AEO Visibility** early access: track Mention / Citation Rate for prompts like “beauty salon Meru”, “facial waxing Meru”. Iterate FAQ/services copy from losing prompts.
6. Monitor **AI Operator Activity** (crawl vs referral). Challenge or Labyrinth scrapers that never refer traffic.
7. Re-run Agent Readiness Diagnostics after origin deploys and after enabling Markdown / Labyrinth.

---

## Defend checklist (bots + supply chain)

1. **Bot Fight Mode** + **AI crawler controls**: allow search/answer crawlers that cite; block known training-only scrapers that ignore Content Signals.
2. Enable **[AI Labyrinth](https://developers.cloudflare.com/bots/additional-configurations/ai-labyrinth/)** for unauthorized AI scrapers (honeypot without hurting SEO).
3. WAF rules from [WAF_CDN_ABUSE_POLICY.md](../security/WAF_CDN_ABUSE_POLICY.md):
   - Challenge volumetric `/images` scrapes and media resolver misses
   - Challenge staff-route probing
   - **Never challenge** guest STK / checkout POSTs after Turnstile success
   - Preserve M-Pesa webhook paths (Django allowlist / shared secret)
4. **Client-Side Security** (see Kenya edge runbook): script monitor → cookie inventory → content-security rules **Log** → **Allow**.
5. Align edge Turnstile with app `hold_bot_guard` — **no double-challenge** on guest STK.

### Never challenge STK

| Path family | Edge challenge? |
|-------------|-----------------|
| `POST /api/bookings/holds/` | Soft bot score OK; do not stack extra challenge after Turnstile |
| `POST /api/bookings/checkout/` | Same |
| `POST /api/bookings/checkout/mpesa/stk/` | **Never** challenge after Turnstile |
| M-Pesa provider webhooks | Never challenge; IP/secret at Django |
| `/staff/**` probing | Challenge / rate-limit |

---

## Out of scope (for now)

- Agent payment protocols (x402 / ACP / AP2) — M-Pesa guest STK remains the money path
- MCP / A2A agent cards / OAuth for agents
- Terraform auto-provisioning of the Cloudflare zone

---

## Sign-off (ops)

| Step | Done | Date / owner |
|------|------|--------------|
| Zone orange-cloud + Full strict SSL | | |
| Cache bypass bookings/customers/csrf/staff | | |
| Origin robots + sitemap + llms.txt live | | |
| Managed robots disabled if conflicting | | |
| Markdown for Agents on marketing paths | | |
| Bot Fight + AI crawler policy | | |
| AI Labyrinth enabled | | |
| Client-Side Security monitoring on | | |
| Agent Readiness Diagnostics re-scan green enough | | |
| STK paths verified unchallenged after Turnstile | | |
