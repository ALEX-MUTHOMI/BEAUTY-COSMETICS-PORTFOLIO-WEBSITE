<#
.SYNOPSIS
  Docker-mirrored lint heal before push — Black / isort / ruff fix + secret_hygiene check-only.

.DESCRIPTION
  Runs the same Poetry toolchain as CI inside the `web` container so host/venv
  drift cannot invent a green local format that CI then rejects.

  Non-goals (explicit):
  - Does NOT mute or auto-suppress secret_hygiene hits (fail-closed).
  - Does NOT bump Poetry / Black / Ruff majors — pins stay in pyproject.toml.
  - Does NOT pass --no-verify or skip hooks.

.EXAMPLE
  .\scripts\ci\preflight_heal.ps1
#>
param(
    [switch]$SkipSecretHygiene,
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$SummaryDir = Join-Path $RepoRoot "reports\ci"
$SummaryPath = Join-Path $SummaryDir "preflight-heal-summary.md"
New-Item -ItemType Directory -Force -Path $SummaryDir | Out-Null

$steps = New-Object System.Collections.Generic.List[string]
$start = Get-Date

function Add-Summary {
    param([string]$Line)
    $script:steps.Add($Line)
}

function Invoke-Checked {
    param(
        [string]$Name,
        [scriptblock]$Action
    )
    Write-Host ""
    Write-Host "== $Name =="
    $stepStart = Get-Date
    & $Action
    $exit = $LASTEXITCODE
    if ($null -eq $exit) { $exit = 0 }
    $elapsed = [int]((Get-Date) - $stepStart).TotalSeconds
    Add-Summary "- ${Name}: exit=$exit duration_seconds=$elapsed"
    if ($exit -ne 0) {
        throw "$Name failed with exit code $exit"
    }
}

Set-Location $RepoRoot
if (-not $env:COMPOSE_FILE) {
    # Windows bind-mount Poetry mask when present; never used by GitHub Actions.
    $windowsOverride = Join-Path $RepoRoot "docker-compose.windows.yml"
    if (Test-Path $windowsOverride) {
        $env:COMPOSE_FILE = "docker-compose.yml;docker-compose.windows.yml"
    }
}

try {
    Add-Summary "# Preflight Heal Summary"
    Add-Summary ""
    Add-Summary "Started: $($start.ToString('o'))"
    Add-Summary ""

    Invoke-Checked "compose ps (web must be up)" {
        & docker compose ps web
        if ($LASTEXITCODE -ne 0) { return }
        $webState = @(& docker compose ps --status running --services 2>$null)
        if ($webState -notcontains "web") {
            throw "web service is not running. Start stack first: docker compose up -d"
        }
    }

    Invoke-Checked "black ." {
        if ($VerboseOutput) { Write-Host "docker compose exec -T web poetry run black ." }
        & docker compose exec -T web poetry run black .
    }

    Invoke-Checked "isort ." {
        if ($VerboseOutput) { Write-Host "docker compose exec -T web poetry run isort ." }
        & docker compose exec -T web poetry run isort .
    }

    Invoke-Checked "ruff check --fix ." {
        if ($VerboseOutput) { Write-Host "docker compose exec -T web poetry run ruff check --fix ." }
        & docker compose exec -T web poetry run ruff check --fix .
    }

    if (-not $SkipSecretHygiene) {
        Invoke-Checked "secret_hygiene (check-only, fail-closed)" {
            if ($VerboseOutput) { Write-Host "docker compose exec -T web poetry run python scripts/ci/secret_hygiene.py" }
            & docker compose exec -T web poetry run python scripts/ci/secret_hygiene.py
        }
    }
    else {
        Add-Summary "- secret_hygiene: SKIPPED (explicit -SkipSecretHygiene)"
        Write-Host "WARNING: secret_hygiene skipped - do not push without a full heal."
    }

    $elapsedTotal = [int]((Get-Date) - $start).TotalSeconds
    Add-Summary ""
    Add-Summary "Result: PASS"
    Add-Summary "Total duration_seconds=$elapsedTotal"
    Add-Summary ""
    Add-Summary "Next (optional): .\scripts\ci\local_ci_mirror.ps1"
    $steps | Set-Content -Path $SummaryPath -Encoding utf8
    Write-Host ""
    Write-Host "Preflight heal PASS (${elapsedTotal}s). Summary: $SummaryPath"
}
catch {
    $elapsedTotal = [int]((Get-Date) - $start).TotalSeconds
    Add-Summary ""
    Add-Summary "Result: FAIL"
    Add-Summary "Error: $($_.Exception.Message)"
    Add-Summary "Total duration_seconds=$elapsedTotal"
    $steps | Set-Content -Path $SummaryPath -Encoding utf8
    Write-Host ""
    Write-Host "Preflight heal FAIL. Summary: $SummaryPath"
    throw
}
