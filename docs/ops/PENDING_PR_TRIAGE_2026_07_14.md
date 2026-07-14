# Pending PR triage — 2026-07-14

Open PRs on `ALEX-MUTHOMI/aesthetic-os` at desk-reality promotion time.
All target **`development`**. Default branch is `development`.

## Promotion path (this train)

`development` → `staging` → `main` only after Secure Enterprise CI is green
on the **self-hosted** runner (`runs-on: [self-hosted, linux, aesthetic-os]`).
See [`docs/ops/SELF_HOSTED_RUNNER.md`](SELF_HOSTED_RUNNER.md).
Do **not** auto-merge Dependabot majors into this train.
Do **not** merge while GitHub-hosted minutes are exhausted and no Idle self-hosted runner is online.

## Open Dependabot PRs (deferred)

| # | Title | Risk class | Decision |
|---|-------|------------|----------|
| [17](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/17) | actions/upload-artifact 4→7 | Actions major | Defer — separate CI tooling PR after desk train |
| [16](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/16) | vite-plugin-vue-devtools 8.1.2→8.1.5 | FE devDependency | Defer — low priority |
| [15](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/15) | oxlint 1.60→1.72 | FE lint major-ish | Defer — run oxlint green before merge |
| [14](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/14) | eslint-plugin-oxlint 1.60→1.72 | Pair with #15 | Defer with #15 |
| [13](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/13) | npm-run-all2 8→9 | Major | Defer |
| [12](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/12) | nuxt-security 2.5→2.6 | Security middleware | Defer — needs CSP/header regression |
| [11](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/11) | @vitest/eslint-plugin patch | Low | Defer |
| [10](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/10) | eslint 10.4→10.6 | Lint | Defer |
| [8](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/8) | **nuxt 3.21→4.4** | **Breaking major** | **Block** — not part of desk train |
| [7](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/7) | @playwright/test 1.60→1.61 | Test | Defer |
| [6](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/6) | @vue/test-utils patch | Low | Defer |
| [5](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/5) | **node 22→26 alpine** | **Runtime major** | **Block** — Docker/FE base image |
| [4](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/4) | **python 3.13→3.14 slim** | **Runtime major** | **Block** — Poetry/Django matrix |
| [3](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/3) | actions/setup-python 5→6 | Actions major | Defer |
| [2](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/2) | actions/checkout 4→7 | Actions major | Defer |

## Secure merge rules

1. Never merge Dependabot runtime majors (#4, #5, #8) without a dedicated upgrade plan + turbo_pass + staging soak.
2. Desk / auth / security product PRs merge first; dependency PRs after green baseline.
3. Prefer squash-merge for Dependabot; merge commits OK for long-lived product branches if history already linear on `development`.
4. No `--force` to `staging`/`main`; no `--no-verify`.
