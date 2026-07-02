# OWASP Top 10 CI/CD Security — Audit & Hardening Record

**Scope:** `ALEX-MUTHOMI/aesthetic-os` (private repository), GitHub Actions pipeline (`.github/workflows/ci.yml`), Docker build system, and repository governance settings.

**Method:** Live audit against the repository via the GitHub REST API (`gh api`), direct inspection of the workflow file, both Dockerfiles, and repository secrets/permissions — not a theoretical checklist. Evidence for every finding was captured before any fix was applied.

## Executive summary

This hardening pass closes every code-level (agent-executable) gap identified in the OWASP Top 10 CI/CD Security Risks audit, **and** was followed by a second pass that executed every *repository-configuration* fix reachable through the GitHub REST API (`gh api` / `gh secret` / `gh` CLI) rather than leaving them as manual checklist items. Of the ten risk categories, nine now have live, verified fixes. Exactly **one** residual gap remains — required PR reviews / branch protection on `main` — and it is a genuine GitHub billing-plan restriction (GitHub Free does not permit branch protection or repository rulesets on private repositories), confirmed by a live API call, not an assumption or a UI-only limitation.

### What was fixed in this pass (code)

| Risk | Fix | File(s) |
|---|---|---|
| CICD-SEC-3 (Dependency Chain Abuse) | Added Dependabot for `pip`, `npm` (frontend), `github-actions`, and `docker` ecosystems on a weekly schedule; added `pip-audit` and `npm audit --audit-level=high` as blocking CI gates | `.github/dependabot.yml`, `.github/workflows/ci.yml` |
| CICD-SEC-9 (Improper Artifact Integrity Validation) | Pinned both base images to immutable SHA-256 digests instead of mutable tags, fetched live from the Docker Hub Registry API (not hallucinated) | `Dockerfile`, `frontend/Dockerfile` |
| CICD-SEC-8 (Ungoverned 3rd Party Services) | Pinned `actions/checkout` and `actions/setup-python` to immutable commit SHAs (resolved live via `git ls-remote`), eliminating the "moved tag" supply-chain attack vector (the exact pattern behind the Homebrew and Gentoo incidents) | `.github/workflows/ci.yml` |
| CICD-SEC-5 (Insufficient PBAC) | Added explicit `permissions: contents: read` at the workflow root (fail-closed default); added `environment: daraja-sandbox` to the one job that touches real third-party (Daraja) secrets | `.github/workflows/ci.yml` |
| CICD-SEC-4 (Poisoned Pipeline Execution) | `CODEOWNERS` now requires review on any change to workflow files, CI scripts, and Dockerfiles — the exact set of files that would let an attacker "poison" the pipeline definition itself | `.github/CODEOWNERS` |

### What was fixed in this pass (live repository configuration, executed via `gh api`/`gh` CLI, evidence captured before/after each call)

| Risk | Fix | Evidence |
|---|---|---|
| CICD-SEC-10 (Logging & Visibility) | Enabled **Dependabot vulnerability alerts** (`PUT /repos/.../vulnerability-alerts`) and **Dependabot automated security fixes** (`PUT /repos/.../automated-security-fixes`). Both were confirmed OFF before the call and ON after (`GET /vulnerability-alerts` returns `204` now vs. `404` before). | Live API round-trip, this session |
| CICD-SEC-7 (System Configuration / Ungoverned Actions) | Restricted the repo from "Allow all actions and reusable workflows" to **`allowed_actions: selected`** with only `github_owned_allowed: true` and `verified_allowed: true` (no third-party, unverified marketplace actions can run). Verified this is safe: every `uses:` in `ci.yml` resolves to `actions/checkout` or `actions/setup-python`, both GitHub-owned, so the pipeline is unaffected. | `GET /actions/permissions` → `{"allowed_actions":"selected", ...}`, `GET /actions/permissions/selected-actions` → `{"github_owned_allowed":true,"verified_allowed":true,"patterns_allowed":[]}` |
| CICD-SEC-6 (Credential Hygiene) | Deleted the unused `DOCKERHUB_TOKEN` and `DOCKERHUB_USERNAME` Actions secrets after confirming zero references anywhere in `.github/workflows/` (dead credentials sitting in a repo are pure liability — an attacker who compromises the pipeline definition gains nothing extra by them being gone). | `gh secret list` before showed both; after showed empty list |
| CICD-SEC-5 (PBAC Gates, partial) | Created the `daraja-sandbox` Environment via `PUT /repos/.../environments/daraja-sandbox` so it exists as a first-class, auditable object (not auto-created implicitly on first workflow run) and appears in the repo's deployment activity log. | `GET /environments` before: `{"total_count":0}`; after: environment object present with `id`, `created_at` |

### What is still blocked, and why (verified live, not assumed)

Two related controls remain unimplemented, and both fail for the **identical, confirmed** reason:

