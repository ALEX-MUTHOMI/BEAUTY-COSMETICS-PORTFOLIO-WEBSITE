# Self-hosted GitHub Actions runner (AestheticOS)

Secure Enterprise CI ([`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)) runs on:

```yaml
runs-on: [self-hosted, linux, aesthetic-os]
```

GitHub still owns the control plane (PR checks, logs, concurrency). **Compute** runs on your machine so private-repo hosted minutes are not required.

## Labels (required)

| Label | Purpose |
|-------|---------|
| `self-hosted` | Built-in self-hosted class |
| `linux` | Linux/`bash` job scripts |
| `aesthetic-os` | Repo-specific pin (avoid stealing unrelated org runners) |

## Path A — Docker Desktop runner (recommended on this Windows PC)

Docker Desktop already runs a Linux engine. Start a long-lived Linux runner container that mounts the Docker socket:

```powershell
.\scripts\ci\start_self_hosted_runner_docker.ps1
```

Checkout stays on the **container Linux filesystem** (do not bind-mount `C:\...` as `RUNNER_WORKDIR` — NTFS makes `actions/setup-python` crawl). Base `docker-compose.yml` has no `.:/app` bind; local desk adds that via `docker-compose.windows.yml`. CI builds images and runs from the bake, so the host daemon does not need the runner checkout path.

Checks:

```powershell
docker ps --filter name=aesthetic-os-gha-runner
gh api repos/ALEX-MUTHOMI/aesthetic-os/actions/runners --jq ".runners[]|{name,status,labels:[.labels[].name]}"
```

Expect `status: online` (Idle when no jobs).

Stop:

```powershell
docker rm -f aesthetic-os-gha-runner
```

## Path B — WSL2 Ubuntu + native runner

1. Install Ubuntu (`wsl --install -d Ubuntu`) and finish first-boot user creation.
2. Docker Desktop → Settings → Resources → WSL integration → enable **Ubuntu**.
3. In Ubuntu:

```bash
docker version   # must work
export RUNNER_TOKEN="$(gh api -X POST repos/ALEX-MUTHOMI/aesthetic-os/actions/runners/registration-token --jq .token)"
# or mint token on Windows and paste once
bash scripts/ci/install_self_hosted_runner.sh
cd ~/actions-runner && ./run.sh
# service: sudo ./svc.sh install && sudo ./svc.sh start
```

### PowerShell 7 on Linux (ZAP job)

`zap-passive-newman` calls `pwsh`. Install PowerShell 7 in the runner environment, or that job will fail closed.

## Job hygiene

Self-hosted runners reuse disk **and** the same Docker engine as the local desk stack. Compose uses fixed `container_name` values (`aesthetic_os_redis`, etc.), so CI and a running desk cannot share those names.

CI jobs call `bash scripts/ci/compose_reset.sh` before `up` and `if: always()` after. That script downs the Compose project **and** force-removes the fixed container names / shared network. Expect the desk stack to stop while CI runs; bring it back afterward:

```powershell
$env:COMPOSE_FILE='docker-compose.yml;docker-compose.windows.yml'
docker compose up -d
```

Manual weekly (host):

```powershell
docker system prune -f
```

Do **not** auto `prune -af` every job (slow + surprises).

## Parallelism

One runner ⇒ jobs **serialize** (T2 units queue). Acceptable for unblock. Scale later with a second container/process using the same labels.

## Security

- Never commit registration tokens (expire ~1h).
- Prefer **repo-scoped** runners while evaluating.
- Treat the host as high-trust (secrets can land in job env).
- Private repo / same-repo PRs only — do not expose self-hosted runners to untrusted forks.

## Verify minutes are not required

After the runner is Idle:

```powershell
gh workflow run "Secure Enterprise CI Pipeline" --ref development
gh run watch --exit-status
```

`validate` must show a real `runner_name` (not a 2s empty-runner failure from hosted-minute exhaustion).

## Promotion gate

Merge [PR #19](https://github.com/ALEX-MUTHOMI/aesthetic-os/pull/19) (`development` → `staging`) only when Secure Enterprise is **green on self-hosted**. Then open `staging` → `main`.
