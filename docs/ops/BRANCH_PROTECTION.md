# Branch protection & required checks — AestheticOS

Secure Enterprise CI now emits a single branch-protection-friendly check:

**`promotion-gate`**

It succeeds only when every promotion-lane job succeeded:

`validate`, `lint-security`, `django-smoke`, domain units (`bookings-unit`,
`billing-unit`, `checkout-unit`, `tests-api-unit`, `cass-calendar-service`),
`frontend-test`, `payment-security`, `checkout-billing-integration`,
`receipt-pipeline`, `newman-acceptance`, `frontend-e2e`, `docker-build`.

Fortress-only jobs (`zap-passive-newman`, load, latency, chaos,
`cass-certification`) and `daraja-sandbox-contract` are **not** required for
everyday merges.

## GitHub settings (enabled 2026-08-04)

Repo is **public**, so classic branch protection is available. Live state:

### On `staging` and `main` (enabled)

1. **Require status checks to pass before merging** — required check: `promotion-gate`
2. **Require a pull request before merging**
3. **Require review from Code Owners** (enforces [`.github/CODEOWNERS`](../../.github/CODEOWNERS))
4. **`enforce_admins`: false** — owner emergency bypass while single-maintainer
5. **Force pushes / deletions** restricted; conversation resolution required

Re-apply / verify:

```powershell
gh api repos/ALEX-MUTHOMI/aesthetic-os/branches/staging/protection --jq .required_status_checks.contexts
gh api repos/ALEX-MUTHOMI/aesthetic-os/branches/main/protection --jq .required_status_checks.contexts
```

Expect `["promotion-gate"]`.

### Environments (enabled 2026-08-04)

| Environment | Purpose | Protection |
|-------------|---------|------------|
| `staging` | [`deploy-staging.yml`](../../.github/workflows/deploy-staging.yml) | Required reviewer `@ALEX-MUTHOMI` (self-review allowed); set var `STAGING_BASE_URL` |
| `daraja-sandbox` | Opt-in real Daraja contract | Required reviewer `@ALEX-MUTHOMI` (self-review allowed); Daraja secrets |

## Concurrency lanes

| Group | When | Behavior |
|-------|------|----------|
| `ci-promo-<ref>` | push / PR / non-fortress dispatch | Cancels superseded promo runs |
| `ci-fortress-<ref>` | schedule or `run_full_fortress=true` | Isolated from promo cancels |

## Residual risk (single maintainer)

**Live (2026-08-04):** Repo is **public**; classic branch protection is
**enabled** on `staging` and `main` with required check `promotion-gate` and
**Require review from Code Owners**. `enforce_admins` is **false** so the
owner can still emergency-bypass while alone.

GitHub will not let a PR author satisfy their own required Code Owner review.
Until a second collaborator exists, merges that touch CODEOWNERS paths need an
admin bypass or a second GitHub account. Non-CODEOWNERS paths still require one
approving review + green `promotion-gate`.
