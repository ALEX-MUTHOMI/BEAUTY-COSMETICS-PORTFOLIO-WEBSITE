param(
    [switch]$SkipNewman,
    [switch]$IncludeZapPassive,
    [string]$DockerConfigPath = "",
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$SummaryDir = Join-Path $RepoRoot "reports\ci"
$SummaryPath = Join-Path $SummaryDir "turbo-pass-summary.md"
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
        [string]$Command
    )
    Write-Host ""
    Write-Host "== $Name =="
    if ($VerboseOutput) {
        Write-Host "RUN $Command"
    }
    $stepStart = Get-Date
    # Docker/tooling often writes progress banners to stderr; only exit codes fail the gate.
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        powershell -NoProfile -ExecutionPolicy Bypass -Command $Command
        $exit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prevEap
    }
    if ($null -eq $exit) {
        $exit = 0
    }
    $elapsed = [int]((Get-Date) - $stepStart).TotalSeconds
    Add-Summary "- ${Name}: exit=$exit duration_seconds=$elapsed"
    if ($exit -ne 0) {
        throw "$Name failed with exit code $exit"
    }
}

function Initialize-SafeDockerConfig {
    param(
        [string]$RepoRoot,
        [string]$RequestedPath
    )
    if ($RequestedPath) {
        New-Item -ItemType Directory -Force -Path $RequestedPath | Out-Null
        $env:DOCKER_CONFIG = (Resolve-Path $RequestedPath).Path
        Write-Host "DOCKER_CONFIG_MODE=explicit"
        return
    }
    if ($env:DOCKER_CONFIG) {
        Write-Host "DOCKER_CONFIG_MODE=existing"
        return
    }
    $safePath = Join-Path $RepoRoot "reports\ci\docker-config-empty"
    New-Item -ItemType Directory -Force -Path $safePath | Out-Null
    $env:DOCKER_CONFIG = $safePath
    Write-Host "DOCKER_CONFIG_MODE=temporary_empty_local"
}

Set-Location $RepoRoot
try {
    Initialize-SafeDockerConfig -RepoRoot $RepoRoot -RequestedPath $DockerConfigPath
    Add-Summary "# Turbo Pass Summary"
    Add-Summary ""
    Add-Summary "- started_utc=$($start.ToUniversalTime().ToString('o'))"
    Add-Summary "- skip_newman=$SkipNewman"
    Add-Summary "- include_zap_passive=$IncludeZapPassive"

    Invoke-Checked "Host git hygiene" ".\scripts\ci\git_hygiene_host.ps1"
    Invoke-Checked "Compose config" "docker compose config -q"
    Invoke-Checked "Security scan compose config" "docker compose -f docker-compose.yml -f docker-compose.security-scan.yml config -q"
    Invoke-Checked "Django check" "docker compose exec -T web poetry run python manage.py check"
    Invoke-Checked "Migration drift check" "docker compose exec -T web poetry run python manage.py makemigrations --check --dry-run"
    Invoke-Checked "Pytest collect-only" "docker compose exec -T web poetry run pytest --collect-only -q"
    Invoke-Checked "Security headers and OpenAPI tests" "docker compose exec -T web poetry run pytest tests/security/test_security_headers_openapi.py -q"
    Invoke-Checked "Throttle semantics tests" "docker compose exec -T web poetry run pytest tests/security/test_throttle_semantics.py -q"
    Invoke-Checked "API and security tests" "docker compose exec -T web poetry run pytest tests/api tests/security -q"
    Invoke-Checked "Unit and integration tests" "docker compose exec -T web poetry run pytest tests/unit tests/integration -q"
    if (!$SkipNewman) {
        Invoke-Checked "Docker Newman acceptance" ".\scripts\ci\run_newman_docker.ps1"
    }
    Invoke-Checked "Black check" "docker compose exec -T web poetry run black --check ."
    Invoke-Checked "Isort check" "docker compose exec -T web poetry run isort --check-only ."
    Invoke-Checked "Ruff check" "docker compose exec -T web poetry run ruff check ."
    Invoke-Checked "Flake8 fatal gate" "docker compose exec -T web poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
    Invoke-Checked "Bandit gate" "docker compose exec -T web poetry run bandit -r bookings billing checkout core scripts -ll -ii"
    Invoke-Checked "Secret hygiene filesystem scan" "docker compose exec -T web poetry run python scripts/ci/secret_hygiene.py"
    Invoke-Checked "Docker health" "docker compose ps"
    Invoke-Checked "Worker ping" "docker compose exec -T worker celery -A core inspect ping --timeout=10"
    if ($IncludeZapPassive) {
        Invoke-Checked "ZAP Newman passive gate" ".\scripts\ci\run_security_passive_gate.ps1 -Mode newman"
    }

    $end = Get-Date
    Add-Summary "- finished_utc=$($end.ToUniversalTime().ToString('o'))"
    Add-Summary "- total_duration_seconds=$([int]($end - $start).TotalSeconds)"
    Add-Summary "- result=passed"
    Set-Content -Path $SummaryPath -Value $steps -Encoding UTF8
    Write-Host "TURBO_PASS_SUMMARY=$SummaryPath"
    Write-Host "TURBO_PASS_RESULT=passed"
} catch {
    $end = Get-Date
    Add-Summary "- finished_utc=$($end.ToUniversalTime().ToString('o'))"
    Add-Summary "- total_duration_seconds=$([int]($end - $start).TotalSeconds)"
    Add-Summary "- result=failed"
    Add-Summary "- failure=$($_.Exception.Message)"
    Set-Content -Path $SummaryPath -Value $steps -Encoding UTF8
    Write-Host "TURBO_PASS_SUMMARY=$SummaryPath"
    Write-Host "TURBO_PASS_RESULT=failed"
    throw
}
