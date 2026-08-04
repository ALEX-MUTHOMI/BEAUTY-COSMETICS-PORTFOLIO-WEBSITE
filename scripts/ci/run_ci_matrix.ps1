param(
    [switch]$IncludePerformance,
    [switch]$IncludePassiveSecurity
)

$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "turbo_pass.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Turbo Pass failed."
}

docker compose exec -T web poetry run pytest bookings/tests -q
if ($LASTEXITCODE -ne 0) {
    throw "bookings partition failed."
}
docker compose exec -T web poetry run pytest checkout/tests billing/tests -q
if ($LASTEXITCODE -ne 0) {
    throw "checkout/billing partition failed."
}

if ($IncludePerformance) {
    & (Join-Path $PSScriptRoot "run_performance_gate.ps1") -Mode standard
    if ($LASTEXITCODE -ne 0) {
        throw "performance gate failed."
    }
}

if ($IncludePassiveSecurity) {
    & (Join-Path $PSScriptRoot "run_security_passive_gate.ps1") -Mode all-passive
    if ($LASTEXITCODE -ne 0) {
        throw "passive security gate failed."
    }
}

