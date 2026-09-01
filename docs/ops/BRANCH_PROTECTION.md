# Branch protection & required checks — AestheticOS

Secure Enterprise CI now emits a single branch-protection-friendly check:

**`promotion-gate`**

It succeeds only when every promotion-lane job succeeded:

`validate`, `lint-security`, `build-images`, `django-smoke`, domain units
(`bookings-unit`, `billing-unit`, `checkout-unit`, `tests-api-unit`,
`cass-calendar-service`), `frontend-test`, `payment-security`,
`checkout-billing-integration`, `receipt-pipeline`, `newman-acceptance`,
`frontend-e2e`, `docker-build`.

`build-images` builds the three CI images once per commit and pushes run-scoped
GHCR tags; downstream jobs pull instead of rebuilding (see
[`CI_WORKFLOW_DESIGN.md`](CI_WORKFLOW_DESIGN.md)).

Fortress-only jobs (`zap-passive-surface` / `platform-latency` / load / chaos /
`cass-certification` / `fortress-gate`) and `daraja-sandbox-contract` are
**not** required for everyday merges. The `ci-images-cleanup` job (run-scoped
tag GC) and the separate `ci-heal.yml` self-heal workflow are advisory and
**never** required checks. Prod promote requires a fresh **`fortress-gate`**
(see [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md)).

On green **schedule**, expected skip set = `{daraja-sandbox-contract}` only.

## GitHub settings (enabled 2026-08-04)

Repo is **public**, so classic branch protection is available. Live state:

### On `staging` and `main` (enabled)

1. **Require status checks to pass before merging** — required check: `promotion-gate` (`strict: true`, i.e. branch must be up to date)
2. **Require a pull request before merging**
3. **Require review from Code Owners** (enforces [`.github/CODEOWNERS`](../../.github/CODEOWNERS))
4. **`enforce_admins`: false** — owner emergency bypass while single-maintainer
5. **Force pushes / deletions** restricted; conversation resolution required

### On `development` (integration trunk, CI-gated with admin bypass)

1. **Require status checks to pass before merging** — required check: `promotion-gate` (`strict: false`, low-friction trunk)
2. **No** required PR/reviews — the maintainer may fast-forward/push directly
3. **`enforce_admins`: false** — admin bypass preserves direct pushes; bots and
   non-admin PRs (e.g. Dependabot) must pass `promotion-gate` before merge/auto-merge

For this to work, [`ci.yml`](../../.github/workflows/ci.yml) runs the promotion
lane on `pull_request` into `development` (not only `staging`/`main`), so PRs
into the trunk produce a `promotion-gate` result. Repo settings enable
**auto-merge** and **delete-branch-on-merge**, so a green Dependabot PR into
`development` merges itself and cleans up its branch.

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

## Branch hygiene (enterprise)

Long-lived refs only:

| Branch | Role |
|--------|------|
| `main` | Production |
| `staging` | Pre-prod |
| `development` | Integration trunk |

Do **not** keep long-lived `audit/*`, `wip/*`, or ungrouped Dependabot farms.

Dependabot ([`.github/dependabot.yml`](../../.github/dependabot.yml)):

- Weekly Monday 06:00 Africa/Nairobi, PRs target **`development`**
- npm split into **prod** vs **dev** groups (avoids one 13-package `npm ci` bomb)
- pip / Actions / Docker remain grouped minor+patch; **Python ≥3.14** and **Node ≥23** image majors ignored
- `insecure-external-code-execution: deny` on pip and npm
- Security updates stay on at repo level (Dependabot alerts + automated security fixes)
- Close stale dependency PRs within **14 days** (merge or close — do not let them rot)

Code scanning ([`.github/workflows/codeql.yml`](../../.github/workflows/codeql.yml)):

- CodeQL **security-extended** for Python, JavaScript/TypeScript, and GitHub Actions
- Own concurrency lane (`codeql-*`) — never part of `promotion-gate`
- Do not require the CodeQL checks until the first soak is green
- Secret scanning + push protection stay enabled on the public repo; private vulnerability reporting is on

Feature work: short-lived branches off `development`, merge via PR, delete the branch on merge.
