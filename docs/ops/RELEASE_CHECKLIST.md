# Release checklist — AestheticOS (production-grade)

Green **promotion-gate** certifies the engineering tree. Production cutover
requires the gates below. Do not claim production readiness from CI alone
([`PRODUCTION_RUNTIME_FAILURE_POLICY.md`](../security/PRODUCTION_RUNTIME_FAILURE_POLICY.md)).

## 1. Engineering (automated)

- [ ] `promotion-gate` green on the release SHA
- [ ] Image published to GHCR (`reports/ci/image-digest.txt` / `docker-build` artifact)
- [ ] No open Dependabot runtime majors (#4 python, #5 node, #8 Nuxt) in the train

## 2. Fortress freshness (automated + human)

- [ ] Successful Secure Enterprise **fortress** run (`schedule` or
      `workflow_dispatch` + `run_full_fortress=true`) within **7 days**
- [ ] Local/CI: `bash scripts/ci/check_fortress_freshness.sh ALEX-MUTHOMI/aesthetic-os`
- [ ] Deploy Staging workflow runs the same gate unless emergency override

```powershell
gh workflow run "Secure Enterprise CI Pipeline" --ref development -f run_full_fortress=true
gh run watch --exit-status
```

## 3. Staging promote (CD)

- [ ] GitHub Environment `staging` configured with required reviewers
- [ ] Repository variable `STAGING_BASE_URL` set
- [ ] Optional: `STAGING_DEPLOY_HOOK_URL` secret for host pull/restart
- [ ] Run **Deploy Staging** with the release SHA / image tag
- [ ] Staging smoke green: `/api/health-check/`, `/book`, `/services`, `/`

```powershell
gh workflow run "Deploy Staging" --ref development
```

## 4. Money-path soak (staging)

- [ ] Daraja sandbox STK + webhook (Environment `daraja-sandbox`,
      `run_daraja_sandbox=true`)
- [ ] Celery Beat running; booking expiry + reminder workers healthy
- [ ] Receipt email to a real inbox (or approved fake→sink with audited trail)
- [ ] Staff desk: login, booking list, reauth → contact reveal, password reset
- [ ] Deep `/api/health-check/` shows DB + Redis healthy under TLS
      (`SECURE_SSL_REDIRECT=True` on staging)

## 5. Runtime / cutover

- [ ] Live `SENTRY_DSN` + `NUXT_PUBLIC_SENTRY_DSN` with scrubbers
- [ ] Redis / Celery / Gunicorn alerts
- [ ] Backup + restore drill evidence (timestamped)
- [ ] Cloudflare Kenya edge checklist
      ([`CLOUDFLARE_KENYA_EDGE.md`](CLOUDFLARE_KENYA_EDGE.md))
- [ ] Incident runbook owner named; rollback image digest recorded
- [ ] Open `staging` → `main` PR only after soak; require `promotion-gate`

## 6. Post-release

- [ ] Watch Sentry + payment failure rate for 24h
- [ ] Confirm fortress schedule remains enabled (weeknights 02:00 UTC)

## Daraja environment approvals

| Item | Value |
|------|-------|
| Environment name | `daraja-sandbox` |
| Workflow job | `daraja-sandbox-contract` in Secure Enterprise CI |
| Trigger | `workflow_dispatch` + `run_daraja_sandbox=true` |
| Secrets | `DARAJA_CONSUMER_KEY`, `DARAJA_CONSUMER_SECRET`, `DARAJA_SHORTCODE`, `DARAJA_PASSKEY`, `DARAJA_CALLBACK_URL`, `DARAJA_ACCOUNT_REFERENCE`, `DARAJA_TRANSACTION_DESC`, `DARAJA_TEST_MSISDN` |
| Policy | Required reviewers; never enable on push/PR |

```powershell
gh workflow run "Secure Enterprise CI Pipeline" --ref development `
  -f run_full_fortress=true `
  -f run_daraja_sandbox=true
```
