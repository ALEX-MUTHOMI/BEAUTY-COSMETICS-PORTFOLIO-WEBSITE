# AestheticOS — Sanitized Code Snippets

These excerpts are **safe for public portfolio use**. They illustrate engineering patterns without exposing secrets, webhook verification, or complete payment flows.

---

## 1. Bounded context separation

```python
# Principle: bookings/ never writes ledger truth directly.
# checkout/ owns payment orchestration; billing/ owns financial mutations.

# checkout/services.py (conceptual)
def handle_provider_callback(payload):
    with transaction.atomic():
        event = inbox.store_once(payload)  # idempotent inbox
        if event.already_processed:
            return
        session = normalize_and_validate(event)
        billing.credit_from_successful_session(session)
        bookings.confirm_from_checkout(session)
```

**Why it matters:** Prevents double-credit on duplicate M-Pesa callbacks and keeps audit trails in one place.

---

## 2. Database-level overlap protection

```sql
-- PostgreSQL exclusion constraint (conceptual)
-- Adjacent slots [10:00, 11:00) and [11:00, 12:00) are allowed.
-- Overlapping ranges for the same resource are rejected by the database.
ALTER TABLE bookings_booking
ADD CONSTRAINT no_overlap
EXCLUDE USING gist (
  resource_id WITH =,
  tstzrange(starts_at, ends_at, '[)') WITH &&
);
```

**Why it matters:** Race conditions under concurrent holds cannot double-book the same resource.

---

## 3. SSR frontend security perimeter

```typescript
// nuxt.config.ts (public-safe excerpt)
export default defineNuxtConfig({
  ssr: true,
  modules: ['@nuxtjs/turnstile', 'nuxt-csurf', 'nuxt-security'],
  security: {
    headers: {
      xFrameOptions: 'DENY',
      xContentTypeOptions: 'nosniff',
    },
  },
})
```

**Why it matters:** SEO-friendly public pages with CSRF, bot mitigation, and strict headers on the same app that hosts staff routes.

---

## 4. Response privacy by role

```python
# Conceptual serializer/view pattern
def staff_booking_payload(booking, *, actor):
    data = base_booking_fields(booking)
    if actor.can_reveal_contact(booking):
        data["contact"] = reveal_contact_audited(booking, actor)
    return redact_for_context(data, role=actor.role)
```

**Why it matters:** Customer PII is not returned by default; staff reveal is explicit and auditable.

---

## 5. CI security gate (structure only)

```yaml
# .github/workflows/ci.yml (simplified public view)
jobs:
  lint-security:
    steps: [black, ruff, bandit, secret-scan]
  django-smoke:
    steps: [docker-compose health, migrations]
  payment-security:
    steps: [checkout red-team, webhook replay tests]
  docker-build:
    steps: [production image build]
```

**Why it matters:** Security and payment regressions are caught before merge, not only in manual QA.

---

## What is intentionally omitted from public snippets

- Daraja credentials and callback verification
- Exact webhook HMAC / IP allowlist rules
- PII encryption keys and HMAC salts
- Full OTP and remember-device token implementation
- Staff session hardening details

Request a private walkthrough in interviews for depth on these areas.


## Booking Flow Snippet

```vue
<template>
  <button @click="startBooking" aria-label="Start booking process">Book Now</button>
</template>
```
