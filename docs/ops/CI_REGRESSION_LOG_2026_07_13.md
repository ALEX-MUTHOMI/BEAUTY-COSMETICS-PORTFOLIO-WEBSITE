# CI regression log — Staff Auth Fortress push train (2026-07-13)

Senior engineer read of Secure Enterprise CI on `development`, keyed to
commits that landed after the staff portal / OAuth hardening batch.

Last green baseline before this train: `a031d80` (staff audit migration + Melis login).

## Run timeline (newest first)

| SHA | Commit intent | Run | Gate that failed | Fingerprint |
|-----|---------------|-----|------------------|-------------|
| `ba59836` | Move Windows `.venv` mask out of CI compose | [29278739517](https://github.com/ALEX-MUTHOMI/aesthetic-os/actions/runs/29278739517) | **bookings-unit** | `test_production_cookie_settings_are_secure` still assumed `DEBUG=False` ⇒ Secure cookies; settings now key Secure flags off `SECURE_SSL_REDIRECT` (CI=False) |
| `e1008f9` | turbo_pass stderr / Bandit / secret-hygiene harden | [29278112805](https://github.com/ALEX-MUTHOMI/aesthetic-os/actions/runs/29278112805) | **django-smoke** | Poetry: empty `linux_venv_mask` at `/app/.venv` → recreate → `Permission denied` |
| `055151c` | Compose Windows `.venv` mask (in main compose) | [29259957276](https://github.com/ALEX-MUTHOMI/aesthetic-os/actions/runs/29259957276) | **lint-security** | Bandit Medium×2 — `urlopen` in `bookings/services/staff_oauth.py:79` (B310) |
| `965e54c` | Ops docs + hostile Newman/ZAP tooling | [29257979549](https://github.com/ALEX-MUTHOMI/aesthetic-os/actions/runs/29257979549) | **lint-security** | Same Bandit B310 on staff OAuth `urlopen` |
| `a031d80` | Prior green | success (~24m) | — | Full matrix green |

Downstream matrix jobs (api/unit/newman/…) were **skipped** whenever an early
required job failed — cascade, not independent regressions.

## What each failure means

### 1) Bandit B310 on staff OAuth (`965e54c`, `055151c`)

- **Cause:** New provisioned-only Google/Apple token exchange uses stdlib
  `urllib.request.urlopen` against settings-bound HTTPS IdP URLs.
- **Why CI caught it:** `lint-security` runs Bandit `-ll -ii` on the host Poetry
  env (no Docker `.venv` noise). Medium+ findings fail the job.
- **Fix landed in `e1008f9`:** `# nosec B310` (+ ruff `noqa: S310`) on the
  intentional transport call; lint-security went **green** on that SHA.
- **Residual risk:** Acceptable — URL comes from settings, not request input;
  failures are fail-closed via `StaffOAuthError`.

### 2) Poetry Permission denied on `/app/.venv` (`e1008f9`)

- **Cause:** Windows-local workaround `linux_venv_mask:/app/.venv` was in
  canonical `docker-compose.yml`. CI mounts an empty named volume; Poetry tries
  to recreate a broken in-project `.venv` → EACCES.
- **Fix in `ba59836`:** Mask moved to `docker-compose.windows.yml` (local opt-in).

### 3) Cookie Secure contract vs CI HTTP (`ba59836`)

- **Cause:** Staff desk hardening keys `SESSION_COOKIE_SECURE` /
  `CSRF_COOKIE_SECURE` off `SECURE_SSL_REDIRECT` so local/CI HTTP desks work.
  `test_cookie_notice_contract.test_production_cookie_settings_are_secure` still
  only flipped `DEBUG=False` and expected Secure=True.
- **Evidence on `ba59836`:** validate, lint-security, django-smoke, frontend,
  billing/checkout/api/cass all green; bookings-unit 358 passed / 1 failed.
- **Fix:** Override Secure + SSL redirect True in that production contract test
  (aligned with `test_staff_session_cookie_posture`).

## Passed gates unlocked by compose fix (`ba59836`)

- `validate`, `lint-security`, `django-smoke`, `frontend-test`, `billing-unit`,
  `checkout-unit`, `tests-api-unit`, `cass-calendar-service` — all green
- Remaining blocker was bookings cookie contract (above)

## Remediation

1. `ba59836` — Move Windows `.venv` mask out of CI compose.
2. Follow-up commit — align cookie notice Secure-flag contract with SSL-redirect posture.
3. Watch full Secure Enterprise CI to green.

## Operator notes

- Do **not** set `COMPOSE_FILE=...windows.yml` in GitHub Actions secrets/env.
- Local Windows: after enabling the windows compose file, recreate web/worker
  and once-run `docker compose exec -u root web poetry install --with dev --no-root`
  if Poetry still complains about an empty mask volume.

## Watch outcome (3f4b1a)

See Actions: https://github.com/ALEX-MUTHOMI/aesthetic-os/actions/runs/29279581517


### 4) Docker Hub registry flake (`b3f4b1a` run 29279581517)

- **Not a product regression.** Multiple parallel jobs failed at
  `docker compose up -d --build` with Docker Hub `500 Internal Server Error`
  fetching `python:3.13-slim` / `node:22-alpine` metadata, plus transient
  `pull access denied for aesthetic_os_web_app` when build aborted mid-bake.
- django-smoke / lint-security / validate / checkout-unit still green on that SHA.
- Action: `gh run rerun --failed 29279581517` (infra retry).

## Desk reality local matrix (2026-07-14)

Evidence index: `reports/ci/desk-phase3-matrix.txt` + `docs/ops/DESK_ACCEPTANCE_CHECKLIST.md`.

| Gate | Result | Artifact |
|------|--------|----------|
| Password login @ `127.0.0.1:3000` | PASS | `reports/ci/desk-phase1a-password-login.txt` |
| Google live | FAIL-CLOSED (`.env` `replace-with-*` placeholders) | `reports/ci/desk-phase1b-google-oauth.txt` |
| `preflight_heal.ps1` | PASS | `reports/ci/preflight-heal-summary.md` |
| turbo_pass | PASS (~1056s) | `reports/ci/turbo-pass-summary.md` |
| Vitest staff | PASS 15/15 | `reports/ci/desk-phase3-vitest-staff.txt` |
| Hostile Newman | PASS | `tests/postman/reports/newman-hostile-red-team.json` |
| ZAP all-passive | PASS (`FAIL-NEW=0`; WARN Non-Storable triage) | `reports/security/zap/**` |
| Actions (last pushed SHA) | success | [29280232120](https://github.com/ALEX-MUTHOMI/aesthetic-os/actions/runs/29280232120) on `b602045` |

**Note:** Desk-reality code changes are local until pushed; do not claim Actions green for unpushed commits.
