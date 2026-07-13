# Production Runtime Failure Policy

Phase 3D-PLUS defines local code behavior and verification boundaries. It does
not certify production readiness.

**Honest status:** green CI on `development` means the *code path* is certified
for that tree. Production readiness is a separate bar (four gates):

1. **Engineering** — local CI mirror / pre-commit so lint never burns Actions
   (`scripts/ci/install_git_hooks.ps1`, `scripts/ci/local_ci_mirror.ps1`).
2. **Money-path** — staging Daraja STK + webhook, Beat running, receipt email
   to a real inbox, deep `/api/health-check/`.
3. **Staff / ops** — provisioned staff login, live bookings, reauth → contact
   reveal, password reset, synthetic desk path. Local HTTP desks require
   `SECURE_SSL_REDIRECT=False` (see `docs/ops/STAFF_PORTAL_PROVISIONING.md`);
   staging/prod keep `True` so Secure session/CSRF cookies work on TLS only.
4. **Runtime / cutover** — live Sentry (FE+BE) with existing PII scrubbers,
   alerts, deploy config gates, backups + restore drill, WAF/CDN, incident
   runbook practice.

Sentry SDK + scrubbers already exist (`core/sentry_init.py`,
`core/sentry_scrubber.py`, FE scaffold). A live `SENTRY_DSN` /
`NUXT_PUBLIC_SENTRY_DSN` is still required before claiming observability.

Before production approval, staging must establish Redis latency/error alerts,
connection-pool limits, Celery worker/queue alerts, WAF/CDN ownership, incident
runbooks, provider/email failure drills, backup/recovery evidence, and measured
booking/payment concurrency capacity. Any rate adjustment requires redacted
telemetry and an explicit decision; tests must never drive production rates up.
