# CI regression log — Staff Auth Fortress push train (2026-07-13)

Senior engineer read of Secure Enterprise CI on `development`, keyed to
commits that landed after the staff portal / OAuth hardening batch.

Last green baseline before this train: `a031d80` (staff audit migration + Melis login).

## Run timeline (newest first)

| SHA | Commit intent | Run | Gate that failed | Fingerprint |
|-----|---------------|-----|------------------|-------------|
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

- **Cause:** Windows-local workaround `linux_venv_mask:/app/.venv` was added to
  **canonical** `docker-compose.yml`. CI Linux runners mount an empty named
  volume there. Poetry (`POETRY_VIRTUALENVS_CREATE=false` image) still sees a
  broken in-project `.venv` and tries to recreate it → EACCES.
- **Why local turbo_pass passed:** Local volume was chmod’d + `poetry install`’d
  into the mask — CI starts cold every job.
- **Corrective design:** Keep the mask **out** of CI compose. Move to
  `docker-compose.windows.yml` and opt-in via local `COMPOSE_FILE` only.

## Passed gates on latest failed SHA (`e1008f9`)

- `validate` — Poetry lock/files OK
- `lint-security` — black/isort/ruff/bandit/secret hygiene OK (post-nosec)

## Remediation commit intent (this follow-up)

1. Strip `linux_venv_mask` from `docker-compose.yml`.
2. Ship `docker-compose.windows.yml` for Windows bind-mount hosts only.
3. Re-push `development` and watch full Secure Enterprise CI to green.

## Operator notes

- Do **not** set `COMPOSE_FILE=...windows.yml` in GitHub Actions secrets/env.
- Local Windows: after enabling the windows compose file, recreate web/worker
  and once-run `docker compose exec -u root web poetry install --with dev --no-root`
  if Poetry still complains about an empty mask volume.
