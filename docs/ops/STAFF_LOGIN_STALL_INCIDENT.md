# Staff login stall / multi-hour desk outage

**Status:** Remediated in-repo (availability + opaque-error fixes). Residual risks remain.
**Date:** 2026-07-13
**Scope:** Staff portal password login (`/staff/login` → `/api/csrf/` → `/api/staff/auth/login/`)

## Symptoms

1. UI stuck on **Signing in…** then ~15s later **Could not reach the desk** (`LOGIN_FETCH_TIMEOUT_MS` abort in `frontend/src/staff/staffAuth.ts`).
2. Direct `curl`/`fetch` to the API sometimes succeeded while the form path hung (worker queue / prior unhealthy window).
3. Desk appeared broken **for hours** when `aesthetic_os_web_app` stayed unhealthy or Redis auth/connectivity failed — not a one-shot UX timeout.
4. Local browser quirks: Cursor IDE browser often fails `localhost:8000` but works with `127.0.0.1:8000`; mixing `localhost` portal + `127.0.0.1` API breaks CSRF cookies (`SameSite=Strict`).

## Blast radius

- Staff cannot authenticate (password path). OAuth start may also fail if CSRF/session/admission is down.
- Guest money paths that share Redis throttle + gunicorn workers can degrade in the same window.
- Ops false negatives: opaque “desk unreachable” masked CSRF/403 and Redis 503 alike.

## Root causes (ranked)

1. **Gunicorn worker exhaustion / OOM death spiral**
   Multiple sync workers under a **1G** compose memory limit → worker SIGKILL / restart loops → accept queue backs up → browser abort at 15s while the process looks “up”. Compose historically used 3 workers; local default is now **1** with env-tunable sizing, shorter `--timeout`, and `--max-requests` recycling.

2. **Redis auth / connectivity → fail-closed admission**
   Throttle store is correctly **fail-closed**. `NOAUTH`, connection refused, or password mismatch on `REDIS_URL` vs `redis --requirepass` yields **503** on CSRF bootstrap and staff login admission. Celery logs showed Redis reconnect storms during redis recreate windows. Healthcheck already authenticates (`redis-cli -a … ping`); mismatch still causes global auth denial (availability DoS surface).

3. **Opaque FE status mapping**
   - **403** (CSRF/session) was mapped to “Could not reach the desk” — same copy as network failure — masking cookie/host issues.
   - **503** was conflated with **429** (“Please try again later”) — availability looked like rate limit.
   Fixed: distinct copy + retryable flag; Retry control re-bootstraps CSRF.

4. **Host mismatch (`localhost` vs `127.0.0.1`) + `CSRF_COOKIE_SAMESITE=Strict`**
   Cross-site credentialed POSTs do not send Strict cookies. Portal on `localhost:3000` + API on `127.0.0.1:8000` → CSRF **403** without a clear ops signal. Not a CSRF bypass; align hosts (prefer `127.0.0.1` for both locally) or same-origin edge in prod.

5. **Single sync worker head-of-line blocking** (secondary once OOM is fixed)
   One long request blocks login until FE abort. Mitigated by lower gunicorn timeout and max-requests; still prefer enough workers only when memory allows.

## Timeline hypotheses

- Redis restart / compose recreate → brief `Connection refused` → throttle 503 on `/api/csrf/` → empty CSRF → login never starts or aborts.
- Memory pressure → worker death → host CSRF curl hangs (`csrf:000`) → multi-hour “desk down”.
- Operator opens `localhost:3000` against `127.0.0.1:8000` API → persistent 403 until host alignment.

## Attacker perspective

