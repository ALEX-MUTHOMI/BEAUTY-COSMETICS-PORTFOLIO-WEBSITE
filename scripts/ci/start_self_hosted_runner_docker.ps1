<#
.SYNOPSIS
  Start a Linux GitHub Actions self-hosted runner in Docker (Docker Desktop / Linux engine).

.DESCRIPTION
  Uses labels self-hosted,linux,aesthetic-os so Secure Enterprise CI (ci.yml) can schedule
  without GitHub-hosted minutes. Mounts the host Docker socket so compose jobs work.

  WORKDIR is bind-mounted at the SAME path on host and in-container so compose
  volume mounts like .:/app resolve on the Docker Desktop host (DinD-socket pattern).

  Never commit RUNNER_TOKEN. Token expires ~1 hour after creation.
#>
param(
    [string]$RunnerName = "aesthetic-os-docker",
    [string]$Image = "myoung34/github-runner:ubuntu-jammy",
    [string]$ContainerName = "aesthetic-os-gha-runner",
    # Linux-style path Docker Desktop accepts for Windows bind mounts
    [string]$WorkDirLinux = "/c/Users/PC/aesthetic-os-gha-work"
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

# Windows host directory corresponding to /c/Users/PC/...
$workWin = "C:\Users\PC\aesthetic-os-gha-work"
New-Item -ItemType Directory -Force -Path $workWin | Out-Null

Write-Host "Minting registration token (ephemeral)..."
$tokenJson = gh api -X POST repos/ALEX-MUTHOMI/aesthetic-os/actions/runners/registration-token | ConvertFrom-Json
$token = $tokenJson.token
if (-not $token) { throw "Failed to obtain registration token." }

$existing = docker ps -a --filter "name=^/${ContainerName}$" --format "{{.Names}}"
if ($existing) {
    Write-Host "Removing existing container $ContainerName..."
    docker rm -f $ContainerName | Out-Null
}

Write-Host "Starting runner container $ContainerName"
Write-Host "  labels: self-hosted,linux,aesthetic-os"
Write-Host "  workdir: $WorkDirLinux  (host: $workWin)"

docker run -d --restart unless-stopped `
  --name $ContainerName `
  -e REPO_URL="https://github.com/ALEX-MUTHOMI/aesthetic-os" `
  -e RUNNER_NAME="$RunnerName" `
  -e RUNNER_TOKEN="$token" `
  -e RUNNER_LABELS="self-hosted,linux,aesthetic-os" `
  -e RUNNER_WORKDIR="$WorkDirLinux" `
  -e DISABLE_AUTO_UPDATE="true" `
  -v /var/run/docker.sock:/var/run/docker.sock `
  -v "${WorkDirLinux}:${WorkDirLinux}" `
  $Image | Out-Null

Start-Sleep -Seconds 10
docker ps --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
Write-Host ""
Write-Host "Verify Idle in GitHub: gh api repos/ALEX-MUTHOMI/aesthetic-os/actions/runners --jq .runners"
Write-Host "Logs: docker logs -f $ContainerName"