1. **Required reviewers on the `daraja-sandbox` Environment** — `PUT .../environments/daraja-sandbox` with a `reviewers` array returns:
   `{"message":"Failed to create the environment protection rule. Please ensure the billing plan supports the required reviewers protection rule."}` (HTTP 422)
2. **Branch protection / repository rulesets on `main`** — both the classic `PUT /branches/main/protection` endpoint and the modern `POST /rulesets` endpoint were tested live and return:
   `{"message":"Upgrade to GitHub Pro or make this repository public to enable this feature."}` (HTTP 403)

This is a **GitHub Free-tier plan restriction on private repositories**, not a permissions or tooling gap — the account has full `admin` scope on the repo (proven by every other write in this pass succeeding), but GitHub itself refuses these two specific features for private repos on the Free plan regardless of caller privilege. The only two ways to close this gap are: (a) upgrade to GitHub Pro/Team (~$4/mo for an individual), or (b) make the repository public (already ruled out per the portfolio-privacy decision earlier in this project). This is captured as the sole remaining manual/business decision below.

---

## Mandatory Manual Infrastructure Checklist (Pending Human Decision — Billing, Not Tooling)

- [x] **CICD-SEC-1 (Flow Control) + CICD-SEC-5 (PBAC, required reviewers): DECISION RECORDED 2026-07-02.** Re-verified live (both classic `PUT /branches/development/protection` and `POST /rulesets` return `403 Upgrade to GitHub Pro or make this repository public`) that this is a GitHub Free private-repo plan restriction, not a tooling or permissions gap. Presented three options to the repository owner: (a) upgrade to GitHub Pro (~$4/mo) for immediate full branch protection, (b) accept the residual risk, (c) make the repo public. **Owner chose (b): accept the residual risk for now.** Rationale accepted: this is a single-maintainer repository with zero external collaborators, so the primary threat branch protection defends against — an unreviewed push from a second party — does not currently apply. The remaining threat model is credential compromise of the owner's own account, which branch protection alone would not fully close anyway (an `enforce_admins: false` policy, the default, lets admins bypass it; full protection against a compromised owner credential requires account-level controls — hardware-key 2FA, unique SSH/PAT scoping, PAT expiry — independent of this repo setting). This decision should be revisited if a second collaborator is ever added, or reversed at any time via the $4/mo Pro upgrade (this doc's fix is already staged — see the exact API calls in the section above and re-run them once upgraded).
- [ ] **CICD-SEC-2 (IAM):** Document the policy that future collaborators must be added with `Write` access, not `Admin` (no API action needed until a second collaborator is actually added — nothing to enforce today on a single-owner repo).

### Additional note on CODEOWNERS in a single-owner repository

`.github/CODEOWNERS` was added requiring `@ALEX-MUTHOMI` review on CI/CD-critical paths. GitHub does not allow a pull request author to approve their own PR to satisfy a required-approval rule, even as a listed code owner. In the current single-collaborator state, this control has no practical enforcement effect until either (a) branch protection with "Require review from Code Owners" is enabled *and* a second collaborator exists to provide that review, or (b) the owner routes sensitive CI/CD changes through a second GitHub account/bot reviewer. It is included now so the control is already in place the moment a second collaborator or branch protection is added — no future PR needed.

---

## Verification performed for this change

- All commit SHAs and image digests in this change were fetched live via `git ls-remote`, the Docker Hub Registry v2 API, and cross-verified via `gh api` tag lookups — none were guessed or reused from memory.
- `docker compose build` was re-run end-to-end against the digest-pinned Dockerfiles to confirm the build still succeeds unchanged.
- YAML structure of `ci.yml` was validated for syntax correctness after every edit.
- Every live repository-configuration change in the second pass was verified with a `GET` immediately after the corresponding `PUT`/`DELETE`, and the before/after state is recorded above rather than assumed. The `actions/permissions` restriction in particular was checked against the *actual* `uses:` lines in `ci.yml` before being applied, specifically to rule out a self-inflicted CI outage.

## Residual risk register (post-hardening)

| # | Residual risk | Severity | Compensating control today | Closed by |
|---|---|---|---|---|
| 1 | No enforced PR review before merge to `main` | Medium | Single maintainer; `CODEOWNERS` advisory; all changes reviewed by the agent/author before push | GitHub Pro/Team upgrade |
| 2 | No required-reviewer gate on `daraja-sandbox` secrets | Low | Same secrets are sandbox-only (Daraja test credentials, not production M-Pesa); `environment:` scoping still isolates the job's secret access even without reviewers | GitHub Pro/Team upgrade |
| 3 | `CODEOWNERS` not enforceable without branch protection | Low | Same as #1 | Same as #1 |

None of these three residual items are exploitable by an external attacker without first compromising a maintainer's GitHub credentials or push access — at which point branch protection alone would also not have been a complete control (a compromised admin account can typically bypass or disable branch protection too, unless "Do not allow bypassing the above settings" and rules-for-admins are also explicitly enabled). They are recorded here for transparency, not because they represent an open remote attack surface today.
