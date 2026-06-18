# Phase 3B Patch Backlog

Production readiness: **rejected / not claimed**.

Phase 3B is discovery-first. No confirmed critical/high BOLA, IDOR, mass
assignment, role tampering, payment tampering, or query widening defect was
confirmed by the added Phase 3B tests.

## Confirmed Findings

| ID | Severity | Affected route | Affected object | Risk | Root cause | Recommended patch | Tests required | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | no confirmed defect |

## Coverage / Follow-Up Backlog

| ID | Severity | Area | Risk | Recommended follow-up | Status |
| --- | --- | --- | --- | --- | --- |
| 3B-FU-001 | Medium | `/api/billing/mpesa-webhook/` | Permission-gated disabled route should have an explicit allowed-IP regression proving the view still returns 410 once IP allowlist passes. | Add bounded fake-IP test without real provider calls. | deferred |
| 3B-FU-002 | Medium | Staff booking scope | Staff views are globally scoped for authorized staff by current design. If per-beautician assignment becomes a product rule, add Staff A/Staff B object authorization before release. | Product/security decision required before implementation. | deferred |
| 3B-FU-003 | Medium | Newman negative coverage | Pytest now covers role/header/mass-assignment cases. Add selected negative Newman cases to catch deployment routing/cookie regressions. | Phase 3C/3D API contract expansion. | deferred |
| 3B-FU-004 | Medium | Response field allowlists | Phase 3B asserts absence of sensitive markers. A formal response allowlist for each public/customer/staff route would tighten future refactors. | Phase 3C response privacy/allowlist. | deferred |

## Patch Discipline

- Do not patch speculative issues without a failing security test.
- Any future patch must keep checkout/billing financial truth separated.
- Any future staff scoping change must be explicit product behavior, not an
  accidental test-only assumption.
