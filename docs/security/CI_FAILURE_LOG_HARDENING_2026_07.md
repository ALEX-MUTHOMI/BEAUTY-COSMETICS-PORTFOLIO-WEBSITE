# CI Failure Log — Hardening Pass Recurrence (2026-07-10)

## Latest failure
- **Run:** https://github.com/ALEX-MUTHOMI/aesthetic-os/actions/runs/29045952897
- **Commit:** `ab666da` — Harden guest STK, webhook secret, Beat expiry, and staff auth fail-closed
- **Failed job:** `lint-security` (cascade-skipped all later tiers)
- **Root cause:** `black --check` — `core/settings.py` would be reformatted
- **Pattern:** Same class as `e21867d` (black on `sentry_scrubber.py`) — format gate before security suite

## Recurring CI failure chain (money-path hardening week)

| Run | Commit | Failed job | Root cause | Fix class |
|-----|--------|------------|------------|-----------|
| 29036928175 | e21867d | lint-security / payment-security cascade | black on scrubber; then FE build | format + remove `@sentry/vue` import |
| 29037263803 | b07eb48 | payment-security | CSRF referer missing on privacy POST; secret-scan hit scrubber regex | referer + split token marker |
| 29038041930 | 5a55f9f | latency | status poll 429 after throttle 30→20 | override_settings only in latency probes |
| 29040039346 | 5c5871b | — | success (only Daraja skipped) | — |
| **29045952897** | **ab666da** | **lint-security** | **black on `core/settings.py`** | **black format + preflight lint** |

## Production-grade prevention
1. Always run `black` / `isort` / `ruff` on touched Python before push.
2. Keep secret-hygiene exclusions for intentional scrubber patterns.
3. Never widen CORS/`IsAuthenticated` removal for guest STK — keep bind+HMAC.
4. Document fail-closed controls in `HACKER_MINDSET_SECURE_EXECUTION_MATRIX.md`.
5. Update Newman/pytest contracts when `/api/health-check/` payload shape changes.
6. Prefer `check --deploy` for weak-secret / live-webhook gates before cutover.

## Follow-up fixes applied (2026-07-10)
- black-format `core/settings.py`
- deep health contract updates (pytest + Newman)
- `core/checks.py` deploy gates (SECRET_KEY / PII / Turnstile / webhook secret)
- durable `PrivacyRightsRequest` + peppered HMAC hashes
- console `PiiMessageRedactionFilter`
- staff OAuth unconfigured → 404 (not 503)
- Beat schedule includes `sweep_booking_reminders`

## Follow-on CI failure (9589cc3 / run 29115481643)
- **Job:** lint-security → Dependency vulnerability audit (pip-audit)
- **Root cause:** Django 6.0.6 — PYSEC-2026-2090/2091/2092; fix versions include **6.0.7**
- **Fix:** bump `django (>=6.0.7,<7.0.0)` + refresh lock

## Follow-on CI failure (0b6cf49 / Django bump)
- **Job:** lint-security → `scripts/ci/secret_hygiene.py` (NOT black)
- **Root cause:** `tests/security/test_deploy_security_checks.py` used `SECRET_KEY="..."` literals; scanner treats that as committed credentials
- **Fix:** assemble fixture values at runtime + `override_settings(**{...})` so lines never match `SECRET_KEY=` / `*_SECRET_KEY=` patterns
- **Production impact:** CI fail-closed only — runtime servers do not run this scanner; weak real secrets are caught by `check --deploy` / `core/checks.py` at cutover
