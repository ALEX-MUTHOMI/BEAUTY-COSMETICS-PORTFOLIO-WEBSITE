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
| 3B-FU-001 | Medium | `/api/billing/mpesa-webhook/` | Permission-gated disabled route should have an explicit allowed-IP regression proving the view still returns 410 once IP allowlist passes. | Covered by `tests/security/test_authorization_control_closeout.py::test_disabled_legacy_billing_webhook_returns_410_after_ip_allowlist_accepts_request`. | closed in 3B-C |
| 3B-FU-002 | Medium | Staff booking scope | Staff views are globally scoped for authorized staff by current design. If per-beautician assignment becomes a product rule, add Staff A/Staff B object authorization before release. | Product policy documented in `docs/security/ABAC_POLICY_MATRIX.md`; covered by `test_staff_booking_access_policy_is_global_for_authorized_staff_and_denies_without_permission`. Future per-staff scoping remains a product-change backlog item. | closed as policy decision / future product backlog |
| 3B-FU-003 | Medium | Newman negative coverage | Pytest now covers role/header/mass-assignment cases. Add selected negative Newman cases to catch deployment routing/cookie regressions. | Phase 3C/3D API contract expansion. | deferred |
| 3B-FU-004 | Medium | Response field allowlists | Phase 3B asserts absence of sensitive markers. A formal response allowlist for each public/customer/staff route would tighten future refactors. | Phase 3C response privacy/allowlist. | deferred |
| 3B-FU-005 | Low | Booking test runtime | Prior `bookings/tests` run timed out under local command budget. | Re-run with durations and maxfail diagnostics; full partition passed in Phase 3B-F. | closed in 3B-F |
| 3B-FU-006 | Low | Turbo wrapper Docker config | Windows shell could not read `C:\Users\PC\.docker\config.json`, causing wrapper/Docker Newman failure before the gate ran. | Add repo-local empty Docker config fallback when `DOCKER_CONFIG` is unset, plus Docker daemon diagnostic. | closed in 3B-F |

## Patch Discipline

- Do not patch speculative issues without a failing security test.
- Any future patch must keep checkout/billing financial truth separated.
- Any future staff scoping change must be explicit product behavior, not an
  accidental test-only assumption.
- No route that accepts object IDs, tokens, owner-like fields, role-like fields,
  status-like fields, or payment-like fields may be added without updating the
  authorization matrix and negative tests.
- Docker tooling patches must fail closed when the Docker daemon is inaccessible;
  they may avoid local credential-config ACL issues but must not skip Newman,
  Compose, health, or security gates.