| Signal | What a hostile party learns | Abuse path |
| --- | --- | --- |
| Timeouts / hung workers | Desk is capacity-bound | Parallel login/CSRF storms to exhaust gunicorn (DoS), not credential oracle |
| 503 + `Retry-After` | Admission/Redis unavailable | Confirms availability outage; still no user enumeration |
| Opaque 403→“desk down” (pre-fix) | Confused CSRF with outage | Low value; fixed |
| Redis unauthenticated | Global fail-closed auth | Availability DoS if Redis exposed without AUTH — keep Redis private + password matched |
| Timeout as oracle | Weak timing only if login crypto differs — password path already constant-ish messaging on 400 | Prefer fixed client timeout; do not return distinct bodies for unknown vs known emails |

Brute-force remains bounded by route throttle + staff login cooldown (fail-closed on Redis for admission).

## Detection signals

- Gunicorn: `WORKER TIMEOUT`, `Booting worker`, unexpected restarts; container OOMKilled.
- App logs: `Redis throttle unavailable … redis_error_class=…`; `failure_behavior=fail_closed_503`.
- Redis: `NOAUTH`, connection refused from web/worker.
- Metrics/logs: elevated `/api/csrf/` and `/api/staff/auth/login/` 503/429 latency; `X-Request-ID` correlation.
- FE: surge of retryable desk messages without 400 invalid-credentials.

## Remediation done

- Compose gunicorn: env-configurable workers (default 1), `--timeout 60`, `--graceful-timeout`, `--max-requests` (+ jitter); memory guidance in comments.
- Route throttle 503 includes **`Retry-After: 5`**; redis error class logged on fail-closed.
- FE: separate messages for 403 / 503 / 429 / network; Retry re-fetches CSRF with `forceRefresh`; host-mismatch warning.
- CSRF bootstrap: timeout + force refresh for staff login (never trust Nuxt-origin cookie).
- Docs/compose: align local desk on `127.0.0.1` with API.

## Security review checklist

- [x] Enumeration: login failures stay generic on 400; welcome-back personalization is local display-name storage / email local-part only — not a server oracle for account existence.
- [x] Resource exhaustion: throttle fail-closed; workers capped for local memory; Retry-After on 503.
- [x] Redis unauthenticated → availability DoS on auth: fail-closed retained (no fail-open in prod).
- [x] CORP/CORS: API CORP `cross-origin` for `/api/` so SPA can read responses; cookies still SameSite=Strict — host alignment required.
- [x] Timeout as oracle: client 15s abort → same unreachable copy; not mapped to invalid credentials.
- [x] CSRF / session / httponly session cookie unchanged (not disabled).

## Residual risk

- Single worker can still HOL-block under load until scaled with RAM.
- Celery worker may stay unhealthy across Redis flaps without separate ops restart.
- True cross-site SPA on HTTP cannot use `SameSite=None` without Secure — production should terminate TLS and prefer **same-origin** API proxy.
- Staff login Redis cooldown path maps store outage to 429 (fail-closed) after admission already passed — rare; still not invalid credentials.

## Follow-up (Auth Fortress 1B + 2A)

- Web compose **healthcheck** probes `GET /api/csrf/` so login-stall death spirals mark `web` unhealthy.
- Frontend waits on `web` **healthy** before starting.
- Public footer staff link removed; `frontend/public/robots.txt` disallows `/staff`.
- Google remains provisioned-only; ops matrix lives in `docs/ops/STAFF_PORTAL_PROVISIONING.md`.
- Regression suite: `tests/security/test_staff_auth_fortress_1b_2a.py`.

### Security variables (ops assert)

| Variable | Assert |
| --- | --- |
| `SECURE_SSL_REDIRECT` | Local false / prod true |
| Redis AUTH | Healthcheck `redis-cli -a … ping`; URL password matches |
| `GUNICORN_WORKERS` | Local 1 under 1G |
| OAuth env | Empty → providers false; all set → google true; no auto-provision |
| `NUXT_PUBLIC_STAFF_GOOGLE_ENABLED` | true only when providers.google |
| Desk host | Same host as API for Strict CSRF |
| CORS / CSRF trusted origins | Include desk origin |
