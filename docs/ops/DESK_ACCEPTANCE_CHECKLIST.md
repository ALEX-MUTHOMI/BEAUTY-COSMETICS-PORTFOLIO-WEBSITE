# Staff desk acceptance checklist

Do **not** call the staff desk “working” without evidence for each row that applies.
Every green claim needs a command exit code and a report path under `reports/` or an Actions URL.

Host rule (G1): browser, `NUXT_PUBLIC_API_BASE_URL`, and `STAFF_PORTAL_PUBLIC_ORIGIN` all use **`127.0.0.1`** locally — never mix with `localhost`.

| Gate | Pass criteria | Evidence |
|------|---------------|----------|
| P0 Topology | `web` / `frontend` / `redis` / `db` / `worker` healthy; `GET /api/csrf/` → 200 + `Set-Cookie` | `reports/ci/desk-phase0-topology.txt` |
| P1a Password | Provisioned owner signs in at `http://127.0.0.1:3000/staff/login` → `/staff/dashboard` under 30s cold | `reports/ci/desk-phase1a-password-login.txt` |
| P1b Google | Live: GCP redirect URI exact match + `providers.google=true` + real client id + desk land. Else: fail-closed (`providers.google=false`, start 404) + setup doc | `reports/ci/desk-phase1b-google-oauth.txt` |
| P2 Preflight heal | `.\scripts\ci\preflight_heal.ps1` exit 0 | `reports/ci/preflight-heal-summary.md` |
| P3 Turbo Pass | `.\scripts\ci\turbo_pass.ps1` exit 0 | turbo_pass summary under `reports/ci/` |
| P3 Staff security pytest | fortress / OWASP portal / OAuth / cookie posture green | pytest output or CI job log |
| P3 Vitest staff | `staffAuth` / `staffPortal` (compose `frontend-test` profile) green | Vitest summary or CI `frontend-test` |
| P3 Newman | `.\scripts\ci\run_newman_docker.ps1` exit 0 | Newman report under `reports/` |
| P3 Hostile (optional same day) | `.\scripts\ci\run_newman_hostile_docker.ps1` | hostile report + `docs/security/HOSTILE_RED_TEAM_LANE.md` |
| P3 ZAP passive | `.\scripts\ci\run_security_passive_gate.ps1 -Mode all-passive` (staff authenticated if creds available) | ZAP report under `reports/` |
| P3 GitHub Actions | Secure Enterprise CI success for the commit under test | Actions run URL + `docs/ops/CI_REGRESSION_LOG_*.md` |

## What we will not claim

- Green Vitest alone ≠ production ready.
- Green CI lint alone ≠ staff can log in.
- Mock OAuth ≠ live Google.
- Placeholder `replace-with-*` OAuth env ≠ configured IdP.
- ZAP warnings are triage items; critical auth/BOLA failures block release.

## Google redirect URI (G2)

Local canonical (must match GCP Authorized redirect URIs byte-for-byte):

`http://127.0.0.1:8000/api/staff/auth/google/callback/`

See `docs/ops/STAFF_OAUTH_LOCAL_SETUP.md` and `docs/ops/STAFF_PORTAL_PROVISIONING.md`.
