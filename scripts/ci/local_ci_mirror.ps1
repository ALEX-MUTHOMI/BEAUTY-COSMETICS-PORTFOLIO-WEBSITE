<#
.SYNOPSIS
  Gate 1 local CI mirror - same lint ladder as GitHub Actions lint-security + frontend-test
  (without full pytest partitions / Newman). Fail here before push so CI is not a spell-checker.

.DESCRIPTION
  Default (fast push gate):
    poetry: black --check, isort --check-only, ruff, flake8 fatal, secret_hygiene
    frontend: lint:oxlint, type-check

  Optional:
    -IncludeFrontendTest   npm run test (Vitest)
    -IncludeFrontendBuild  npm run build
    -IncludeBandit         bandit (matches CI lint-security; slower)

  Rule: first push of a feature should be the green one. Lint-only follow-ups are process debt.
#>
param(
    [switch]$IncludeFrontendTest,
    [switch]$IncludeFrontendBuild,
    [switch]$IncludeBandit,
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$SummaryDir = Join-Path $RepoRoot "reports\ci"
$SummaryPath = Join-Path $SummaryDir "local-ci-mirror-summary.md"
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
try {
    Add-Summary "# Local CI Mirror Summary"
    Add-Summary ""
    Add-Summary "- started_utc=$($start.ToUniversalTime().ToString('o'))"
    Add-Summary "- include_frontend_test=$IncludeFrontendTest"
    Add-Summary "- include_frontend_build=$IncludeFrontendBuild"
    Add-Summary "- include_bandit=$IncludeBandit"
    Add-Summary "- note=CI_green_certifies_tree_not_production_readiness"

    if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
        throw "poetry not found on PATH. Install Poetry or run from an environment that has it."
    }
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "npm not found on PATH."
    }

    Invoke-Checked "Black check" { poetry run black --check . }
    Invoke-Checked "Isort check" { poetry run isort --check-only . }
    Invoke-Checked "Ruff check" { poetry run ruff check . }
    Invoke-Checked "Flake8 fatal gate" {
        poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    }
    if ($IncludeBandit) {
        Invoke-Checked "Bandit gate" {
            poetry run bandit -r . -x tests,.venv,.cache,frontend/node_modules -ll -ii
        }
    }
    Invoke-Checked "Secret hygiene" { poetry run python scripts/ci/secret_hygiene.py }

    Invoke-Checked "Frontend oxlint" {
        npm --prefix frontend run lint:oxlint
    }
    Invoke-Checked "Frontend type-check" {
        npm --prefix frontend run type-check
    }
    if ($IncludeFrontendTest) {
        Invoke-Checked "Frontend Vitest" { npm --prefix frontend run test }
    }
    if ($IncludeFrontendBuild) {
        Invoke-Checked "Frontend build" { npm --prefix frontend run build }
    }

    $end = Get-Date
    Add-Summary "- finished_utc=$($end.ToUniversalTime().ToString('o'))"
    Add-Summary "- total_duration_seconds=$([int]($end - $start).TotalSeconds)"
    Add-Summary "- result=passed"
    Set-Content -Path $SummaryPath -Value $steps -Encoding UTF8
    Write-Host ""
    Write-Host "LOCAL_CI_MIRROR_SUMMARY=$SummaryPath"
    Write-Host "LOCAL_CI_MIRROR_RESULT=passed"
    Write-Host "Reminder: green mirror/CI certifies this tree - not production readiness (Daraja staging, Sentry DSN, Beat-in-deploy, backups)."
} catch {
    $end = Get-Date
    Add-Summary "- finished_utc=$($end.ToUniversalTime().ToString('o'))"
    Add-Summary "- total_duration_seconds=$([int]($end - $start).TotalSeconds)"
    Add-Summary "- result=failed"
    Add-Summary "- failure=$($_.Exception.Message)"
    Set-Content -Path $SummaryPath -Value $steps -Encoding UTF8
    Write-Host "LOCAL_CI_MIRROR_SUMMARY=$SummaryPath"
    Write-Host "LOCAL_CI_MIRROR_RESULT=failed"
    throw
}
