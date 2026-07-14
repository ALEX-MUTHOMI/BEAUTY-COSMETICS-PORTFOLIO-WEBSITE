<#
.SYNOPSIS
  Start a Linux GitHub Actions self-hosted runner in Docker (Docker Desktop / Linux engine).

.DESCRIPTION
  Uses labels self-hosted,linux,aesthetic-os so Secure Enterprise CI (ci.yml) can schedule
  without GitHub-hosted minutes. Mounts the host Docker socket so compose jobs work.

  Never commit RUNNER_TOKEN. Token expires ~1 hour after creation.
#>
param(
    [string]$RunnerName = "aesthetic-os-docker",
    [string]$Image = "myoung34/github-runner:ubuntu-jammy",
    [string]$ContainerName = "aesthetic-os-gha-runner"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "gh CLI is required to mint a registration token."
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "docker is required."
}

Write-Host "Minting registration token (ephemeral)..."
$tokenJson = gh api -X POST repos/ALEX-MUTHOMI/aesthetic-os/actions/runners/registration-token | ConvertFrom-Json
$token = $tokenJson.token
if (-not $token) { throw "Failed to obtain registration token." }

$existing = docker ps -a --filter "name=^/${ContainerName}$" --format "{{.Names}}"
if ($existing) {
    Write-Host "Removing existing container $ContainerName..."
    docker rm -f $ContainerName | Out-Null
}

Write-Host "Starting runner container $ContainerName (labels: self-hosted,linux,aesthetic-os)..."
docker run -d --restart unless-stopped `
  --name $ContainerName `
  -e REPO_URL="https://github.com/ALEX-MUTHOMI/aesthetic-os" `
  -e RUNNER_NAME="$RunnerName" `
  -e RUNNER_TOKEN="$token" `
  -e RUNNER_LABELS="self-hosted,linux,aesthetic-os" `
  -e RUNNER_WORKDIR="/tmp/runner-work" `
  -e DISABLE_AUTO_UPDATE="true" `
  -v /var/run/docker.sock:/var/run/docker.sock `
  -v "${ContainerName}-work:/tmp/runner-work" `
  $Image | Out-Null

Start-Sleep -Seconds 8
docker ps --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
Write-Host ""
Write-Host "Verify Idle in GitHub: gh api repos/ALEX-MUTHOMI/aesthetic-os/actions/runners --jq .runners"
Write-Host "Logs: docker logs -f $ContainerName"
