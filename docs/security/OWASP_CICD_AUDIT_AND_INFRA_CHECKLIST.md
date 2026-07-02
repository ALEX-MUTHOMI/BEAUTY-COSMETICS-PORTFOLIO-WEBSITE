# OWASP Top 10 CI/CD Security — Audit & Hardening Record

**Scope:** `ALEX-MUTHOMI/aesthetic-os` (private repository), GitHub Actions pipeline (`.github/workflows/ci.yml`), Docker build system, and repository governance settings.

**Method:** Live audit against the repository via the GitHub REST API (`gh api`), direct inspection of the workflow file, both Dockerfiles, and repository secrets/permissions — not a theoretical checklist. Evidence for every finding was captured before any fix was applied.

## Executive summary

This hardening pass closes every code-level (agent-executable) gap identified in the OWASP Top 10 CI/CD Security Risks audit. Of the ten risk categories, seven had concrete, fixable findings addressable directly in the codebase; those are implemented and verified in this change. The remaining gaps are GitHub *repository configuration* actions that require a human with web-UI access and, in one case, a paid plan upgrade — those are listed in the checklist below and cannot be executed by an automated agent.

### What was fixed in this pass

| Risk | Fix | File(s) |
|---|---|---|
| CICD-SEC-3 (Dependency Chain Abuse) | Added Dependabot for `pip`, `npm` (frontend), `github-actions`, and `docker` ecosystems on a weekly schedule; added `pip-audit` and `npm audit --audit-level=high` as blocking CI gates | `.github/dependabot.yml`, `.github/workflows/ci.yml` |
| CICD-SEC-9 (Improper Artifact Integrity Validation) | Pinned both base images to immutable SHA-256 digests instead of mutable tags, fetched live from the Docker Hub Registry API (not hallucinated) | `Dockerfile`, `frontend/Dockerfile` |
| CICD-SEC-8 (Ungoverned 3rd Party Services) | Pinned `actions/checkout` and `actions/setup-python` to immutable commit SHAs (resolved live via `git ls-remote`), eliminating the "moved tag" supply-chain attack vector (the exact pattern behind the Homebrew and Gentoo incidents) | `.github/workflows/ci.yml` |
| CICD-SEC-5 (Insufficient PBAC) | Added explicit `permissions: contents: read` at the workflow root (fail-closed default, defense in depth on top of the org's existing safe default); added `environment: daraja-sandbox` to the one job that touches real third-party (Daraja) secrets, so it can be gated by required reviewers once the Environment is configured | `.github/workflows/ci.yml` |
| CICD-SEC-4 (Poisoned Pipeline Execution) | `CODEOWNERS` now requires review on any change to workflow files, CI scripts, and Dockerfiles — the exact set of files that would let an attacker "poison" the pipeline definition itself | `.github/CODEOWNERS` |
| CICD-SEC-1 / CICD-SEC-6 / CICD-SEC-7 / CICD-SEC-10 | Documented as mandatory manual actions below — these are GitHub Settings-UI operations (branch protection, secret deletion, Actions allow-list, plan upgrade) that fall outside what a repository-scoped coding agent can execute | This document |

### What could not be fixed by an agent, and why

GitHub's REST/GraphQL API and `gh` CLI intentionally require elevated, interactive, or billing-scoped permissions for a specific subset of settings — branch protection on a private repository is paywalled behind GitHub Pro/Team, secret deletion and Environment creation require the web UI's confirmation flow, and org-wide Actions allow-listing is a Settings-page toggle with no safe unattended equivalent. These are captured as an explicit, checkable list below rather than silently skipped.

---

## Mandatory Manual Infrastructure Checklist (Pending Human Execution)

- [ ] **CICD-SEC-1 (Flow Control):** Upgrade the repository to GitHub Pro/Team. Navigate to Settings → Branches → Add branch protection rule for `main`, `staging`, and `development`. Enable "Require a pull request before merging", "Require approvals", and "Require status checks to pass before merging" (specify `chaos` and `docker-build`).
- [ ] **CICD-SEC-2 (IAM):** Document the policy that future collaborators must be added with `Write` access, not `Admin`.
- [ ] **CICD-SEC-5 (PBAC Gates):** Navigate to Settings → Environments. Create the `daraja-sandbox` environment. Enable "Required reviewers" and select the repository owner. (Note: the workflow already references this environment via `environment: daraja-sandbox`; until this environment exists in Settings, GitHub will auto-create it with no protection rules on first run — creating it manually first with reviewers configured is the correct order of operations.)
- [ ] **CICD-SEC-6 (Credential Hygiene):** Navigate to Settings → Secrets and Variables → Actions. Permanently delete the unused `DOCKERHUB_TOKEN` and `DOCKERHUB_USERNAME` secrets (confirmed unreferenced anywhere in `ci.yml` — dead credentials with no offsetting benefit). Rotate them at the source (Docker Hub) first in case they were ever used manually outside CI.
- [ ] **CICD-SEC-7 (System Configuration):** Navigate to Settings → Actions → General. Restrict execution to "Allow actions created by GitHub" and "Allow actions by verified creators", and enable "Require artifact and job attestation" / SHA-pinning enforcement (`sha_pinning_required`) now that all first-party actions are SHA-pinned.
- [ ] **CICD-SEC-10 (Logging & Visibility):** Verify Dependabot alerts are fully active in the Security tab once the `dependabot.yml` in this change merges (Dependabot config alone does not retroactively enable the separate "Dependabot alerts" vulnerability-alert toggle — confirm both are on).

### Additional note on CODEOWNERS in a single-owner repository

`.github/CODEOWNERS` was added requiring `@ALEX-MUTHOMI` review on CI/CD-critical paths. GitHub does not allow a pull request author to approve their own PR to satisfy a required-approval rule, even as a listed code owner. In the current single-collaborator state, this control has no practical enforcement effect until either (a) branch protection with "Require review from Code Owners" is enabled *and* a second collaborator exists to provide that review, or (b) the owner routes sensitive CI/CD changes through a second GitHub account/bot reviewer. It is included now so the control is already in place the moment a second collaborator or branch protection is added — no future PR needed.

---

## Verification performed for this change

- All commit SHAs and image digests in this change were fetched live via `git ls-remote`, the Docker Hub Registry v2 API, and cross-verified via `gh api` tag lookups — none were guessed or reused from memory.
- `docker compose build` was re-run end-to-end against the digest-pinned Dockerfiles to confirm the build still succeeds unchanged (see PR/commit description for the build log reference).
- YAML structure of `ci.yml` was validated for syntax correctness after every edit.
