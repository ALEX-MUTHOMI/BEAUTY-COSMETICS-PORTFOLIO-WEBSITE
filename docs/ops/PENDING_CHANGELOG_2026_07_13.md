# Pending change log — Staff Auth Fortress + portal scale (pre-push)

Date: 2026-07-13
Branch: `development`

Diagnostic artifacts **not** committed: `_login_diag/`, `*_login_proof.png`,
`_agent_staff_login_result.json`, `frontend/_owner_login_probe.mjs`, accidental `NUL`.

## Commit plan (one logical change per commit)

1. **RBAC / fulfillment** — roles, migration, portal APIs, receipt permission split
2. **Staff OAuth backend** — Google/Apple provisioned-only, CSRF audit helpers, settings
3. **Login availability** — gunicorn sizing, Redis fail-closed 503, CORP for `/api/`, FE taxonomy
4. **Compose / env** — healthchecks, 127.0.0.1 desk alignment, OAuth env passthrough
5. **Staff portal FE UX** — Melis shell, login panel, bookings/dashboard polish
6. **Staff auth FE hardening** — CSRF refresh, host mismatch, middleware, specs
7. **Discoverability 2A** — remove public staff link, `robots.txt`
8. **Security tests** — fortress 1B/2A, OWASP, OAuth callbacks, RBAC, redis safety
9. **Ops / security docs** — provisioning, stall incident, hostile lane, policy tweaks
10. **CI / ZAP / Newman hostile** — scripts + Postman hostile collection

## OAuth note

Local `.env` has **no** Google/Apple client secrets. Live provider buttons stay off until
ops sets secrets (see `docs/ops/STAFF_OAUTH_LOCAL_SETUP.md`). Automated tests mock
token exchange and assert provision gates.
